# Copyright (c) 2026 iiPython

# Driver: random
# Purpose: Provide psuedo-random number generation to waffle
#
# Registers:
#   R 0x0030 - Read a random 16-bit integer
#   W 0x0032 - Set maximum bound
#
# Examples:
#   lwa r1, 0x0030  ; Load random number between 0 - 65535 to R1
#   swa r1, 0x0024  ; Send R1 to screen
#
#   ldi r1, 100
#   swa r1, 0x0032  ; Set RNG upper bound to 100
#   lwa r1, 0x0030  ; Load random number between 0 - 100 to R1
#   swa r1, 0x0024  ; Send R1 to screen

import random

from waffle.vm.drivers import DriverManager

class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind_read( "GET_RANDOM",        0x0030, self.read_random)
        core.bind_write("SET_RANDOM_BOUNDS", 0x0032, self.write_upper_bound)

        self.upper_bound = (2 ** 16) - 1

    def read_random(self, memory: bytearray) -> int:
        return random.randint(0, self.upper_bound)

    def write_upper_bound(self, memory: bytearray, value: int) -> None:
        self.upper_bound = value
