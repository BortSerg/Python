#!/usr/bin/sudo python3.10

from colorama import Fore
from time import time
from my_serialdata import Hub
from datetime import datetime


def fibra_scan(obj: Hub):
    dev_id_list = []
    obj.write_serial("log j* 5")
    obj.write_serial("fibra reset")
    time_command = int(time())
    while int(time()) - time_command < 2:
        obj.read_serial()

    obj.write_serial("fibra scan")  # начать сканировиние шин
    while True:
        line = obj.read_serial()
        if "Finish SCAN" in line:
            break


def show_dev(obj: Hub):
    dev_id_list = []
    obj.write_serial("show")
    while obj.read_serial().split(" ")[0] not in {"Hub", "User", "Room", "Device"}:
        pass

    while True:
        line = obj.read_serial()
        line_part = line.split(" ")
        if "Device" in line:
            print(Fore.YELLOW + line + Fore.RESET)
            dev_id_list.append(line_part[2])
        elif line_part[0] not in {"Hub", "User", "Room", "Device"}:
            break
    return dev_id_list


def blink_dev(obj: Hub, dev_id_list, flag):
    counter = len(dev_id_list)
    for dev_id in dev_id_list:
        counter -= 1
        obj.write_serial(f"fibra {flag} {dev_id}")
        time_command = int(time())
        while True:
            line = obj.read_serial()
            if f"{dev_id};CMD=130" in line and (counter >= 0):
                if flag.upper() == "ON":
                    print(Fore.GREEN)
                elif flag.upper() == "OFF":
                    print(Fore.RED)
                print(f"Blink  {flag.upper()} {dev_id}" + Fore.RESET)

                while int(time()) - time_command < 2:
                    obj.read_serial()
                break


def main():
    hub = Hub()
    port = input("Ведите номер порта: ")
    hub.set_serial_port(port, 115200)
    hub.crete_log_file(f"Blink {datetime.now()}")
    print(hub.get_path_log_file(), hub.get_name_log_file())

    fibra_scan(hub)
    dev_id_list = show_dev(hub)

    for a in range(2):
        blink_dev(hub, dev_id_list, "on")
        blink_dev(hub, dev_id_list, "off")

    blink_dev(hub, dev_id_list, "on")
    hub.write_serial("fibra reset")

    hub.close_port()


if __name__ == '__main__':
    main()
