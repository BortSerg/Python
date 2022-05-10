#!/usr/bin/sudo python3.9
import re
import datetime
import serial
import sys
import colorama
import os
import keyboard

UART_SPEED = 115200


def anti_esc(line):  # фильтр "мусора"
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    line = ansi_escape.sub('', line).replace('>\r', '>')
    return line


def read_serial_port(serial_port, logs):
    line = serial_port.readline().decode('utf-8')
    line = anti_esc(line)
    logs.write('[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ']' + ' ' + line)
    print(line)
    return line

def check_delete_dev(line, id_dev_arr, frame):
    if "05 DEV_REG 05 050635 05" in line:
        line_parts = line.split(" ")
        dev_id = line_parts[13]
        for idx in enumerate(id_dev_arr):
            if dev_id in id_dev_arr[idx]:
                id_dev_arr.pop([idx])
        clear_screen()
        show_statistic(id_dev_arr, frame)



def check_add_new_dev(line, id_dev_arr, frame):
    if "CMD=14" in line:
        line_parts = line.split(";")
        id_dev = line_parts[3]
        dev_data = [id_dev, "CMD[20] = NO", 0, 0, 0, 0]
        id_dev_arr.append(dev_data)
        clear_screen()
        show_statistic(id_dev_arr, frame)


def get_hub_dev_id(serial_port, logs):
    serial_port.write("show\r\n".encode("UTF-8"))  # вывод списка устройств на хабе
    read_serial_port(serial_port, logs)
    id_dev_arr = []
    hub_id = None  # заменить на то что будет по умолчанию

    while True:
        line = read_serial_port(serial_port, logs)
        line_parts = line.split(" ")
        if "Hub" in line:
            hub_id = line_parts[5]
        if "Device" in line:
            id_dev_arr.append([line_parts[2], colorama.Fore.RED + "CMD[20] = NO" + colorama.Fore.RESET, 0, 0, 0, 0])  # dev id, CMD=20, 15s pack, 30s pack, 60s pack, last time recv
        if line_parts[0] not in {"Hub", "User", "Room", "Device"}:
            break
    return hub_id, id_dev_arr


def check_change_frame(line, hub_id):
    write_param = "WRITE_PARAM 21 0521 05" + hub_id + " 0538"
    if write_param in line:
        sub_line = line.split(" ")
        frame = sub_line[18][2:]
        print(colorama.Fore.GREEN + "Фрейм: " + str(int(frame, 16)) + colorama.Fore.RESET)
        return int(frame, 16)
    else:
        return 0


def check_GoToFindSynchro(line, id_dev_arr, frame):
    if "CMD=20" in line:
        line_parts = line.split(";")
        dev_id = line_parts[3]
        for idx, dev_data in enumerate(id_dev_arr):
            _dev_id_, *_ = dev_data
            if dev_id == _dev_id_:
                temp_data = [dev_id, colorama.Fore.GREEN + "CMD[20] = OK" + colorama.Fore.RESET, 0, 0, 0, 0]
                id_dev_arr[idx] = temp_data
                clear_screen()
                show_statistic(id_dev_arr, frame)


def count_CheckSynchro(line, id_dev_arr, frame):
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
                clear_screen()
                show_statistic(id_dev_arr, frame)


def show_statistic(id_dev_arr, frame):
    print(colorama.Fore.GREEN + "Фрейм: " + str(frame) + colorama.Fore.RESET)
    for dev_data in enumerate(id_dev_arr):
        print(str(dev_data[0]) + " " + dev_data[1][0] + " " + str(dev_data[1][1]) + " " + str(dev_data[1][2]) + " " + str(dev_data[1][3]) + " " + str(dev_data[1][4]))

    print("\nFor exit press CTRL+Z")


def reset_statistic(id_dev_arr):
    for idx, dev_data in enumerate(id_dev_arr):
        _dev_id_, *_ = dev_data
        dev_data = [_dev_id_, colorama.Fore.RED + "CMD[20] = NO" + colorama.Fore.RESET, 0, 0, 0, 0]
        id_dev_arr[idx] = dev_data


def clear_screen():
    os.system('clear')


def main():
    port = input("Введите номер порта: ")
    if sys.platform == "linux" or "linux2":
        serial_port = serial.Serial("/dev/ttyUSB" + port, UART_SPEED)
    elif sys.platform == "win32":
        serial_port = serial.Serial("COM" + port, UART_SPEED)

    with open('/home/user/Log/PowerTest_' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.txt',
              'w') as logs:  # если для винды, то (r'path')
        hub_id, id_dev_arr = get_hub_dev_id(serial_port, logs)
        frame = 0

        while True:
            line = read_serial_port(serial_port, logs)
            f = check_change_frame(line, hub_id)

            if f != 0:
                frame = f
                reset_statistic(id_dev_arr)

            check_GoToFindSynchro(line, id_dev_arr, frame)
            count_CheckSynchro(line, id_dev_arr, frame)
            check_add_new_dev(line, id_dev_arr, frame)
            check_delete_dev(line, id_dev_arr, frame)
            """
            if keyboard.is_pressed('ctrl+z'):
                break
            """
        logs.close()
    serial_port.close()


if __name__ == '__main__':
    main()
