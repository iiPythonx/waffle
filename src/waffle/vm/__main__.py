# Copyright (c) 2026 iiPython

import gzip
from pathlib import Path
from time import sleep

from waffle.cli import cexit, p
from waffle.isa import Addresses
from waffle.vm.core import Waffle


def main() -> None:
    p.add_argument("-s", "--speed", type = int, help = "emulation speed in hertz, default: no limit", default = 0)
    p.add_argument("-D", "--debug", action = "store_true", help = "enable the debugger", default = False)
    p.add_argument("executable", type = Path, help = "path to compiled executable")

    args = p.parse_args()

    # Confirm file
    file = Path(args.executable)
    if not file.is_file():
        cexit("The provided file path does not exist.")

    bytecode = file.read_bytes()

    # Handle decompression
    if bytecode[:2] == b"\x1f\x8b":
        try:
            bytecode = gzip.decompress(bytecode)

        except gzip.BadGzipFile:
            cexit("Gzip decompression failed! Is the file corrupted?")

    # Confirm speed
    speed = args.speed
    if speed < 0:
        cexit("Provided speed argument is negative and thus invalid.")

    # Fetch drivers
    enabled_drivers, driver_offset = {}, 0
    for _ in range(bytecode[0]):
        driver_name = ""
        for character in bytecode[driver_offset + 1:]:
            if not character:
                break

            driver_name += chr(character)

        driver_offset += len(driver_name) + 3
        enabled_drivers[driver_name] = int.from_bytes(bytecode[driver_offset - 1:driver_offset + 1])

    bytecode = bytecode[driver_offset + 1:]

    # Setup emulation
    system = Waffle(
        enabled_drivers = enabled_drivers,
        enable_debugger = args.debug
    )

    system.write_range(bytecode[:Addresses.CODE.size], Addresses.CODE.start)
    system.write_range(bytecode[Addresses.CODE.size:], Addresses.CODE.end)

    if system.enable_debugger:
        system.debugger.init()

    # System loop
    delay = 1 / speed if speed != 0 else 0
    while True:
        try:
            system.step()
            sleep(delay)

        except KeyboardInterrupt:
            system.terminate()

