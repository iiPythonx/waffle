// Copyright (c) 2026 iiPython

import { Waffle } from "./lib/waffle.js";

let waffle = null;

const emit = (type, data) => self.postMessage({ type, data });

self.addEventListener("message", async (e) => {
    const { type, data } = e.data;
    if (type === "LOAD") {
        waffle = new Waffle(emit);
        waffle.set_live(false);
        waffle.load(data);
    } else if (type === "START" && !waffle.live) {
        waffle.set_live(true);
        run();
    } else if (type === "STOP") {
        waffle.set_live(false);
    } else if (type === "STEP") {
        waffle.step();
    }
});

function run() {
    if (!waffle.live || !waffle) return;

    const start = performance.now();
    while (waffle.live && (performance.now() - start < 12)) {
        for (let i = 0; i < 50; i++) {
            if (waffle.step() === false) {
                waffle.set_live(false);
                return;
            }
        }
    }

    if (waffle.live) setTimeout(run, 0);
}