# Copyright (c) 2026 iiPython

import importlib
import typing
from pathlib import Path

from waffle.cli import cexit


class DriverManager:
    def __init__(self, memory: bytearray, enabled_drivers: dict[str, int] | None = None) -> None:
        self.memory = memory

        # Handle bindings
        self.binding_names: dict[str, typing.Callable] = {}
        self.binding_addresses: dict[int, typing.Callable] = {}

        # Begin initializing drivers
        for file in Path(__file__).parent.iterdir():
            if file.suffix != ".py" or file.name == "__init__.py":
                continue

            module = importlib.import_module(f"waffle.vm.drivers.{file.stem}")
            driver = module.Driver
            if driver is None:
                cexit(f"Attempted to load driver '{file.stem}', but it has no Driver class!")
                return

            driver(self)

        # Move to correct MMIO addressess
        for name, address in (enabled_drivers or {}).items():
            self.initialize(name, address)

    def initialize(self, name: str, address: int) -> None:
        if name in self.binding_names:
            self.binding_addresses[address] = self.binding_names[name]

    def bind(self, name: str, callback: typing.Callable) -> None:
        self.binding_names[name] = callback

    def on_write(self, address: int, value: int) -> bool:
        if address in self.binding_addresses:
            self.binding_addresses[address](self.memory, value)
            return True

        return False

    def on_read(self, address: int) -> int | None:
        if address in self.binding_addresses:
            return self.binding_addresses[address](self.memory)

        return None
