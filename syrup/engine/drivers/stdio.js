// Copyright (c) 2026 iiPython

// Driver: stdio
// Purpose: Provide general purpose I/O to waffle
//
// Registers:
//   W WRITE_CHR - Send a character to the screen
//   W WRITE_STR - Send a string to the screen from a memory address
//   W WRITE_INT - Send an integer to the screen
//   W CLEAR_SCR - Clear the entire screen and reset to home position
//   R READ_CHR  - Read one character from stdin and place in requested register
//   W READ_STR  - Read an entire string from stdin into memory at offset 0x2100

export class StdioDriver {
    constructor(core, emit) {
        this.core = core;
        this.emit = emit;

        // Bindings
        core.bind("WRITE_CHR", this.write_character.bind(this), "write");
        core.bind("WRITE_STR", this.write_string.bind(this),    "write");
        core.bind("WRITE_INT", this.write_integer.bind(this),   "write");
        core.bind("CLEAR_SCR", this.clear_screen.bind(this),    "write");
        core.bind("READ_CHR",  this.read_character.bind(this),  "read");
        core.bind("READ_STR",  this.read_string.bind(this),     "write");
    }

    write_character(ram, value) {
        this.emit("stdio_write", String.fromCharCode(value));
    }

    write_string(ram, value) {
        let output = "";
        for (let i = value; i < ram.length; i++) {
            const byte = ram[i];
            if (byte === 0) break;
            output += String.fromCharCode(byte);
        }
        this.emit("stdio_write", output);
    }

    write_integer(ram, value) {
        this.emit("stdio_write", value.toString());
    }

    clear_screen() {
        this.emit("stdio_wipe");
    }

    read_character() {
        console.log("read character");
        return 0;
    }

    read_string(ram, value) {
        console.log("read string");
    }
}
