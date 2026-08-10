# Copyright (c) 2026 iiPython

import io
import sys
import time
from itertools import batched

from waffle.isa import INSTRUCTIONS, REGISTERS, Addresses

REGISTERS_BY_NAME = {reg.name: reg for reg in REGISTERS}

class Debugger:
    def __init__(self, memory: bytearray) -> None:
        self.memory = memory

        # Handle autostepping
        self.steps = 0

        # Disable time.sleep (since our stepping is slow anyway)
        time.sleep = lambda _: None

        # Handle stdout redirection
        self.stdout = sys.stdout
        self.stdout_store = io.StringIO()

    def init(self) -> None:
        self.show_interface()
        sys.stdout = self.stdout_store

    def write(self, text: str = "", **kwargs) -> None:
        print(text, flush = True, **kwargs)

    def print_label(self, text: str) -> None:
        self.write(f"\033[44m {text:<20}\033[0m\n\n", end = "")

    def print_instructions(self) -> None:
        self.print_label("INSTRUCTIONS")

        # Read current line
        offset = REGISTERS_BY_NAME["LC"].address
        offset = Addresses.CODE.start + int.from_bytes(self.memory[offset:offset + 2])

        # Fetch instruction
        for _ in range(6):
            instruction = INSTRUCTIONS.get(self.memory[offset], None)
            if instruction is None:
                self.write(f" \033[31m0x{offset:04x} ???\033[0m")
                continue

            self.write(f"\033[{32 if not _ else 90}m ", end = "")
            self.write(f"0x{offset:04x} {instruction.opcode}", end = " ")

            # Read arguments
            arg_offset = 1
            for arg in instruction.args:
                value = int.from_bytes(self.memory[offset + arg_offset:offset + arg_offset + arg.size])

                # Try to become human readable
                self.write(f"0x{value:04x}", end = " ")
                arg_offset += arg.size

            self.write("\033[0m")
            offset += arg_offset

        print()

    def print_registers(self) -> None:
        def register_value(offset: int) -> str:
            value = int.from_bytes(self.memory[offset:offset + 2])
            return f"\033[{32 if value else 90}m{value}\033[0m"

        self.print_label("REGISTERS")
        for register in range(9):
            offset = register * 2
            print(f" R{register + 1}: {register_value(offset)}")

        print("\033[9A", end = "")
        for index, register in enumerate(("LC", "CR", "SP")):
            offset = REGISTERS_BY_NAME["LC"].address + (index * 2)
            print(f"\033[10C{register}: {register_value(offset)}")

    def print_stdout(self) -> None:
        print("\033[H\033[30C", end = "")
        self.print_label("STDOUT")

        # Print out stdout (byte encoded)
        stdout = str(self.stdout_store.getvalue().encode())[2:-1]
        for item in ["".join(batch) for batch in batched(stdout, 100)]:
            self.write(f"\033[30C{item}")

    def print_console(self) -> None:
        print(f"\033[H{'\n' * 9}\033[30C", end = "")
        self.print_label("CONSOLE")
        print("\033[30CPress \033[32m[ENTER]\033[0m to step once.\n\033[30CType a number of steps and press \033[32m[ENTER]\033[0m to autostep.\n")

        # Read input
        steps = input("\033[30C> ")
        if steps.isdecimal():
            self.steps = int(steps)

    def show_interface(self) -> None:
        print("\033[2J\033[H", end = "")

        # Printing
        self.print_instructions()
        self.print_registers()
        self.print_stdout()

        # Rebind CTRL+C to actually exit
        if self.steps > 0:
            self.steps -= 1
            return

        try:
            self.print_console()

        except KeyboardInterrupt:
            print("\033[2J\033[H", end = "")
            sys.exit()

    def step(self) -> None:
        sys.stdout = self.stdout

        # Handle debugging UI
        self.show_interface()

        # Erase previous data
        if self.stdout_store.tell() > 200:
            text = self.stdout_store.getvalue()[-200:]
            self.stdout_store.seek(0)
            self.stdout_store.truncate(0)
            self.stdout_store.write(text)

        sys.stdout = self.stdout_store
