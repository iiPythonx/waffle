# Copyright (c) 2026 iiPython

# Driver: stdio
# Purpose: Provide general purpose I/O to waffle
#
# Registers:
#   W 0x0020 - Send a character to the screen
#   W 0x0022 - Send a string to the screen from a memory address
#   W 0x0024 - Send an integer to the screen
#   W 0x0026 - Clear the entire screen and reset to home position
#   R 0x0028 - Read one character from stdin and place in requested register
#   W 0x002A - Read an entire string from stdin into memory at offset 0x2100
# 
# Examples:
#   ldi r1, 72
#   swa r1, 0x0020  ; Send ASCII 72 (H) from R1 to the screen
#
#   ldi r1, &hello  ; Assume hello is an existing string
#   swa r1, 0x0022  ; Send the entire string to the screen
#                   ; This also reads until it hits a NULL byte (\0), so be wary of that
#
#   ldi r1, 69
#   swa r1, 0x0024  ; Send the number 69 to the screen (for debugging math, etc)
#
#   ldi r1, 0       ; Not needed, as clear doesn't care about args
#   swa r1, 0x0026  ; Wipe the entire screen and reset
#
#   lwa r1, 0x0028  ; Grab one character from stdin
#   ldi r1, 0x0024  ; Send ASCII code to stdout
#
#   ldi r1, 0x2100  ; Set R1 to memory addr 0x2100
#   swa r1, 0x002A  ; Request an entire string from stdin
#   swa r1, 0x0022  ; Send the entire memory block to the screen

import sys
import tty
import termios

from waffle.vm.drivers import DriverManager

class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind_write("WRITE_CHR", 0x0020, self.write_character)
        core.bind_write("WRITE_STR", 0x0022, self.write_string)
        core.bind_write("WRITE_INT", 0x0024, self.write_integer)
        core.bind_write("CLEAR_SCR", 0x0026, self.clear_screen)
        core.bind_read( "READ_CHR",  0x0028, self.read_stdin_getch)
        core.bind_write("READ_STR",  0x002A, self.read_stdin_input)

    def write(self, data: str) -> None:
        print(data, end = "", flush = True)

    def write_character(self, memory: bytearray, value: int) -> None:
        self.write(chr(value))

    def write_string(self, memory: bytearray, value: int) -> None:
        for item in memory[value:]:
            if not item:
                break

            self.write(chr(item))

    def write_integer(self, memory: bytearray, value: int) -> None:
        self.write(str(value))

    def clear_screen(self, memory: bytearray, value: int) -> None:
        self.write("\033[2J\033[H")

    def read_stdin_getch(self, memory: bytearray) -> int:
        existing_fileno = sys.stdin.fileno()
        settings = termios.tcgetattr(existing_fileno)
        tty.setcbreak(sys.stdin.fileno())

        # Read our character
        character = sys.stdin.read(1)
        termios.tcsetattr(existing_fileno, termios.TCSADRAIN, settings)
        return ord(character)

    def read_stdin_input(self, memory: bytearray, value: int) -> None:
        for index, item in enumerate(input().encode("utf-8") + b"\0"):
            memory[value + index] = item
