# Copyright (c) 2026 iiPython

# Driver: random
# Purpose: Provide psuedo-random number generation to waffle
#
# Registers:
#   R GET_RANDOM - Read a random 16-bit integer
#   W SET_RANDOM_BOUNDS - Set maximum bound
#
# Examples:
#   lwa r1, D_GET_RANDOM  ; Load random number between 0 - 65535 to R1
#   swa r1, D_WRITE_INT   ; Send R1 to screen
#
#   ldi r1, 100
#   swa r1, D_SET_RANDOM_BOUNDS  ; Set RNG upper bound to 100
#   lwa r1, D_GET_RANDOM         ; Load random number between 0 - 100 to R1
#   swa r1, D_WRITE_INT          ; Send R1 to screen

import random

from waffle.vm.drivers import DriverManager


class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind("GET_RANDOM",        self.read_random)
        core.bind("SET_RANDOM_BOUNDS", self.write_upper_bound)

        self.upper_bound = (2 ** 16) - 1

    def read_random(self, memory: bytearray) -> int:
        return random.randint(0, self.upper_bound)

    def write_upper_bound(self, memory: bytearray, value: int) -> None:
        self.upper_bound = value
