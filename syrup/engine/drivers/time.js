// Copyright (c) 2026 iiPython

// Driver: time
// Purpose: Provide time related utilities to waffle
//
// Registers:
//   W SET_TIME_UNIT - Set item to read (see OPTIONS)
//   R READ_TIME     - Read currently selected item
//   W SET_TIME_FMT  - Set memory address of strftime string
//   W READ_TIME_FMT - Read time in strftime format to specified memory address
//   W SLEEP         - Sleep main thread for specified duration in milliseconds
//   W ZERO_CLOCK    - Set elapsed clock to zero
//   R READ_ELAPSED  - Read elapsed clock in requested unit (MONTH and YEAR unsupported)
//
// Options:
//   SET_TIME_UNIT -> 0: Millisecond
//   SET_TIME_UNIT -> 1: Second
//   SET_TIME_UNIT -> 2: Minute
//   SET_TIME_UNIT -> 3: Hour
//   SET_TIME_UNIT -> 4: Day
//   SET_TIME_UNIT -> 5: Month
//   SET_TIME_UNIT -> 6: Year

const WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

const ENCODER = new TextEncoder();
const DECODER = new TextDecoder();

export class TimeDriver {
    constructor(core, emit) {
        this.core = core;
        this.emit = emit;

        // Bindings
        core.bind("SET_TIME_UNIT", this.write_selection.bind(this),  "write");
        core.bind("READ_TIME",     this.read_selection.bind(this),   "read");
        core.bind("SET_TIME_FMT",  this.write_strftime.bind(this),   "write");
        core.bind("READ_TIME_FMT", this.read_strftime.bind(this),    "write");
        core.bind("SLEEP",         this.write_sleep.bind(this),      "write");
        core.bind("ZERO_CLOCK",    this.write_zero_clock.bind(this), "write");
        core.bind("READ_ELAPSED",  this.read_elapsed.bind(this),     "read");

        // State
        this.selection = 0;
        this.strftime_address = 0;
        this.elapsed_start = performance.now();
    }

    get now() { return new Date(); }

    write_selection(ram, value) { this.selection = value; }

    read_selection(ram) {
        const now = new Date();
        const units = [
            d => d.getMilliseconds(),
            d => d.getSeconds(),
            d => d.getMinutes(),
            d => d.getHours(),
            d => d.getDate(),
            d => d.getMonth() + 1,
            d => d.getFullYear()
        ];
        return units[this.selection]?.(now) ?? 0;
    }


    write_strftime(ram, value) { this.strftime_address = value; }

    read_cstring(ram, address) {
        const null_index = ram.indexOf(0, address);
        return DECODER.decode(ram.subarray(address, null_index !== -1 ? null_index : undefined));
    }

    format_strftime(format, date) {
        const pad = (v, w = 2) => String(v).padStart(w, "0");
        const replacements = {
            "%a": WEEKDAYS[date.getDay()].slice(0, 3),
            "%A": WEEKDAYS[date.getDay()],
            "%b": MONTHS[date.getMonth()].slice(0, 3),
            "%B": MONTHS[date.getMonth()],
            "%d": pad(date.getDate()),
            "%e": String(date.getDate()).padStart(2, " "),
            "%H": pad(date.getHours()),
            "%I": pad((date.getHours() % 12) || 12),
            "%m": pad(date.getMonth() + 1),
            "%M": pad(date.getMinutes()),
            "%p": date.getHours() < 12 ? "AM" : "PM",
            "%S": pad(date.getSeconds()),
            "%U": pad(this.weeknum(date, 7)),
            "%W": pad(this.weeknum(date, 8)),
            "%w": String(date.getDay()),
            "%y": pad(date.getFullYear() % 100),
            "%Y": String(date.getFullYear()),
            "%z": this.tzoffset(date),
            "%Z": this.timezone(date),
            "%%": "%"
        };
        return format.replace(/%[aAbBdeHjImMpSUwWyYzZ%]/g, token => replacements[token] ?? token);
    }

    weeknum(date, interval) {
        const start = new Date(date.getFullYear(), 0, 1);
        const day = new Date(start);
        day.setDate(start.getDate() + ((interval - start.getDay()) % 7));
        return date < day ? 0 : Math.floor((date - day) / 604800000) + 1;
    }

    tzoffset(date) {
        const offset = date.getTimezoneOffset();
        const abs = Math.abs(offset);
        return `${offset <= 0 ? "+" : "-"}${String(Math.floor(abs / 60)).padStart(2, "0")}${String(abs % 60).padStart(2, "0")}`;
    }

    timezone(date) {
        return date.toLocaleTimeString("en-US", { timeZoneName: "short" }).match(/[A-Z]{2,5}$/)?.[0] ?? "";  // Sometimes not available, ¯\_(ツ)_/¯
    }

    read_strftime(ram, value) {
        const format = this.read_cstring(ram, this.strftime_address);
        const output = this.format_strftime(format, new Date());
        const target = ram.subarray(value, ram.length - 1);
        const { written } = ENCODER.encodeInto(output, target);
        ram[value + written] = 0;
    }


    write_sleep(ram, value) {
        const end = performance.now() + value;
        while (performance.now() < end) {};
    }

    write_zero_clock(ram, value) { this.elapsed_start = performance.now(); }

    read_elapsed() {
        const divisors = [1, 1000, 60000, 3600000, 86400000];
        const div = divisors[this.selection];
        return div ? Math.floor((performance.now() - this.elapsed_start) / div) : 0;
    }
}
