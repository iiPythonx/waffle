# Copyright (c) 2026 iiPython

# Driver: network
# Purpose: Provide networking capabilities to 8255

import socket
from x8255.vm.drivers import DriverManager

class Driver:
    def __init__(self, core: DriverManager) -> None:
        core.bind_write("SELECT_NET_VARIABLE", 0x0070, self.set_variable)
        core.bind_write( "WRITE_NET_VARIABLE", 0x0072, self.write_variable)
        core.bind_write(      "CREATE_SOCKET", 0x0074, self.create_socket)
        core.bind_write(       "CLOSE_SOCKET", 0x0076, self.close_socket)
        core.bind_write(           "NET_SEND", 0x0078, self.send_packet)
        core.bind_read(         "NET_RECEIVE", 0x007A, self.receive)

        # State
        self.socket: socket.socket | None = None

        # Variables
        self.variables: dict[str, int] = {}
        self.variable_active: str | None = None
        self.variable_mapping: dict[int, str] = {
            1: "socket_family",
            2: "socket_type",
            3: "socket_protocol",
            4: "packet_address",
            5: "packet_size",
            6: "target_host_address",
            7: "target_port",
            8: "receive_address",
            9: "receive_size"
        }

    def set_variable(self, memory: bytearray, value: int) -> None:
        if value in self.variable_mapping:
            self.variable_active = self.variable_mapping[value]

    def write_variable(self, memory: bytearray, value: int) -> None:
        if self.variable_active is not None:
            self.variables[self.variable_active] = value

    def create_socket(self, memory: bytearray, value: int) -> None:
        self.socket = socket.socket(
            self.variables["socket_family"],
            self.variables["socket_type"],
            self.variables["socket_protocol"]
        )

    def send_packet(self, memory: bytearray, value: int) -> None:
        if self.socket is None:
            return

        # Sanity checking
        for v in {"target_host_address", "target_port", "packet_address", "packet_size"}:
            if v not in self.variables:
                return

        target_host = memory[self.variables["target_host_address"]:].split(b"\0")[0].decode()
        target_port = self.variables["target_port"]

        # Send packet to host
        address = self.variables["packet_address"]
        self.socket.sendto(
            memory[address:address + self.variables["packet_size"]],
            (target_host, target_port)
        )

    def receive(self, memory: bytearray) -> int:
        if self.socket is not None and "receive_address" in self.variables:
            packet = self.socket.recv(self.variables.get("receive_size", 1024))

            # Save to memory at chosen address
            address = self.variables["receive_address"]
            memory[address:address + len(packet)] = packet

            # Return length of received data
            return len(packet)
        
        return 0

    def close_socket(self, memory: bytearray, value: int) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None
