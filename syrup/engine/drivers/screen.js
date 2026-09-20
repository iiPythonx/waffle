// Copyright (c) 2026 iiPython

// Driver: screen
// Purpose: Provide a 400x400 screen to waffle

export class ScreenDriver {
    constructor(core, emit) {
        this.core = core;
        this.emit = emit;

        // Bindings
        core.bind("SCR_SET_X", this.set_x.bind(this), "write");
        core.bind("SCR_SET_Y", this.set_y.bind(this), "write");
        core.bind("SCR_SET_R", this.set_r.bind(this), "write");
        core.bind("SCR_SET_G", this.set_g.bind(this), "write");
        core.bind("SCR_SET_B", this.set_b.bind(this), "write");
        core.bind("SCR_SET_A", this.set_a.bind(this), "write");
        core.bind("SCR_PAINT", this.paint.bind(this), "write");

        // State
        this.state = {
            x: 0,
            y: 0,
            r: 0,
            g: 0,
            b: 0,
            a: 255
        };
    }

    set_x(ram, value) { this.state.x = value <= 399 ? value : 399; }
    set_y(ram, value) { this.state.y = value <= 399 ? value : 399; }
    set_r(ram, value) { this.state.r = value <= 255 ? value : 255; }
    set_g(ram, value) { this.state.g = value <= 255 ? value : 255; }
    set_b(ram, value) { this.state.b = value <= 255 ? value : 255; }
    set_a(ram, value) { this.state.a = value <= 255 ? value : 255; }
    paint(ram, value) { this.emit("screen_paint", this.state); }
}
