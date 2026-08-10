# Copyright (c) 2026 iiPython

import re
import typing
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParseState:
    index:   int
    lines:   list[list[str]]
    labels:  dict[str, int]
    label:   str | None
    preload: dict[str, bytes]

@dataclass
class LineState:
    buffer: str
    chunks: list[str]
    nested: bool

class ParseException(Exception):
    pass

RE_LABEL = re.compile(r"^(\w+):$")
RE_PRELOAD_LINE = re.compile(r"^\s*(\w+):\s+\.(\w+)\s+(\"(?:[^\"\\]|\\.)*\"|0x[0-9a-fA-F]+|\d+)")

def parse_line(line: str) -> list[str]:
    state = LineState("", [], False)

    def push() -> None:
        if not state.buffer:
            return

        if not state.chunks:
            state.buffer = state.buffer.upper()  # Fully uppercase instruction

        if state.buffer.endswith(","):
            if len(state.chunks) != 1:
                raise ParseException("Found a comma in an incorrect location!")

            state.buffer = state.buffer[:-1]

        state.chunks.append(state.buffer)
        state.buffer = ""

        if len(state.chunks) > 3:
            raise ParseException("Too many arguments present for line!")

    for character in line:
        if character == ";" and not state.nested:
            break

        if character == " " and not state.nested:
            push()
            continue

        if character == "'":
            state.nested = not state.nested

        state.buffer += character

    if state.buffer:
        push()

    return state.chunks

def parse_file(file: Path, callback: typing.Callable | None = None) -> ParseState:
    state = ParseState(0, [], {}, None, {})
    for index, line in enumerate(file.read_text().splitlines()):
        line = line.strip()

        # Handle skipping
        if not line.strip() or line.startswith(";"):
            continue

        # Labels
        if (label_match := RE_LABEL.match(line)) is not None:
            label_name = label_match.group(1)
            state.label = label_name

            # Handle non-preload
            if label_name != "preload":
                state.labels[label_name] = state.index

            continue

        # Preload
        preload_match = RE_PRELOAD_LINE.match(line)
        if preload_match is not None:
            if state.label != "preload":
                raise ParseException("Found a preload line outside of the preload section!")

            key, type, value = preload_match.groups()
            match type:
                case "byte" | "short" | "word":
                    value = int(value, 16 if value.startswith("0x") else 10)
                    if type == "byte" and value > 255:
                        raise ParseException("Cannot store a byte with a value above 255!")

                    value = value.to_bytes(1 if type == "byte" else 2)

                case "ascii" | "string" | "asciz":
                    value = value[1:-1]
                    for index, character in enumerate(value):
                        if character == "\"" and (index and value[index - 1] != "\\" or not index):
                            raise ParseException("Found a non-escaped double quote inside of a preload string!")

                    value = value.encode("utf-8").decode("unicode-escape").encode("utf-8")
                    if type != "ascii":
                        value += b"\0"

                case _:
                    raise ParseException("Found a preload line with an invalid format!")

            if not isinstance(value, bytes):
                raise ParseException("Exception occured while interpreting preload line!")

            state.preload[key] = value
            continue

        if state.label == "preload" and preload_match is None:
            raise ParseException("Found a non-preload line inside of the preload section!")

        # Normal lines
        state.lines.append(parse_line(line))
        state.index += 1

        if callback is not None:
            callback(state, index)

    return state
