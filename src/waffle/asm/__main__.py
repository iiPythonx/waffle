# Copyright (c) 2026 iiPython

import gzip
from pathlib import Path
from time import perf_counter

from waffle.asm import exception
from waffle.asm.assemble import Assembler
from waffle.asm.token import parse_file
from waffle.cli import cexit, p
from waffle.vm.drivers import DriverManager


def main() -> None:
    p.add_argument("source", type = Path, help = "path to source code")
    p.add_argument("-G", "--gzip", action = "store_true", default = False, help = "compress output with gzip")
    p.add_argument("-Z", "--zero-jump", action = "store_true", default = False, help = "auto jump to the main label on launch")
    p.add_argument("-d", "--drivers", help = "enabled list of drivers, default: stdio", default = "stdio")
    p.add_argument("-N", "--no-drivers", action = "store_true", help = "disable all drivers", default = False)

    args = p.parse_args()

    # Confirm file
    file = Path(args.source)
    if not file.is_file():
        cexit("The provided file path does not exist.")

    exception.set_file(file)

    # Initialize requested drivers
    # We need to do this to retrieve their name mappings
    enabled_drivers = args.drivers.split(",") if not args.no_drivers else []
    drivers = DriverManager(bytearray(), enabled_drivers)

    # Initialize assembler
    asm = Assembler(parse_file(file), drivers.binding_names)

    # Build snapshot
    start_time = perf_counter()
    snapshot = asm.assemble(zero_jump = args.zero_jump)
    elapsed = perf_counter() - start_time

    # Add in the enabled driver names
    driver_bytes = bytearray()
    driver_bytes.append(len(enabled_drivers))
    for driver_name in enabled_drivers:
        driver_bytes.extend(driver_name.encode() + b"\0")

    snapshot = driver_bytes + snapshot

    # Compression
    if args.gzip:
        snapshot = gzip.compress(snapshot)

    # Write to binary file and show status
    file.with_suffix(".bin").write_bytes(snapshot)
    print(f"Compiled in \033[32m{elapsed * 1000:.2f}ms\033[0m to \033[32m{file.with_suffix('.bin')}\033[0m")
