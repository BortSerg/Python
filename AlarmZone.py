#! python3.9
import time
import serial
import re
import colorama
colorama.init()
import keyboard

from datetime import datetime
from sys import platform

dev_list = []
STATUS_ZONE_TAMPER_MASK = 0x01
STATUS_ZONE_MAIN_MASK   = 0x02
STATUS_ZONE_EX1_MASK    = 0x04
STATUS_ZONE_EX2_MASK    = 0x08
STATUS_ZONE_EX3_MASK    = 0x10
STATUS_ZONE_EX4_MASK    = 0x20
STATUS_ZONE_EX5_MASK    = 0x40
STATUS_ZONE_EX6_MASK    = 0x80


def main():
    UART_SPEED = 115200

    port = input("Введите номер порта: ")

    if platform == "linux" or platform == "linux2":
        serial_port = serial.Serial("/dev/ttyUSB" + port, UART_SPEED)
    elif platform == "win32":
        serial_port = serial.Serial("COM" + port, UART_SPEED)

    read_serial_port(serial_port)

    serial_port.close()


def read_serial_port(serial_port):
    with open('/home/user/Log/tampers_' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.txt',
              'w') as logs:  # если для винды, то (r'path')
        flag = True
        while flag:
            line = serial_port.readline().decode('utf-8')
            line = anti_esc(line)
            logs.write('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ']' + ' ' + line)
            print(line)

            if "CMD=31" in line:
                spl = line.split(";")[2:]
                line = ""

                print(spl)

                for element in spl:
                    line += str(element) + " "

                print(line)
                payload_cmd_30 = spl[len(spl) - 2]
                id_dev_cmd_30 = spl[1]
                type_dev = spl[8]
                status_zone = int("0x" + payload_cmd_30[2:4], 16)

                print(colorama.Fore.CYAN + id_dev_cmd_30 + " " + type_dev + " " + payload_cmd_30 + "\r\n" + colorama.Fore.RESET)

                if status_zone & STATUS_ZONE_TAMPER_MASK == 0x01:
                    print(colorama.Fore.RED + "BACK TAMPER OPEN")
                else:
                    print(colorama.Fore.GREEN + "BACK TAMPER CLOSE")

                if status_zone & STATUS_ZONE_EX4_MASK == 0x20:
                    print(colorama.Fore.RED + "FRONT TAMPER OPEN")
                else:
                    print(colorama.Fore.GREEN + "FRONT TAMPER CLOSE")

                if status_zone & STATUS_ZONE_MAIN_MASK == 0x02:
                    print(colorama.Fore.RED + "MAIN SENSOR ALARM")
                else:
                    print(colorama.Fore.GREEN + "MAIN SENSOR GOOD")

                if type_dev == '61' or '6F':
                    if status_zone & STATUS_ZONE_EX1_MASK == 0x04:
                        print(colorama.Fore.RED + "EXTERNAL CONTACT OPEN")
                    else:
                        print(colorama.Fore.GREEN + "EXTERNAL CONTACT CLOSE")

                if type_dev == '6F':
                    if status_zone & STATUS_ZONE_EX2_MASK == 0x08:
                        print(colorama.Fore.RED + "ROLLER SHUTTER ALARM")
                    else:
                        print(colorama.Fore.GREEN + "ROLLER SHUTTER NORMAL")

                    if status_zone & STATUS_ZONE_EX3_MASK == 0x10:
                        print(colorama.Fore.RED + "ROLLER SHUTTER LOST")
                    else:
                        print(colorama.Fore.GREEN + "ROLLER SHUTTER SERVICEABLE")

                    if status_zone & STATUS_ZONE_EX5_MASK == 0x40:
                        print(colorama.Fore.RED + "SHOCK SENSOR ALARM")
                    else:
                        print(colorama.Fore.GREEN + "SHOCK SENSOR NORMAL")

                    if status_zone & STATUS_ZONE_EX6_MASK == 0x80:
                        print(colorama.Fore.RED + "TILL SENSOR ALARM")
                    else:
                        print(colorama.Fore.GREEN + "TILL SENSOR NORMAL")
            print(colorama.Fore.WHITE)
            logs.write(line)

        logs.close()


def anti_esc(serial_port_date_line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    serial_port_date_line = ansi_escape.sub('', serial_port_date_line).replace('>\r', '>')
    return serial_port_date_line


if __name__ == '__main__':
    main()
