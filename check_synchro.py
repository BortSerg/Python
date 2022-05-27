#!/usr/bin/sudo python3.10
from my_serialdata import Hub
from colorama import Fore
from datetime import datetime
import keyboard


def check_delete_dev(obj: Hub, line, id_dev_arr, frame):
    if "05 DEV_REG 05 050635 05" in line:
        line_parts = line.split(" ")
        dev_id = line_parts[16][2:]
        for idx, element in enumerate(id_dev_arr):
            if dev_id in element:
                id_dev_arr.pop(idx)
        obj.clear_console()
        show_statistic(id_dev_arr, frame)


def check_add_new_dev(obj: Hub, line, id_dev_arr, frame):
    if "CMD=14" in line:
        line_parts = line.split(";")
        id_dev = line_parts[3]
        dev_data = [id_dev, Fore.RED + "CMD[20]" + Fore.RESET, 0, 0, 0, 0]
        duplicate = False
        for element in id_dev_arr:
            if id_dev in element:
                duplicate = True
        if not duplicate:
            id_dev_arr.append(dev_data)
            obj.clear_console()
        show_statistic(id_dev_arr, frame)


def get_hub_dev_id(obj: Hub):
    obj.write_serial("show")  # вывод списка устройств на хабе
    obj.read_serial()

    id_dev_arr = []

    while True:
        line = obj.read_serial()
        line_parts = line.split(" ")
        if "Hub" in line:
            obj.hub_id = line_parts[5]
        if "Device" in line:
            id_dev_arr.append([line_parts[2], Fore.RED + "CMD[20]" + Fore.RESET, 0, 0, 0, 0])  # dev id, CMD=20, 15s pack, 30s pack, 60s pack, last time recv
        if line_parts[0] not in {"Hub", "User", "Room", "Device"}:
            break
    show_statistic(id_dev_arr, 0)
    return id_dev_arr


def check_change_frame(obj: Hub, line):
    write_param = f"WRITE_PARAM 21 0521 05{str(obj.hub_id)} 0538"
    if write_param in line:
        sub_line = line.split(" ")
        frame = sub_line[18][2:]
        #print(Fore.GREEN + f"Фрейм: {str(int(frame, 16))}" + Fore.RESET)
        return int(frame, 16)
    else:
        return 0


def check_GoToFindSynchro(obj: Hub, line, id_dev_arr, frame):
    if "CMD=20" in line:
        line_parts = line.split(";")
        dev_id = line_parts[3]
        for idx, dev_data in enumerate(id_dev_arr):
            _dev_id_, *_ = dev_data
            if dev_id == _dev_id_:
                temp_data = [dev_id, Fore.GREEN + "CMD[20]" + Fore.RESET, 0, 0, 0, 0]
                id_dev_arr[idx] = temp_data
                obj.clear_console()
                show_statistic(id_dev_arr, frame)


def count_CheckSynchro(obj: Hub, line, id_dev_arr, frame):
    if "CMD=23" in line:
        line_parts = line.split(";")
        dev_id = line_parts[3]
        time_recv = int(line_parts[18])
        for idx, dev_data in enumerate(id_dev_arr):
            _dev_id_, _cmd_status_, _time_15_count, _time_30_count, _time_60_count, _last_recv_ = dev_data

            if dev_id == _dev_id_:
                if _last_recv_ <= 0:
                    _time_15_count += 1
                    _last_recv_ = int(time_recv)
                else:
                    if (time_recv - _last_recv_ > 14000) and (time_recv - _last_recv_ < 16000):
                        _time_15_count += 1
                        _last_recv_ = int(time_recv)
                    if (time_recv - _last_recv_ > 29000) and (time_recv - _last_recv_ < 31000):
                        _time_30_count += 1
                        _last_recv_ = int(time_recv)
                    if (time_recv - _last_recv_ > 59000) and (time_recv - _last_recv_ < 61000):
                        _time_60_count += 1
                        _last_recv_ = int(time_recv)
                dev_data = _dev_id_, _cmd_status_, _time_15_count, _time_30_count, _time_60_count, _last_recv_
                id_dev_arr[idx] = dev_data
                obj.clear_console()
                show_statistic(id_dev_arr, frame)


def show_statistic(id_dev_arr, frame):
    print(Fore.GREEN + f"Фрейм: {frame}" + Fore.RESET)
    for dev_data in id_dev_arr:
        _dev_id_, _cmd_status_, _time_15_count_, _time_30_count_, _time_60_count_, _last_recv_ = dev_data
        print(f"{_dev_id_} {_cmd_status_} {_time_15_count_} {_time_30_count_} {_time_60_count_}")

    print("\nFor exit press CTRL+Z")


def reset_statistic(id_dev_arr):
    for idx, dev_data in enumerate(id_dev_arr):
        _dev_id_, *_ = dev_data
        dev_data = [_dev_id_, Fore.RED + "CMD[20]" + Fore.RESET, 0, 0, 0, 0]
        id_dev_arr[idx] = dev_data


def main():
    port = input("Введите номер порта: ")
    hub = Hub()
    hub.crete_log_file(f"CheckSynchro {datetime.now()}")
    hub.set_serial_port(port, 115200)
    id_dev_arr = get_hub_dev_id(hub)
    frame = 0

    while True:
        line = hub.read_serial()
        f = check_change_frame(hub, line)

        if f != 0:
            frame = f
            reset_statistic(id_dev_arr)
            hub.clear_console()
            show_statistic(id_dev_arr, frame)
        check_add_new_dev(hub, line, id_dev_arr, frame)
        check_GoToFindSynchro(hub, line, id_dev_arr, frame)
        count_CheckSynchro(hub, line, id_dev_arr, frame)
        check_delete_dev(hub, line, id_dev_arr, frame)

        if keyboard.is_pressed('ctrl+z'):
           break

    hub.close_port()


if __name__ == '__main__':
    main()
