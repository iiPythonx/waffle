// Copyright (c) 2026 iiPython

const ArgumentType = Object.freeze({
    REGISTER: 0,
    ADDRESS:  1,
    VALUE:    2
});

export const ARGUMENT_SIZES = Object.freeze({
    [ArgumentType.REGISTER]: 1,
    [ArgumentType.ADDRESS]:  2,
    [ArgumentType.VALUE]:    2,
});

// Instructions
export const INSTRUCTIONS = Object.freeze({
    0x00: {
        args: [],
        opcode: "HLT",
        name: "HALT",
    },
    0x01: {
        args: [ArgumentType.REGISTER, ArgumentType.VALUE],
        opcode: "LDI",
        name: "LOAD IMMEDIATE",
    },
    0x02: {
        args: [ArgumentType.REGISTER, ArgumentType.ADDRESS],
        opcode: "LBA",
        name: "LOAD BYTE ADDRESS",
    },
    0x03: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "LBR",
        name: "LOAD BYTE REGISTER",
    },
    0x04: {
        args: [ArgumentType.REGISTER, ArgumentType.ADDRESS],
        opcode: "LWA",
        name: "LOAD WORD ADDRESS",
    },
    0x05: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "LWR",
        name: "LOAD WORD REGISTER",
    },
    0x06: {
        args: [ArgumentType.REGISTER, ArgumentType.ADDRESS],
        opcode: "SBA",
        name: "STORE BYTE ADDRESS",
    },
    0x07: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "SBR",
        name: "STORE BYTE REGISTER",
    },
    0x08: {
        args: [ArgumentType.REGISTER, ArgumentType.ADDRESS],
        opcode: "SWA",
        name: "STORE WORD ADDRESS",
    },
    0x09: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "SWR",
        name: "STORE WORD REGISTER",
    },
    0x0A: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "ADD",
        name: "ADD",
    },
    0x0B: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "SUB",
        name: "SUBTRACT",
    },
    0x0C: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "MUL",
        name: "MULTIPLY",
    },
    0x0D: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "DIV",
        name: "DIVIDE",
    },
    0x0E: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "AND",
        name: "BITWISE AND",
    },
    0x0F: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "OR",
        name: "BITWISE OR",
    },
    0x10: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "XOR",
        name: "BITWISE EXCLUSIVE OR",
    },
    0x11: {
        args: [ArgumentType.REGISTER],
        opcode: "NOT",
        name: "BITWISE NOT",
    },
    0x12: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "SHL",
        name: "SHIFT LEFT",
    },
    0x13: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "SHR",
        name: "SHIFT RIGHT",
    },
    0x14: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "CMP",
        name: "COMPARE",
    },
    0x15: {
        args: [ArgumentType.ADDRESS],
        opcode: "JEQ",
        name: "JUMP EQUAL",
    },
    0x16: {
        args: [ArgumentType.ADDRESS],
        opcode: "JNE",
        name: "JUMP NOT EQUAL",
    },
    0x17: {
        args: [ArgumentType.ADDRESS],
        opcode: "JGT",
        name: "JUMP GREATER THAN",
    },
    0x18: {
        args: [ArgumentType.ADDRESS],
        opcode: "JLT",
        name: "JUMP LESS THAN",
    },
    0x19: {
        args: [ArgumentType.ADDRESS],
        opcode: "JGE",
        name: "JUMP GREATER EQUAL",
    },
    0x1A: {
        args: [ArgumentType.ADDRESS],
        opcode: "JLE",
        name: "JUMP LESS EQUAL",
    },
    0x1B: {
        args: [ArgumentType.ADDRESS],
        opcode: "JMP",
        name: "JUMP",
    },
    0x1C: {
        args: [ArgumentType.ADDRESS],
        opcode: "CAL",
        name: "CALL SUBROUTINE",
    },
    0x1D: {
        args: [],
        opcode: "RET",
        name: "RETURN FROM SUBROUTINE",
    },
    0x1E: {
        args: [ArgumentType.REGISTER],
        opcode: "PSH",
        name: "PUSH REGISTER TO STACK",
    },
    0x1F: {
        args: [ArgumentType.REGISTER],
        opcode: "POP",
        name: "POP STACK TO REGISTER",
    },
    0x20: {
        args: [ArgumentType.REGISTER],
        opcode: "INC",
        name: "INCREMENT",
    },
    0x21: {
        args: [ArgumentType.REGISTER],
        opcode: "DEC",
        name: "DECREMENT",
    },
    0x22: {
        args: [ArgumentType.REGISTER, ArgumentType.REGISTER],
        opcode: "MOV",
        name: "COPY REGISTER",
    }
});

// Registers
const REGISTERS = [
    { name: "R1", id: 0x0, address: 0x00 },
    { name: "R2", id: 0x1, address: 0x02 },
    { name: "R3", id: 0x2, address: 0x04 },
    { name: "R4", id: 0x3, address: 0x06 },
    { name: "R5", id: 0x4, address: 0x08 },
    { name: "R6", id: 0x5, address: 0x0A },
    { name: "R7", id: 0x6, address: 0x0C },
    { name: "R8", id: 0x7, address: 0x0E },
    { name: "R9", id: 0x8, address: 0x10 },

    { name: "LC", id: 0xA, address: 0x12 },
    { name: "CR", id: 0xB, address: 0x14 },
    { name: "SP", id: 0xC, address: 0x16 }
];
export const REGISTERS_BY_ID = Object.fromEntries(REGISTERS.map(r => [r.id, r]));

Object.freeze(REGISTERS);
Object.freeze(REGISTERS_BY_ID);

// Memory addresses
const address = (start, end) => Object.freeze({ start, end, size: end - start });
export const Addresses = Object.freeze({
    REGISTERS: address(0x0000, 0x0100),
    CODE:      address(0x0100, 0x2000),
    DATA:      address(0x2000, 0x3000),
    STACK:     address(0x3000, 0x4000)
});
