# Copyright (c) 2026 iiPython

from pathlib import Path

from waffle.asm.token import ParseState, parse_file

target_file: Path | None = None

def set_file(file: Path) -> None:
    global target_file
    target_file = file

class AssemblerError(Exception):
    def __init__(self, message: str, index: int, argument_offset: int | None = None, argument: str | None = None) -> None:
        if target_file is None:
            raise ValueError("Cannot raise an AssemblerError without calling set_file() first!")

        self.file_lines = target_file.read_text().splitlines()
        self.argument_offset, self.argument = argument_offset, argument

        # Track line
        target_line: int | None = None

        def track_state(state: ParseState, real_index: int) -> None:
            nonlocal target_line
            if state.index == index:
                target_line = real_index + 1

        parse_file(target_file, track_state)

        # Confirm line exists
        if target_line is None:
            raise RuntimeError("Could not find a line with the given code index!")

        lower_line = target_line - 1
        upper_line = target_line + 2
        if upper_line > len(self.file_lines):
            upper_line -= 1
            lower_line -= 1

        # Begin printing
        print(f"\033[1;31mAssembly Fault\033[0m ({type(self).__name__}) in \033[4;33m{target_file}:{target_line + 1}\033[0m\n")
        for line in range(lower_line, upper_line):
            self.print_code_line(line, target_line)

        print(f"\n\033[1;4;31mE:\033[22m {message}\033[0m")
        exit(1)

    def print_code_line(self, line: int, target: int) -> None:
        print(f" \033[{90 if line != target else 31}m{line + 1:03}  ", end = "")
        for index, character in enumerate(self.file_lines[line].strip().replace(", ", " ")):

            # Set underline mode on requested argument
            if self.argument_offset is not None and self.argument is not None and line == target:
                if index == self.argument_offset:
                    print("\033[4m", end = "")

                if index == self.argument_offset + len(self.argument):
                    print("\033[24m", end = "")

            print(character, end = "")

        print("\033[0m")
