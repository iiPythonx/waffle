# Copyright (c) 2026 iiPython

from waffle.asm import exception
from waffle.asm.token import ParseState
from waffle.isa import INSTRUCTIONS, REGISTERS, Addresses

REGISTERS_BY_NAME = {reg.name: reg for reg in REGISTERS}
INSTRUCTS_BY_VERB = {v.opcode: (k, v) for k, v in INSTRUCTIONS.items()}

class Assembler:
    def __init__(self, state: ParseState, driver_mapping: dict[str, int] | None = None) -> None:
        self.data_block = bytearray([0] * Addresses.DATA.size)
        self.code_block = bytearray([0] * Addresses.CODE.size)

        self.state = state
        self.driver_mapping: dict[str, int] = driver_mapping or {}

        self.line_index: int = 0
        self.code_offset: int = 0
        self.subroutines: dict[str, list[int]] = {}

        self.string_mapping: dict[str, int] = {}
        if state.preload:
            self.string_mapping = self.write_preload(state.preload)

    def write_code(self, data: bytes) -> None:
        data_size: int = len(data)
        self.code_block[self.code_offset:self.code_offset + data_size] = data
        self.code_offset += data_size

    def write_preload(self, preload: dict[str, bytes]) -> dict[str, int]:
        mapping, offset = {}, 0
        for key, value in preload.items():
            mapping[key] = offset + Addresses.DATA.start

            # Encode value and store in block
            self.data_block[offset:offset + len(value)] = value

            # Increment offset for next value
            offset += len(value)

        return mapping

    def parse_argument(self, offset: int, argument: str, size: int) -> int:
        if (a := argument.upper()) in REGISTERS_BY_NAME:
            return REGISTERS_BY_NAME[a].id

        if size == 1:
            raise exception.AssemblerError(f"Invalid value provided for a register: '{argument}'!", self.line_index, offset, argument)

        if argument.startswith("0x"):
            return int(argument, 16)

        if argument.startswith("&"):
            if (argument := argument[1:]) not in self.string_mapping:
                raise exception.AssemblerError(f"Reference to an unknown string: '{argument}'!", self.line_index, offset, argument)

            return self.string_mapping[argument]

        if len(argument) == 3 and argument[0] == "'" and argument[-1] == "'":
            return ord(argument[1:-1])

        if argument in self.state.labels:
            self.subroutines.setdefault(argument, [])
            self.subroutines[argument].append(self.code_offset)
            return 0  # Will be replaced after initial building

        if (binding := argument.upper().removeprefix("D_")) in self.driver_mapping:
            return self.driver_mapping[binding]

        try:
            value = int(argument)
            if value < 0 or value > 0xFFFF:
                raise exception.AssemblerError(
                    "Integer either negative or too large to store!",
                    self.line_index, offset, argument
                )

            return value

        except ValueError:
            raise exception.AssemblerError(
                f"Argument matches no known types and is thus invalid: '{argument}'!",
                self.line_index, offset, argument
            )

    def assemble(self, zero_jump: bool = False) -> bytearray:
        if zero_jump:
            self.write_code(INSTRUCTS_BY_VERB["JMP"][0].to_bytes() + b"\0\0")

        subroutine_addresses: dict[str, int] = {}
        for index, (instruction, *arguments) in enumerate(self.state.lines):
            self.line_index = index

            # Attempt to find matching label
            label_match = next(filter(lambda x: self.state.labels[x] == index, self.state.labels), None)
            if label_match:
                subroutine_addresses[label_match] = self.code_offset

            # Push instruction bytecode
            if instruction not in INSTRUCTS_BY_VERB:
                raise exception.AssemblerError("Invalid instruction referenced!", self.line_index)

            bytecode, instruction = INSTRUCTS_BY_VERB[instruction]
            self.write_code(bytecode.to_bytes())

            # Argument mapping
            argument_offset = len(instruction.opcode) + 1
            for index, argument in enumerate(instruction.args):
                self.write_code(self.parse_argument(argument_offset + index, arguments[index], argument.size).to_bytes(argument.size))
                argument_offset += len(arguments[index])

        for subroutine, addresses in self.subroutines.items():
            for address in addresses:
                self.code_block[address:address + 2] = subroutine_addresses[subroutine].to_bytes(2)

        if terminate := subroutine_addresses.get("terminate"):
            self.data_block[0x0700:0x0702] = terminate.to_bytes(2)

        first_subroutine = min(subroutine_addresses, key = lambda k: subroutine_addresses[k])
        if main := subroutine_addresses.get("main"):
            if zero_jump:
                self.code_block[1:3] = main.to_bytes(2)

            elif first_subroutine != "main":
                print(f"\033[33;1mWarning!\033[0m Zero-jump is \033[31mnot enabled\033[0m and the first subroutine is \033[34m{first_subroutine}\033[0m!")

        return self.code_block + self.data_block
