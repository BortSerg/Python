from serial_data_read import *
from time import time
from colorama import Fore
from sys import exit


def get_info(hub: SerialDataRead):
    hub.write_serial_data("show")
    while True:
        if "show" in hub.read_serial_data():
            break

    socket_id = None
    relay_id_low = None
    relay_id_norm = None
    hub_name = None
    hub_id = None
    exit_flag = False

    while True:
        line = hub.read_serial_data()
        line_parts = line.split(" ")
        if "Hub" in line:
            hub_name = ''
            for i in line_parts[6:]:
                hub_name += i
            hub_name = hub_name[:-1]
            hub_id = line_parts[5]

        if "Device 1E" in line:
            socket_id = line_parts[2][2:].upper()

        if "Device 12" in line:
            # smth = line_parts[3].upper()
            if "LOW" in line_parts[3].upper():
                relay_id_low = line_parts[2][2:].upper()
            if "NOR" in line_parts[3].upper():
                relay_id_norm = line_parts[2][2:].upper()

        if line_parts[0] not in {"Hub", "User", "Room", "Device"}:
            break

    conditions = (socket_id, relay_id_low, relay_id_norm)
    descriptions = [
        "Error socket_id! Please add a socket",
        "Error relay_id_low! Please add a relay and name it 'LOW'",
        "Error socket_id! Please add a socket"
    ]

    for cond, descr in zip(conditions, descriptions):
        if cond is None:
            exit_flag = True
            print(descr)

    if exit_flag:
        print(Fore.YELLOW + "Check if the socket and relay are added to the hub" + Fore.RESET)
        exit(0)

    return hub_name, hub_id, socket_id, relay_id_norm, relay_id_low


def relay_on(hub: SerialDataRead, relay_id):
    hub.write_serial_data(f"jwl3 ws {relay_id} 1")
    waiter(hub, relay_id)


def relay_off(hub: SerialDataRead, relay_id):
    hub.write_serial_data(f"jwl3 ws {relay_id} 2")
    waiter(hub, relay_id)


def socket_on(hub: SerialDataRead, socket_id):
    hub.write_serial_data(f"jwl3 ws {socket_id} 1")
    waiter(hub, socket_id)


def socket_off(hub: SerialDataRead, socket_id):
    hub.write_serial_data(f"jwl3 ws {socket_id} 2")
    waiter(hub, socket_id)


def waiter(hub: SerialDataRead, dev_id):
    time_command = None
    while True:
        line = hub.read_serial_data()
        if f"{dev_id};CMD=105" in line:
            time_command = int(time())

        if time_command is not None:
            if int(time()) - time_command > 5:
                break


def main():
    hub = SerialDataRead()
    port = input("Номер порта: ")
    hub.set_serial_port(port, 115200)
    get_info(hub)


if __name__ == '__main__':
    main()
