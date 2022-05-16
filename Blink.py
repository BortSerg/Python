#!/usr/bin/sudo python3.10

import os
import re
import sys
import colorama
import time
import serial
import datetime


def read_serial_port(serial_port, logs):
    line = serial_port.readline().decode('utf-8')
    line = anti_esc(line)
    logs.write('[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ']' + ' ' + line)
    #print(line)
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
        file_name = "/Blink_" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"

    elif system == "win32":
        serial_port = serial.Serial("COM" + port, UART_SPEED)
        path_line = os.getcwd().split("\\")
        path = path_line[0] + "\\Log"
        file_name = "\Blink_" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"

    try:
        os.makedirs(path)
    except OSError as error:
        if "[WinError 183]" in str(error):
            print(f"Каталог {path} уже существует")
    return serial_port, path, system, file_name


def fibra_scan(serial_port, logs):
    dev_id_list = []
    serial_port.write("log j* 5\r\n".encode("UTF-8"))
    serial_port.write("fibra reset\r\n".encode("UTF-8"))  # контрольный сброс сканирования
    time_command = time.time()
    while abs(time.time() - time_command < 5.0):
        read_serial_port(serial_port, logs)

    serial_port.write("fibra scan\r\n".encode("UTF-8"))  # начать сканировиние шин
    while True:
        line = read_serial_port(serial_port, logs)
        if "Finish SCAN" in line:
            break


def show_dev(serial_port, logs):
    dev_id_list = []
    serial_port.write("show\r\n".encode("UTF-8"))
    while read_serial_port(serial_port, logs).split(" ")[0] not in {"Hub", "User", "Room", "Device"}:
        pass

    while True:
        line = read_serial_port(serial_port, logs)
        line_part = line.split(" ")
        if "Device" in line:
            print(colorama.Fore.YELLOW + line + colorama.Fore.RESET)
            dev_id_list.append(line_part[2])
        elif line_part[0] not in {"Hub", "User", "Room", "Device"}:
            break
    return dev_id_list


def blink_dev(serial_port, dev_id_list, logs, flag):
    counter = len(dev_id_list)
    for dev_id in dev_id_list:
        counter -= 1
        serial_port.write((f"fibra {flag} " + dev_id + "\r\n").encode("UTF-8"))
        time_command = time.time()
        while True:
            line = read_serial_port(serial_port, logs)
            if f"{dev_id};CMD=130" in line and (counter >= 0):
                if flag.upper() == "ON":
                    print(colorama.Fore.GREEN)
                elif flag.upper() == "OFF":
                    print(colorama.Fore.RED)
                print("Blink  %s %s" % (flag.upper(), dev_id) + colorama.Fore.RESET)

                while time.time() - time_command < 2.0:
                    read_serial_port(serial_port, logs)
                break

def clear_screen(os_system):
    if (os_system == "linux") or (os_system == "linux2"):
        os.system('clear')
    if os_system == "win32":
        os.system('cls')


def main():
    print(sys.version)
    port = input("Ведите номер порта: ")
    serial_port, path, system, file_name = set_os_port_path(port, 115200)

    with open(path + file_name, 'w') as logs:
        fibra_scan(serial_port, logs)
        dev_id_list = show_dev(serial_port, logs)

        for a in range(2):
            blink_dev(serial_port, dev_id_list, logs, "on")
            blink_dev(serial_port, dev_id_list, logs, "off")

        blink_dev(serial_port, dev_id_list, logs, "on")
        serial_port.write("fibra reset\r\n".encode("UTF-8"))

    logs.close()
    serial_port.close()


if __name__ == '__main__':
    main()
