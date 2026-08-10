# Copyright (c) 2026 iiPython

import sys
from argparse import ArgumentParser

p = ArgumentParser(
    description = "A 16-bit CPU with 16 KiB of RAM.",
    epilog = "Copyright (c) 2024-2026 iiPython"
)

def cexit(message: str) -> None:
    print(message)
    sys.exit(1)
