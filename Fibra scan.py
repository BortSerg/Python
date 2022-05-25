#!/usr/bin/sudo python3.10
import re
import os
import sys
import time
import serial
import datetime
import colorama

added_dev_list = []


def show_devices(serialport, logs, list):
    serialport.write("show\r\n".encode("UTF-8"))  # вывести девайсы на хабе
    while read_serial_data(serialport, logs).split(" ")[0] not in {"Hub", "User", "Room", "Device"}:
        pass

    while True:
        console_line = read_serial_data(serialport, logs)
        if "Device" in console_line:
            _, dev_type, dev_id, *_ = console_line.split(" ")
            list.append((dev_type, dev_id))
        else:
            if console_line.split(" ")[0] not in {"Hub", "User", "Room", "Device"}:
                break


def add_device(serialport, logs, added_list, type):    # added_list - список с устройствами на хабе до скана; scan_list - список после скана
    scan_list = []
    finish_scan = "Finish SCAN"
    while True: # отслеживание конца сканирования
        line = read_serial_data(serialport, logs)
        if finish_scan in line:
            break

    show_devices(serialport, logs, scan_list)   # получаем список устройств после скана

    for i in scan_list: # удаляем повторы
        for a in added_list:
            if i == a:
                scan_list.remove(a)

    # serialport.write("jwl3 add {} {}" .format(dev_list[0][0], dev_list[0][1]))
    for dev in scan_list:
        if type == "FF" or dev[0] == type:
            serialport.write(f"jwl3 add {dev[0]} {dev[1]}\r\n".encode("UTF-8"))

            while True:
                console_line = read_serial_data(serialport, logs)
                if f"{dev[1]};CMD=20;" in console_line:
                    break

                if f"Registration finished for {dev[1]} with result = 1" in console_line:
                    print(colorama.Fore.RED + f"Registration {dev[1]} is FALSE" + colorama.Fore.RESET)
                    break


def set_os_port(port, uart_speed):
    if sys.platform == "linux" or sys.platform == "linux2":
        serialport = serial.Serial("/dev/ttyUSB" + port, uart_speed)
    elif sys.platform == "win32":
        serialport = serial.Serial("COM" + port, uart_speed)
    return serialport


def set_os_path():
    path_line = os.getcwd().split("/")
    path = '/' + str(path_line[1]) + '/' + str(path_line[2]) + '/Log/'
    if not (os.path.isdir(path)):
        os.makedirs(path, 0o777)
    return path


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


def main():
    uart_speed = 115200

    port = input("Введите номер порта: ")
    path = set_os_path()
    serialport = set_os_port(port, uart_speed)

    fname = input('введите имя файла логгирования: ')

    print('введите тип девайса FIBRA для добавления.')
    dev_type = input('для добавления всех отсканеных девайсов ввести FF: ')

    if dev_type not in {"61", "62", "64", "68", "6A", "6D", "6E", "6F", "74", "75", "7C", "FF"}:
        raise "Incorrect device type! Try again"
    else:
        with open(path + fname + '.txt', 'w') as logs:  # если для винды, то (r'path')

            serialport.write("log j* 5\r\n".encode("UTF-8"))

            show_devices(serialport, logs, added_dev_list)  # показать девайсы что уже есть на хабе и запомнить их

            serialport.write("fibra reset\r\n".encode("UTF-8"))  # контрольный сброс сканирования
            time.sleep(1)
            serialport.write("fibra scan\r\n".encode("UTF-8"))  # начать сканирование шин

            add_device(serialport, logs, added_dev_list, dev_type)

            serialport.write("fibra reset\r\n".encode("UTF-8"))  # начать сканирование шин
            logs.close()
        serialport.close()


if __name__ == '__main__':
    main()