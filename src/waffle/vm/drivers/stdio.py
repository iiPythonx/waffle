# Copyright (c) 2026 iiPython

# Driver: stdio
# Purpose: Provide general purpose I/O to waffle
#
# Registers:
#   W WRITE_CHR - Send a character to the screen
#   W WRITE_STR - Send a string to the screen from a memory address
#   W WRITE_INT - Send an integer to the screen
#   W CLEAR_SCR - Clear the entire screen and reset to home position
#   R READ_CHR  - Read one character from stdin and place in requested register
#   W READ_STR  - Read an entire string from stdin into memory at offset 0x2100
# 
# Examples:
#   ldi r1, 72
#   swa r1, D_WRITE_CHR  ; Send ASCII 72 (H) from R1 to the screen
#
#   ldi r1, &hello       ; Assume hello is an existing string
#   swa r1, D_WRITE_STR  ; Send the entire string to the screen
#                        ; This also reads until it hits a NULL byte (\0), so be wary of that
#
#   ldi r1, 69
#   swa r1, D_WRITE_INT  ; Send the number 69 to the screen (for debugging math, etc)
#
#   ldi r1, 0            ; Not needed, as clear doesn't care about args
#   swa r1, D_CLEAR_SCR  ; Wipe the entire screen and reset
#
#   lwa r1, D_READ_CHR   ; Grab one character from stdin
#   ldi r1, D_WRITE_INT  ; Send ASCII code to stdout
#
#   ldi r1, 0x2100       ; Set R1 to memory addr 0x2100
#   swa r1, D_READ_STR   ; Request an entire string from stdin
#   swa r1, D_WRITE_STR  ; Send the entire memory block to the screen

import sys
import termios
import tty

from waffle.vm.drivers import DriverManager


class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind("WRITE_CHR", self.write_character)
        core.bind("WRITE_STR", self.write_string)
        core.bind("WRITE_INT", self.write_integer)
        core.bind("CLEAR_SCR", self.clear_screen)
        core.bind("READ_CHR",  self.read_stdin_getch)
        core.bind("READ_STR",  self.read_stdin_input)

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
