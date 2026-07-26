# Copyright (c) 2026 iiPython

# Driver: time
# Purpose: Provide time related utilities to waffle
#
# Registers:
#   W 0x0050 - Set item to read (see OPTIONS)
#   R 0x0052 - Read currently selected item
#   W 0x0054 - Set memory address of strftime string
#   W 0x0056 - Read time in strftime format to specified memory address
#   W 0x0058 - Sleep main thread for specified duration in milliseconds
#   W 0x005A - Set elapsed clock to zero
#   R 0x005C - Read elapsed clock in requested unit (MONTH and YEAR unsupported)
#
# Options:
#   0x0050 -> 0: Millisecond
#   0x0050 -> 1: Second
#   0x0050 -> 2: Minute
#   0x0050 -> 3: Hour
#   0x0050 -> 4: Day
#   0x0050 -> 5: Month
#   0x0050 -> 6: Year
#
# Examples:
#   ldi r1, 1
#   swa r1, 0x0050  ; Set selection to SECOND
#   lwa r1, 0x0052  ; Read into R1
#   swa r1, 0x0024  ; Send R1 (second) to screen
#
#   ldi r1, 500
#   swa r1, 0x0054  ; Halt main thread for 500ms

import math
from time import perf_counter, sleep
from datetime import datetime
from zoneinfo import ZoneInfo

from waffle.vm.drivers import DriverManager

class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind_write("SET_TIME_UNIT", 0x0050, self.write_selection)
        core.bind_read( "READ_TIME",     0x0052, self.read_selection)
        core.bind_write("SET_TIME_FMT",  0x0054, self.write_strftime)
        core.bind_write("READ_TIME_FMT", 0x0056, self.read_strftime)
        core.bind_write("SLEEP",         0x0058, self.write_sleep)
        core.bind_write("ZERO_CLOCK",    0x005A, self.write_zero_clock)
        core.bind_read( "READ_ELAPSED",  0x005C, self.read_elapsed)

        # State
        self.selection = 0
        self.strftime_address = 0
        self.elapsed_start = 0

    @property
    def now(self) -> datetime:
        return datetime.now(tz = ZoneInfo("localtime"))

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
