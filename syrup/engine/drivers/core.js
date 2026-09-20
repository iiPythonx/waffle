// Copyright (c) 2026 iiPython

export class DriverManager {
    constructor(ram, driver_mappings) {
        this.ram = ram;
        this.driver_mappings = driver_mappings;

        // Hook into R/W
        this.read_map = new Map();
        this.write_map = new Map();
    }

    bind(name, callback, type) {
        const address = this.driver_mappings.get(name);
        if (!address) return;

        (type === "read" ? this.read_map : this.write_map).set(address, callback);
    }

    read(address) {
        const callback = this.read_map.get(address);
        return callback ? callback(this.ram) : undefined;
    }

    write(address, value) {
        const callback = this.write_map.get(address);
        if (!callback) return false;

        callback(this.ram, value);
        return true;
    }
}
