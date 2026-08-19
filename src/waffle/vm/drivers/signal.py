# Copyright (c) 2026 iiPython

# Driver: signal
# Purpose: Provide signal handling capabilities to waffle

import signal
import typing

from waffle.isa import REGISTERS
from waffle.vm.drivers import DriverManager

REGISTERS_BY_ID = {reg.id: reg for reg in REGISTERS}

class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind("SIG_TARGET" ,  self.set_signal)
        core.bind("SIG_HOOK",  self.hook_signal)
        core.bind("SIG_RESET", self.reset_signal)

        self.hooks: dict[int, int] = {}
        self.targeted_signal: int = 0

    def callback(self, memory: bytearray, value: int) -> None:
        offset = REGISTERS_BY_ID[0xA].address
        memory[offset:offset + 2] = (value & 0xFFFF).to_bytes(2)

    def set_signal(self, memory: bytearray, value: int) -> None:
        self.targeted_signal = value

    def hook_signal(self, memory: bytearray, value: int) -> None:
        signal.signal(self.targeted_signal, lambda a, b: self.callback(memory, value))

    def reset_signal(self, memory: bytearray, value: int) -> None:
        existing_signal = signal.getsignal(self.targeted_signal)
        if isinstance(existing_signal, typing.Callable) and existing_signal.__name__ == "<lambda>":
            signal.signal(self.targeted_signal, signal.SIG_DFL)
