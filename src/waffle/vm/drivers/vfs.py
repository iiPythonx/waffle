# Copyright (c) 2026 iiPython

# Driver: vfs
# Purpose: Provide a virtual file system (vfs) to waffle
#
# Registers:
#   W SET_FILENAME        - Set memory address containing target filename
#   W READ_FILE           - Read file contents into provided memory offset
#   W SET_FILE_WRITE_SIZE - Set data size (for pending write)
#   W WRITE_TO_FILE       - Write from provided memory offset into target file (size required)
#   W WRITE_TO_NULL_FILE  - Write from provided memory offset into target file (null terminated)
#   R READ_FILE_SIZE      - Return size of target file
#   R READ_FILE_STATUS    - Return status of target file (1 = exists, 0 = doesn't exist)

from pathlib import Path

from waffle.vm.drivers import DriverManager


class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind("SET_FILENAME",        self.write_memory_address)
        core.bind("READ_FILE",           self.write_file_contents)
        core.bind("SET_FILE_WRITE_SIZE", self.write_data_size)
        core.bind("WRITE_TO_FILE",       self.write_into_file)
        core.bind("WRITE_TO_NULL_FILE",  self.write_into_file_auto)
        core.bind("READ_FILE_SIZE",      self.read_file_size)
        core.bind("READ_FILE_STATUS",    self.read_file_status)

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
