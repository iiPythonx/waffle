# Copyright (c) 2026 iiPython

# Driver: snapshot
# Purpose: Provide basic memory analysis capabilities to waffle
#
# Registers:
#   W 0x0060 - Save memory snapshot to snapshot.bin
#
# Examples:
#   swa r1, D_MEMORY_SNAPSHOT

from pathlib import Path
from waffle.vm.drivers import DriverManager

class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind_write("MEMORY_SNAPSHOT", 0x0060, self.write_snapshot)

    def write_snapshot(self, memory: bytearray, value: int) -> None:
        Path("snapshot.bin").write_bytes(memory)
