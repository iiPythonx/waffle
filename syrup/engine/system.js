// Copyright (c) 2026 iiPython

import { ARGUMENT_SIZES, REGISTERS_BY_ID, INSTRUCTIONS, Addresses } from "./isa.js";

// Utilities
const hex = (n) => `0x${n.toString(16).padStart(4, "0")}`;

// Waffle
class Waffle {
    constructor() {
        this.ram = new Uint8Array(Addresses.STACK.end);
        this.view = new DataView(this.ram.buffer);

        // Initialize SP
        this.write_reg(0xC, 2);
    }

    // Stack
    push_stack(value) {
        const offset = this.read_reg(0xC);
        this.write_word(Addresses.STACK.end - offset, value);
        this.write_reg(0xC, offset + 2);
    }

    pop_stack() {
        const offset = this.read_reg(0xC) - 2;
        if (offset === 0) return -1;

        this.write_reg(0xC, offset);
        return this.read_word(Addresses.STACK.end - offset);
    }

    // Registers
    read_reg(register) {
        const offset = REGISTERS_BY_ID[register].address;
        return this.view.getUint16(offset, false);
    }

    write_reg(register, value) {
        const offset = REGISTERS_BY_ID[register].address;
        this.view.setUint16(offset, value & 0xFFFF, false);
    }

    // General I/O
    read_word(offset) { return this.view.getUint16(offset, false); }
    write_word(offset, value) { this.view.setUint16(offset, value & 0xFFFF, false); }

    read_byte(offset) { return this.ram[offset]; }
    write_byte(offset, value) { this.ram[offset] = value & 0xFF; }

    // Handle file parsing
    load(bytecode) {
        const view = new DataView(bytecode.buffer, bytecode.byteOffset, bytecode.byteLength);
        const drivers = new Map();

        let offset = 1;
        for (let i = 0; i < bytecode[0]; i++) {
            const start = offset;
            while (bytecode[offset] !== 0) offset++;

            const name = new TextDecoder().decode(bytecode.subarray(start, offset));
            offset++;

            drivers.set(name, view.getUint16(offset, false));
            offset += 2;
        }

        // this.drivers = drivers;
        this.ram.set(bytecode.subarray(offset), Addresses.CODE.start);
    }

    // Execution
    step() {
        const current_line = this.read_reg(0xA);

        // Grab next instruction
        const offset = Addresses.CODE.start + current_line;
        const opcode = this.read_byte(offset);

        const instruction = INSTRUCTIONS[opcode];
        if (!instruction) throw new Error(`Found invalid instruction ${hex(opcode)} at ${hex(offset)}!`);
        
        // Read arguments
        let read_offset = 1;
        
        const args = [];
        for (const arg of instruction.args) {
            const size = ARGUMENT_SIZES[arg];
            args.push(this[size === 1 ? "read_byte" : "read_word"](offset + read_offset));
            read_offset += size;
        }

        // Execute
        switch (instruction.opcode) {
            case "HLT":
                return;

            case "LDI":
                this.write_reg(args[0], args[1]);
                break;

            case "ADD":
                this.write_reg(args[0], this.read_reg(args[0]) + this.read_reg(args[1]));
                break;

            case "SUB":
                this.write_reg(args[0], this.read_reg(args[0]) - this.read_reg(args[1]));
                break;

            case "MUL":
                this.write_reg(args[0], this.read_reg(args[0]) * this.read_reg(args[1]));
                break;

            case "DIV":
                this.write_reg(args[0], Math.floor(this.read_reg(args[0]) / this.read_reg(args[1])));
                break;

            case "JMP":
                this.write_reg(0xA, args[0]);
                break;

            case "CAL":
                this.push_stack(this.read_reg(0xA) + read_offset);
                this.write_reg(0xA, args[0]);
                break;

            case "RET": {
                const return_line = this.pop_stack();
                if (return_line === -1) return;
                this.write_reg(0xA, return_line);
                break;
            }

            case "LBA":
            case "LBR":
            case "LWA":
            case "LWR": {
                let address = args[1];

                const data_size = instruction.opcode[1] === "B" ? 1 : 2;
                if (instruction.opcode[2] === "R") address = this.read_reg(address);

                this.write_reg(args[0], this[data_size === 1 ? "read_byte" : "read_word"](address));
                break;
            }

            case "SBA":
            case "SBR":
            case "SWA":
            case "SWR": {
                let address = args[1];

                const data_size = instruction.opcode[1] === "B" ? 1 : 2;
                if (instruction.opcode[2] === "R") address = this.read_reg(address);

                const value = this.read_reg(args[0]);
                this[data_size === 1 ? "write_byte" : "write_word"](address, value);
                break;
            }

            case "AND":
                this.write_reg(args[0], this.read_reg(args[0]) & this.read_reg(args[1]));
                break;

            case "OR":
                this.write_reg(args[0], this.read_reg(args[0]) | this.read_reg(args[1]));
                break;

            case "XOR":
                this.write_reg(args[0], this.read_reg(args[0]) ^ this.read_reg(args[1]));
                break;

            case "NOT":
                this.write_reg(args[0], ~this.read_reg(args[0]));
                break;

            case "SHL":
                this.write_reg(args[0], this.read_reg(args[0]) << this.read_reg(args[1]));
                break;

            case "SHR":
                this.write_reg(args[0], this.read_reg(args[0]) >> this.read_reg(args[1]));
                break;

            case "CMP": {
                const left = this.read_reg(args[0]);
                const right = this.read_reg(args[1]);
                this.write_reg(0xB, (left < right) ? 255 : (left > right) ? 1 : 0);
                break;
            }

            case "JEQ":
                if (this.read_reg(0xB) === 0) this.write_reg(0xA, args[0]);
                break;

            case "JNE":
                if (this.read_reg(0xB) !== 0) this.write_reg(0xA, args[0]);
                break;

            case "JGT":
                if (this.read_reg(0xB) === 1) this.write_reg(0xA, args[0]);
                break;

            case "JLT":
                if (this.read_reg(0xB) === 255) this.write_reg(0xA, args[0]);
                break;

            case "JGE":
                if (this.read_reg(0xB) === 1 || this.read_reg(0xB) === 0) this.write_reg(0xA, args[0]);
                break;

            case "JLE":
                if (this.read_reg(0xB) === 0 || this.read_reg(0xB) === 255) this.write_reg(0xA, args[0]);
                break;

            case "PSH":
                this.push_stack(this.read_reg(args[0]));
                break;

            case "POP":
                this.write_reg(args[0], Math.max(this.pop_stack(), 0));
                break;

            case "INC":
                this.write_reg(args[0], this.read_reg(args[0]) + 1);
                break;

            case "DEC":
                this.write_reg(args[0], this.read_reg(args[0]) - 1);
                break;

            case "MOV":
                this.write_reg(args[0], this.read_reg(args[1]));
                break;
        }

        // Auto advance
        const new_line = this.read_reg(0xA);
        if (current_line === new_line) {
            this.write_reg(0xA, new_line + read_offset);
        }
    }
}

document.getElementById("bin-input").addEventListener("change", async (e) => {
    const file = e.target.files[0];

    // Load waffle
    const waffle = new Waffle();
    waffle.load(new Uint8Array(await file.arrayBuffer()));

    // while (true) waffle.step();
    setInterval(() => waffle.step(), 1000);
});

// Terminal initialization
const terminal = new Terminal();
const addon = new FitAddon.FitAddon();
terminal.loadAddon(addon);
terminal.open(document.getElementById("console"));
addon.fit();
