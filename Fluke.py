import os
import re
import sys
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
        file_name = "/Fluke_" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"

    elif system == "win32":
        serial_port = serial.Serial("COM" + port, UART_SPEED)
        path_line = os.getcwd().split("\\")
        path = path_line[0] + "\\Log"
        file_name = "\Fluke_" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"

    try:
        os.makedirs(path)
    except OSError as error:
        if "[WinError 183]" in str(error):
            print(f"Каталог {path} уже существует")
    return serial_port, path, system, file_name


def main():
    pass


if __name__ == '__main__':
    main()
