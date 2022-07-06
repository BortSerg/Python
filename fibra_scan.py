#!/usr/bin/sudo python3

from my_logging import Logging
from colorama import Fore
from time import time


def show_devises(obj: Logging, list):
    obj.write_serial("show")
    while True:
        if "show" in obj.write_log():
            break

    while True:
        console_line = obj.write_log()
        if "Device" in console_line:
            _, dev_type, dev_id, *_ = console_line.split(" ")[2:]
            list.append((dev_type, dev_id))
        else:
            if console_line.split(" ")[2] not in {"Hub", "User", "Room", "Device"}:
                break


def wait(obj: Logging):
    time_start = int(time())
    while True:
        obj.write_log()
        if int(time() - time_start) > 2:
            break


def add_device(obj: Logging,  added_list, type):  # added_list - список с устройствами на хабе до скана; scan_list - список после скана
    scan_list = []
    finish_scan = "Finish SCAN"

    obj.write_serial("fibra reset")
    wait(obj)
    obj.write_serial("fibra scan")
    wait(obj)

    while True:                     # отслеживание конца сканирования
        line = obj.write_log()
        if finish_scan in line:
            break

    show_devises(obj, scan_list)    # получаем список устройств после скана

    for i in scan_list:             # удаляем повторы
        for a in added_list:
            if i == a:
                scan_list.remove(a)

    for dev in scan_list:
        if type == "FF" or dev[0] == type:
            obj.write_serial(f"jwl3 add {dev[0]} {dev[1]}")
            while True:
                console_line = obj.write_log()
                if f"{dev[1]};CMD=20;" in console_line:
                    break

                if f"Registration finished for {dev[1]} with result = 1" in console_line:
                    print(Fore.RED + f"Registration {dev[1]} is FALSE" + Fore.RESET)
                    break
    obj.write_serial("fibra reset")


def main():
    added_dev_list = []
    port = input('Введите номер порта: ')
    hub = Logging(port, 115200)
    hub.prefix_name_log_file = "FibraScan"

    print('введите тип девайса FIBRA для добавления.')
    dev_type = input('для добавления всех отсканеных девайсов ввести FF: ')

    if dev_type not in {"61", "62", "64", "68", "6A", "6D", "6E", "6F", "74", "75", "7C", "FF"}:
        raise "Incorrect device type! Try again"
    else:
        print(hub.get_path_log_file(), hub.get_name_log_file())
        hub.write_serial("log j* 5")
        hub.print_data = True
        show_devises(hub, added_dev_list)   # показать девайсы что уже есть на хабе и запомнить их
        add_device(hub, added_dev_list, dev_type)


if __name__ == "__main__":
    main()