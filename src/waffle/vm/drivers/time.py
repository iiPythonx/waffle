# Copyright (c) 2026 iiPython

# Driver: time
# Purpose: Provide time related utilities to waffle
#
# Registers:
#   W SET_TIME_UNIT - Set item to read (see OPTIONS)
#   R READ_TIME     - Read currently selected item
#   W SET_TIME_FMT  - Set memory address of strftime string
#   W READ_TIME_FMT - Read time in strftime format to specified memory address
#   W SLEEP         - Sleep main thread for specified duration in milliseconds
#   W ZERO_CLOCK    - Set elapsed clock to zero
#   R READ_ELAPSED  - Read elapsed clock in requested unit (MONTH and YEAR unsupported)
#
# Options:
#   SET_TIME_UNIT -> 0: Millisecond
#   SET_TIME_UNIT -> 1: Second
#   SET_TIME_UNIT -> 2: Minute
#   SET_TIME_UNIT -> 3: Hour
#   SET_TIME_UNIT -> 4: Day
#   SET_TIME_UNIT -> 5: Month
#   SET_TIME_UNIT -> 6: Year
#
# Examples:
#   ldi r1, 1
#   swa r1, D_SET_TIME_UNIT  ; Set selection to SECOND
#   lwa r1, D_READ_TIME      ; Read into R1
#   swa r1, D_WRITE_INT      ; Send R1 (second) to screen
#
#   ldi r1, 500
#   swa r1, D_SLEEP          ; Halt main thread for 500ms

import math
from datetime import UTC, datetime
from time import perf_counter, sleep

from waffle.vm.drivers import DriverManager


class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind("SET_TIME_UNIT", self.write_selection)
        core.bind("READ_TIME",     self.read_selection)
        core.bind("SET_TIME_FMT",  self.write_strftime)
        core.bind("READ_TIME_FMT", self.read_strftime)
        core.bind("SLEEP",         self.write_sleep)
        core.bind("ZERO_CLOCK",    self.write_zero_clock)
        core.bind("READ_ELAPSED",  self.read_elapsed)

        # State
        self.selection = 0
        self.strftime_address = 0
        self.elapsed_start = 0

    @property
    def now(self) -> datetime:
        return datetime.now(UTC).astimezone()

    def write_selection(self, memory: bytearray, value: int) -> None:
        self.selection = value

    def read_selection(self, memory: bytearray) -> int:
        match self.selection:
            case 0:
                return self.now.microsecond // 10

            case 1:
                return self.now.second

            case 2:
                return self.now.minute

            case 3:
                return self.now.hour

            case 4:
                return self.now.day

            case 5:
                return self.now.month

            case 6:
                return self.now.year

        return 0

    def write_strftime(self, memory: bytearray, value: int) -> None:
        self.strftime_address = value

    def read_strftime(self, memory: bytearray, value: int) -> None:
        read_value = self.now.strftime(memory[self.strftime_address:].split(b"\0")[0].decode())
        for index, item in enumerate(read_value.encode("utf-8") + b"\0"):
            memory[value + index] = item

    def write_sleep(self, memory: bytearray, value: int) -> None:
        sleep(value / 1000)

    def write_zero_clock(self, memory: bytearray, value: int) -> None:
        self.elapsed_start = perf_counter()

    def read_elapsed(self, memory: bytearray) -> int:
        elapsed = perf_counter() - self.elapsed_start
        match self.selection:
            case 0:
                return math.floor(elapsed * 1000)

            case 1:
                return math.floor(elapsed)

            case 2:
                return math.floor(elapsed / 60)

            case 3:
                return math.floor(elapsed / 3600)

            case 4:
                return math.floor(elapsed / 86400)

            case _:
                return 0
