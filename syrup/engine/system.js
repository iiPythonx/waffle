// Copyright (c) 2026 iiPython

// Utilities
const hex = (n) => `0x${n.toString(16).padStart(4, "0")}`;

// Terminal initialization
const terminal = new Terminal({ convertEol: true });
const addon = new FitAddon.FitAddon();
terminal.loadAddon(addon);
terminal.open(document.getElementById("console"));
addon.fit();

const instruction_div = document.getElementById("instruction-log");

// Handle waffle
const worker = new Worker(new URL("./worker.js", import.meta.url), { type: "module" });
worker.addEventListener("message", (e) => {
    const { type, data } = e.data;
    switch (type) {
        case "stdio_write":
            terminal.write(data);
            break;

        case "waffle_instruction_log":
            const { offset, instruction, args } = data;

            const fragment = document.createDocumentFragment();
            const div = document.createElement("div");
            div.innerHTML = `
                <span class = "hex-offset">${hex(offset)}</span> |
                <span class = "instruction">${instruction.opcode}</span> 
                <span class = "hex-arg">${args.map(a => hex(a)).join(" ")}</span>
            `;
            fragment.appendChild(div);

            instruction_div.appendChild(fragment);
            instruction_div.scrollTop = instruction_div.scrollHeight;

            break;

        case "waffle_register_update":
            for (const [k, v] of Object.entries(data)) document.getElementById(`r-${k}`).innerText = v;
            break;
    }
});

document.getElementById("bin-input").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    worker.postMessage({ type: "LOAD", data: new Uint8Array(await file.arrayBuffer()) });

    // Setup new buttons
    const section = document.getElementById("section-control");
    section.innerHTML = `
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

    document.getElementById("btn-stop").addEventListener("click", () => {
        worker.postMessage({ type: "STOP" });
        instruction_div.innerHTML = "";
        document.getElementById("mode").innerText = "MANUAL";
    });

    document.getElementById("btn-start").addEventListener("click", () => {
        worker.postMessage({ type: "START" });
        instruction_div.innerHTML = "<span>Not available in live mode.</span>";
        document.getElementById("mode").innerText = "AUTO";
    });

    document.getElementById("btn-step").addEventListener("click", () => {
        worker.postMessage({ type: "STEP" });
    });
});
