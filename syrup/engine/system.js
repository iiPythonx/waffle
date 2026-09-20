// Copyright (c) 2026 iiPython

// Utilities
const hex = (n) => `0x${n.toString(16).padStart(4, "0")}`;

// Track DOM
const DOM = {
    console: document.getElementById("console"),
    instructionLog: document.getElementById("instruction-log"),
    binInput: document.getElementById("bin-input"),
    sectionControl: document.getElementById("section-control"),
    canvas: document.querySelector("canvas")
};

// Begin caching canvas
const context = DOM.canvas.getContext("2d");
const pixel = context.createImageData(1, 1);

// Terminal initialization
const terminal = new Terminal({ convertEol: true });
const addon = new FitAddon.FitAddon();
terminal.loadAddon(addon);
terminal.open(DOM.console);
addon.fit();

// Handlers
const handlers = {
    stdio_write(data) {
        terminal.write(data);
    },

    screen_paint({ r, g, b, a, x, y }) {
        if (!context) return;
        const d = pixel.data;
        d[0] = r; d[1] = g; d[2] = b; d[3] = a;
        console.log(x, y);
        context.putImageData(pixel, x, y);
    },

    waffle_instruction_log({ offset, instruction, args }) {
        const div = document.createElement("div");

        const offset_elem = document.createElement("span");
        offset_elem.className = "hex-offset";
        offset_elem.textContent = hex(offset);

        const instruction_elem = document.createElement("span");
        instruction_elem.className = "instruction";
        instruction_elem.textContent = instruction.opcode;

        const argument_element = document.createElement("span");
        argument_element.className = "hex-arg";
        argument_element.textContent = args.map(hex).join(" ");

        div.append(offset_elem, " | ", instruction_elem, " ", argument_element);

        DOM.instructionLog.appendChild(div);
        DOM.instructionLog.scrollTop = DOM.instructionLog.scrollHeight;
    },

    waffle_register_update(data) {
        for (const [k, v] of Object.entries(data)) document.getElementById(`r-${k}`).innerText = v;
    }
};

// Handle waffle
const worker = new Worker(new URL("./worker.js", import.meta.url), { type: "module" });
worker.addEventListener("message", (e) => {
    const { type, data } = e.data;
    handlers[type](data);
});

// UI
const CONTROL_TEMPLATE = `
    <h3>Control</h3>
    <button id = "btn-stop"><img src = "/assets/icons/pause.svg"> Stop</button>
    <button id = "btn-start"><img src = "/assets/icons/play.svg"> Start</button>
    <button id = "btn-step"><img src = "/assets/icons/code.svg"> Step</button>
    <span>Mode: <b id = "mode">MANUAL</b></span>
    <span>
        R1: <span id = "r-1">0</span> | 
        R2: <span id = "r-2">0</span> | 
        R3: <span id = "r-3">0</span> | 
        R4: <span id = "r-4">0</span> | 
        R5: <span id = "r-5">0</span> | 
        R6: <span id = "r-6">0</span>
    </span>
    <span>
        R7: <span id = "r-7">0</span> | 
        R8: <span id = "r-8">0</span> | 
        R9: <span id = "r-9">0</span> | 
        LC: <span id = "r-lc">0</span> | 
        CR: <span id = "r-cr">0</span> | 
        SP: <span id = "r-sp">0</span>
    </span>
`;

DOM.binInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    worker.postMessage({ type: "LOAD", data: new Uint8Array(await file.arrayBuffer()) });

    // Setup new buttons
    const section = document.getElementById("section-control");
    section.innerHTML = CONTROL_TEMPLATE;

    document.getElementById("btn-stop").addEventListener("click", () => {
        worker.postMessage({ type: "STOP" });
        DOM.instructionLog.innerHTML = "";
        document.getElementById("mode").innerText = "MANUAL";
    });

    document.getElementById("btn-start").addEventListener("click", () => {
        worker.postMessage({ type: "START" });
        DOM.instructionLog.innerHTML = "<span>Not available in live mode.</span>";
        document.getElementById("mode").innerText = "AUTO";
    });

    document.getElementById("btn-step").addEventListener("click", () => {
        worker.postMessage({ type: "STEP" });
    });
});
