<p align = "center">
    <img alt = "waffle logo" src = ".github/logo.png">
    <hr>
</p>

A 16-bit CPU with 16 KiB of RAM, for playing around with.

## Installation

```bash
git clone git@github.com:iiPythonx/waffle
cd waffle

# Activate environment
uv venv
source .venv/bin/activate
uv pip install -e .

# Run the clock example
waffleasm -Z examples/clock.asm
waffleemu examples/clock.bin
```

## Features

- Complete [ISA](https://en.wikipedia.org/wiki/Instruction_set_architecture) covering memory operations, math, and branching
- 9 general purpose registers (R1 - R9) with 3 hardware registers (LC, CR, & SP)
- [MMIO](https://en.wikipedia.org/wiki/Memory-mapped_I/O_and_port-mapped_I/O) for [drivers](#drivers) on the 0x0013 - 0x0100 range
- Subroutine and stack support, including `PSH`, `POP`, `CAL`, & `RET`

## Specifications

Last updated: August 9th, 2026  
Version: 2.2.1

### Memory

```js
16 KiB / 16386 B

0x0000 - 0x0100: REGISTERS
0x0100 - 0x2000: CODE
0x2000 - 0x3000: DATA
0x3000 - 0x4000: STACK
```

### Registers

```js
0x0: R1
0x1: R2
0x2: R3
0x3: R4
0x4: R5
0x5: R6
0x6: R7
0x7: R8
0x8: R9
0xA: LC (LINE COUNTER)
0xB: CR (COMPARE RESULT)
0xC: SP (STACK POINTER)
```

### Instructions

```js
R = CPU REG
A = MEM ADDR
V = VALUE (ASM EMBEDDED)

0x00: HLT     (HALT)
0x01: LDI R V (LOAD IMMEDIATE)
0x02: LBA R A (LOAD BYTE ADDRESS)
0x03: LBR R R (LOAD BYTE REGISTER)
0x04: LWA R A (LOAD WORD ADDRESS)
0x05: LWR R R (LOAD WORD REGISTER)
0x06: SBA R A (STORE BYTE ADDRESS)
0x07: SBR R R (STORE BYTE REGISTER)
0x08: SWA R A (STORE WORD ADDRESS)
0x09: SWR R R (STORE WORD REGISTER)
0x0A: ADD R R (ADD)
0x0B: SUB R R (SUBTRACT)
0x0C: MUL R R (MULTIPLY)
0x0D: DIV R R (DIVIDE)
0x0E: AND R R (BITWISE AND)
0x0F: OR  R R (BITWISE OR)
0x10: XOR R R (BITWISE EXCLUSIVE OR)
0x11: NOT R   (BITWISE NOT)
0x12: SHL R R (SHIFT LEFT)
0x13: SHR R R (SHIFT RIGHT)
0x14: CMP R R (COMPARE)
0x15: JEQ A   (JUMP EQUAL)
0x16: JNE A   (JUMP NOT EQUAL)
0x17: JGT A   (JUMP GREATER THAN)
0x18: JLT A   (JUMP LESS THAN)
0x19: JGE A   (JUMP GREATER EQUAL)
0x1A: JLE A   (JUMP LESS EQUAL)
0x1B: JMP A   (JUMP)
0x1C: CAL A   (CALL SUBROUTINE)
0x1D: RET     (RETURN FROM SUBROUTINE)
0x1E: PSH R   (PUSH REGISTER TO STACK)
0x1F: POP R   (POP STACK TO REGISTER)
0x20: INC R   (INCREMENT)
0x21: DEC R   (DECREMENT)
0x22: MOV R R (COPY REGISTER)
```

### Drivers

See the [vm/drivers](./src/waffle/vm/drivers) tree for a list of drivers.  
It's up to the driver maintainer to produce accurate documentation regarding their use.

## Labels

### Preload

You can create a label called `preload` to store strings or raw data into the data block automatically at assembly time.  
Here's an example:

```asm
preload:
    hello: .string "Hello, world!"
```

This string will be automatically loaded into memory starting at the 0x2000 block.  
Referencing it can be done with `ldi r1, &hello`, which will load the string's memory address into R1.

Available types:
- `string` and `asciz`: encode as UTF-8 and add a null byte
- `ascii`: encode as UTF-8
- `byte`: encode as a one byte integer
- `word` and `short`: encode as a two byte integer

For integers, you can write their value in either decimal (`82`) or hex (`0x52`).

### Main

No main label is required to be used, as the only requirement of waffle assembly is that ONE label exists (of which preload does not count).  
If you do add a main label, however, you will likely want to make use of the `-Z` (`--zero-jump`) flag on `waffleasm`, which will auto jump to main on program init.

## Debugger

Run `waffleemu` with the `-D` (`--debug`) option to enable the built-in system debugger.

![waffle debugger](.github/debugger.png)

## Inspiration

waffle is based on [BASIC](https://en.wikipedia.org/wiki/BASIC) and [Assembly](https://en.wikipedia.org/wiki/Assembly_language).  
The CPU itself has no real backing inspiration, it's just a normal 16-bit chip w/ RAM.

## Copyright

© 2024-2026 Benjamin "iiPython" O'Brien, see [LICENSE.txt](LICENSE.txt) for details.
