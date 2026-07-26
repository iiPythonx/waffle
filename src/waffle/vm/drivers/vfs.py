# Copyright (c) 2026 iiPython

# Driver: vfs
# Purpose: Provide a virtual file system (vfs) to waffle
#
# Registers:
#   W 0x0040 - Set memory address containing target filename
#   W 0x0042 - Read file contents into provided memory offset
#   W 0x0044 - Set data size (for pending write)
#   W 0x0046 - Write from provided memory offset into target file (size required)
#   W 0x0048 - Write from provided memory offset into target file (null terminated)
#   R 0x004A - Return size of target file
#   R 0x004C - Return status of target file (1 = exists, 0 = doesn't exist)

from pathlib import Path

from waffle.vm.drivers import DriverManager

class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind_write("SET_FILENAME",        0x0040, self.write_memory_address)
        core.bind_write("READ_FILE",           0x0042, self.write_file_contents)
        core.bind_write("SET_FILE_WRITE_SIZE", 0x0044, self.write_data_size)
        core.bind_write("WRITE_TO_FILE",       0x0046, self.write_into_file)
        core.bind_write("WRITE_TO_NULL_FILE",  0x0048, self.write_into_file_auto)
        core.bind_read( "READ_FILE_SIZE",      0x004A, self.read_file_size)
        core.bind_read( "READ_FILE_STATUS",    0x004C, self.read_file_status)

        self.address = 0x2400
        self.size = 0

    def read_filename(self, memory: bytearray) -> Path:
        return Path(memory[self.address:].split(b"\0", 1)[0].decode())

    def write_memory_address(self, memory: bytearray, value: int) -> None:
        self.address = value

    def write_file_contents(self, memory: bytearray, value: int) -> None:
        file = self.read_filename(memory)
        if not file.is_file():
            return

        for index, item in enumerate(file.read_bytes() + b"\0"):
            memory[value + index] = item

    def write_data_size(self, memory: bytearray, value: int) -> None:
        self.size = value

    def write_into_file(self, memory: bytearray, value: int) -> None:
        self.read_filename(memory).write_bytes(memory[value:value + self.size])

    def write_into_file_auto(self, memory: bytearray, value: int) -> None:
        self.read_filename(memory).write_bytes(memory[value:].split(b"\0", 1)[0])

    def read_file_size(self, memory: bytearray) -> int:
        file = self.read_filename(memory)
        return file.stat().st_size if file.is_file() else 0

    def read_file_status(self, memory: bytearray) -> int:
        return int(self.read_filename(memory).is_file())
