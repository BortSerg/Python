#!/usr/bin/sudo python3.10

import re
import os
import sys
import time
import serial
import datetime


dev_list = []


def save_log(serialport, fname, path):
    with open(path + fname, 'w') as logs:  # если для винды, то (r'path')
        finish_scan = "Finish SCAN"

        while True:
            line = read_serial_data(serialport, logs)
            if finish_scan in line:
                time.sleep(3)
                show_devices(serialport, logs)
                break
        logs.close()


def show_devices(serialport, logs):
    serialport.write("show\r\n".encode("UTF-8"))  # вывести девайсы на хабе
    while read_serial_data(serialport, logs).split(" ")[0] not in {"Hub", "User", "Room", "Device"}:
        pass

    while True:
        console_line = read_serial_data(serialport, logs)
        if "Device" in console_line:
            _, dev_type, dev_id, *_ = console_line.split(" ")
            dev_list.append((dev_type, dev_id))
        else:
            if console_line.split(" ")[0] not in {"Hub", "User", "Room", "Device"}:
                break


def add_device(serialport, fname, dev_type, path):
    with open(path + fname, 'a') as logs:

        # serialport.write("jwl3 add {} {}" .format(dev_list[0][0], dev_list[0][1]))
        for dev in dev_list:
            if dev_type == "FF" or dev[0] == dev_type:
                serialport.write(f"jwl3 add {dev[0]} {dev[1]}\r\n".encode("UTF-8"))

                while True:
                    console_line = read_serial_data(serialport, logs)
                    if f"{dev[1]};CMD=20;" in console_line:
                        break
        logs.close()


def read_serial_data(serialport, logs):  # чтение UART и запись в лог файл
    line = serialport.readline().decode('utf-8')
    line = anti_esc(line)
    logs.write('[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ']' + ' ' + line)
    print(line)
    return line


def anti_esc(line):  # фильтр "мусора"
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    line = ansi_escape.sub('', line).replace('>\r', '>')
    return line


def set_os_port_path(port, UART_SPEED):
    system = sys.platform
    if (system == "linux") or (system == "linux2"):

        serial_port = serial.Serial("/dev/ttyUSB" + port, UART_SPEED)
        path_line = os.getcwd().split("/")
        path = "/" + str(path_line[1]) + "/" + str(path_line[2]) + "/Log"
        file_name = "/FibraScan_" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"

    elif system == "win32":
        serial_port = serial.Serial("COM" + port, UART_SPEED)
        path_line = os.getcwd().split("\\")
        path = path_line[0] + "\\Log"
        file_name = "\FibraScan_" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"

    try:
        os.makedirs(path)
    except OSError as error:
        if "[WinError 183]" in str(error):
            print(f"Каталог {path} уже существует")
    return serial_port, path, system, file_name


def main():
    uart_speed = 115200

    port = input("Введите номер порта: ")
    serial_port, path, system, file_name = set_os_port_path(port, uart_speed)

    print('введите тип девайса FIBRA для добавления.')
    dev_type = input('для добавления всех отсканеных девайсов ввести FF: ')

    if dev_type not in {"61", "62", "64", "68", "6A", "6D", "6E", "6F", "74", "75", "7C", "FF"}:
        raise "Incorrect device type! Try again"
    else:
        serial_port.write("log j* 5\r\n".encode("UTF-8"))
        serial_port.write("fibra reset\r\n".encode("UTF-8"))  # контрольный сброс сканирования
        time.sleep(1)
        serial_port.write("fibra scan\r\n".encode("UTF-8"))  # начать сканировиние шин

        save_log(serial_port, file_name, path)

        add_device(serial_port, file_name, dev_type, path)

        serial_port.write("fibra reset\r\n".encode("UTF-8"))  # начать сканировиние шин
        serial_port.close()


if __name__ == '__main__':
    main()
