#!/usr/bin/sudo python3.10

import os
import re
import sys
import time
import tqdm
import serial
import datetime
import colorama
import keyboard




def read_serial_port(serialport, logs):
    line = serialport.readline().decode('utf-8')
    line = anti_esc(line)
    logs.write('[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ']' + ' ' + line)
    # print(line)
    return line


def anti_esc(line):  # фильтр "мусора"
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    line = ansi_escape.sub('', line).replace('>\r', '>')
    return line


def eth_off(serialport):
    serialport.write("conn eth off\r\n".encode('UTF-8'))


def eth_on(serialport):
    serialport.write("conn eth on\r\n".encode('UTF-8'))


def gsm_off(serialport):
    serialport.write("conn gprs off\r\n".encode('UTF-8'))


def gsm_on(serialport):
    serialport.write("conn gprs on\r\n".encode('UTF-8'))


def start_test(hub_name, hub_id, distance, type_cable, name_test, serialport, port, path):
    with open(path + type_cable + '_' + distance + '_' + hub_name + '_' + hub_id + '_' + name_test + '_USB' + port + '.txt', 'w') as logs:  # если для винды, то (r'path')
        os.chmod(logs.name, 0o777)
        os.chown(logs.name, 1000, 1000)

        time_start = datetime.datetime.now().minute
        print(colorama.Fore.CYAN + "Start time " + type_cable + "_" + name_test + " " + str(datetime.datetime.now()))
        serialport.write("show\r\n".encode('UTF-8'))
        for i in tqdm.tqdm(range(0, 60), desc=colorama.Fore.RED + "Progress " + name_test):
            while True:
                line = read_serial_port(serialport, logs)
                time_now = datetime.datetime.now().minute
                if abs(time_now - time_start) > 0:
                    time_start = time_now
                    break
        print(colorama.Fore.GREEN + "\rTest " + name_test + " Finish at " + str(
            datetime.datetime.now()) + colorama.Fore.RESET + "\n")
        logs.close()


def wait_enter():
    while True:
        if keyboard.is_pressed('enter'):
            break


def _220V_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path):
    if mode == 2:
        print(colorama.Fore.YELLOW + "Отключите АКБ и нажмите ENTER для продолжения тестов " + colorama.Fore.RESET)
        wait_enter()
    elif mode == 1:
        socket_on(serialport, socket_id)
        relay_off(serialport, relay_id_norm)
        relay_off(serialport, relay_id_low)
    match sel2:
        case 1:
            # GSM Only
            gsm_on(serialport)
            eth_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "220V_GSM", serialport, port, path)

            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "220V_GSM+ETH", serialport, port, path)
            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "220V_ETH", serialport, port, path)
        case 2:
            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "220V_GSM+ETH", serialport, port, path)

            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "220V_ETH", serialport, port, path)
        case 3:
            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "220V_ETH", serialport, port, path)


def _AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path):
    # Normal AKB Test
    if mode == 2:
        print(colorama.Fore.YELLOW + "1. Подключите заряженый АКБ")
        print("2. Отключите питание 220В и нажмите ENTER для продолжения тестов" + colorama.Fore.RESET)
        wait_enter()
    elif mode == 1:
        relay_on(serialport, relay_id_norm)
        socket_off(serialport, socket_id)
    match sel2:
        case 1:
            # GSM Only
            gsm_on(serialport)
            eth_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "AKB_GSM", serialport, port, path)

            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "AKB_GSM+ETH", serialport, port, path)

            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "AKB_ETH", serialport, port, path)
        case 2:
            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "AKB_GSM+ETH", serialport, port, path)

            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "AKB_ETH", serialport, port, path)
        case 3:
            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "AKB_ETH", serialport, port, path)


def _LOW_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path):
    # LOW Power AKB Test
    if mode == 2:
        print(colorama.Fore.YELLOW + "1. Подключите питание 220В")
        print("2. Подключите разряженый АКБ")
        print("3. Отключите питание 220В и нажмите ENTER для продолжения тестов" + colorama.Fore.RESET)
        wait_enter()
    elif mode == 1:
        socket_on(serialport, socket_id)
        relay_off(serialport, relay_id_norm)
        relay_on(serialport, relay_id_low)
        socket_off(serialport, socket_id)

    match sel2:
        case 1:
            # GSM Only
            gsm_on(serialport)
            eth_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "LOW_AKB_GSM", serialport, port, path)

            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "LOW_AKB_GSM+ETH", serialport, port, path)

            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "LOW_AKB_ETH", serialport, port, path)
        case 2:
            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "LOW_AKB_GSM+ETH", serialport, port, path)

            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "LOW_AKB_ETH", serialport, port, path)
        case 3:
            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "LOW_AKB_ETH", serialport, port, path)


def _Charge_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path):
    # Charge AKB
    if mode == 2:
        print(colorama.Fore.YELLOW + "1. Подключите питание 220В и нажмите ENTER для продолжения тестов" + colorama.Fore.RESET)
        wait_enter()
    elif mode == 1:
        socket_on(serialport, socket_id)
    match sel2:
        case 1:
            # GSM Only
            gsm_on(serialport)
            eth_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "Charge_AKB_GSM", serialport, port, path)

            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "Charge_AKB_GSM+ETH", serialport, port, path)

            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "Charge_AKB_ETH", serialport, port, path)
        case 2:
            # GSM + ETH
            eth_on(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "Charge_AKB_GSM+ETH", serialport, port, path)

            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "Charge_AKB_ETH", serialport, port, path)
        case 3:
            # ETH Only
            gsm_off(serialport)
            start_test(hub_name, hub_id, distance, type_cable, "Charge_AKB_ETH", serialport, port, path)

    eth_on(serialport)
    gsm_on(serialport)

    if mode == 1:
        relay_off(serialport, relay_id_low)


def cable_type():
    while True:
        type = input("\nТип кабеля:\n1. Alarm\n2. UTP \t\t")
        if type == "1":
            type_cable = "Alarm"
            break
        if type == "2":
            type_cable = "UTP"
            break
    return type_cable


def read_line(serialport):
    line = serialport.readline().decode('UTF-8')
    line = anti_esc(line)
    # print(line)
    return line


def relay_on(serialport, reley_id):
    serialport.write(("jwl3 ws %s 1\r\n" % reley_id).encode('UTF-8'))
    while True:
        line = read_line(serialport)
        if (reley_id + ";CMD=105") in line:
            time.sleep(5)
            """
            time_now = datetime.datetime.now().second
            while abs(datetime.datetime.now().second - time_now < 5):
                pass
            """
            break


def relay_off(serialport, reley_id):
    serialport.write(("jwl3 ws %s 2\r\n" % reley_id).encode('UTF-8'))
    while True:
        line = read_line(serialport)
        if (reley_id + ";CMD=105") in line:
            time.sleep(5)
            """
            time_now = datetime.datetime.now().second
            while abs(datetime.datetime.now().second - time_now < 5):
                pass
            """
            break


def socket_on(serialport, socket_id):
    serialport.write(("jwl3 ws %s 1\r\n" % socket_id).encode('UTF-8'))
    while True:
        line = read_line(serialport)
        if (socket_id + ";CMD=105") in line:
            time.sleep(5)
            """
            time_now = datetime.datetime.now().second
            while abs(datetime.datetime.now().second - time_now < 5):
                pass
            """
            break


def socket_off(serialport, socket_id):
    serialport.write(("jwl3 ws %s 2\r\n" % socket_id).encode('UTF-8'))
    while True:
        line = read_line(serialport)
        if (socket_id + ";CMD=105") in line:
            time.sleep(5)
            """
            time_now = datetime.datetime.now().second
            while abs(datetime.datetime.now().second - time_now < 5):
                pass
            """
            break


def cable_distance():
    distance = str(input("\nДлина кабеля: \t\t"))
    return distance


def selector():
    while True:
        sel1 = int(input("\nКакие тесты проводить? \n1. 220В/АКБ/LOW_AKB/Charge \n2. АКБ/LOW_AKB/Charge \n3. LOW_AKB/Charge \n4. Charge \t\t"))
        if (sel1 >= 1) and (sel1 < 5):
            break
    while True:
        sel2 = int(input("\nПодтесты: \n1. GSM/GSM+ETH/ETH \n2. GSM+ETH \n3. ETH \t\t"))
        if (sel2 >= 1) and (sel2 < 4):
            break
    return sel1, sel2


def test_mode():
    while True:
        mode = int(input("\n1. Авто режим теста \n2. Ручной режим: \t\t"))
        if mode == 1 or mode == 2:
            break
    return mode


def set_os_serialport(port, UART_SPEED):
    if sys.platform == "linux" or sys.platform == "linux2":
        serialport = serial.Serial("/dev/ttyUSB" + port, UART_SPEED)
    elif sys.platform == "win32":
        serialport = serial.Serial("COM" + port, UART_SPEED)
    return serialport


def set_os_path():
    try:
        path_line = os.getcwd().split("/")
        path = '/' + str(path_line[1]) + '/' + str(path_line[2]) + '/Log/LineLostTest/'
    except OSError as error:
        os.makedirs(path[:-1])
    return path


def get_info(serialport, mode):
    serialport.write("show\r\n".encode('UTF-8'))
    while True:
        if "show" in read_line(serialport):
            break

    socket_id = ""
    relay_id_low = ""
    relay_id_norm = ""
    hub_name = ""
    hub_id = ""
    exit_flag = False
    while True:
        line = read_line(serialport)
        line_parts = line.split(" ")
        if "Hub" in line:
            hub_name = ""
            for i in line_parts[6:]:
                hub_name += i
            hub_name = hub_name[:-1]
            hub_id = line_parts[5]

        if mode == 1:
            if "Device 1E" in line:
                socket_id = line_parts[2][2:].upper()

            if "Device 12" in line:
                if "LOW" in line_parts[3].upper():
                    relay_id_low = line_parts[2][2:].upper()
                if "NOR" in line_parts[3].upper():
                    relay_id_norm = line_parts[2][2:].upper()

        if mode == 2:
            socket_id = "000000"
            relay_id_norm = "000000"
            relay_id_low = "000000"

        if line_parts[0] not in {"Hub", "User", "Room", "Device"}:
            break

    if mode == 1:
        if socket_id == "":
            print("Error socket_id! Please add a socket")
            socket_id = "000000"
            exit_flag = True
        if relay_id_low == "":
            print("Error relay_id_low! Please add a relay and name it 'LOW' ")
            relay_id_low = "000000"
            exit_flag = True
        if relay_id_norm == "":
            print("Error relay_id_norm! Please add a relay and name it 'NORM'")
            relay_id_norm = "000000"
            exit_flag = True

    return hub_name, hub_id, socket_id, relay_id_norm, relay_id_low, exit_flag




def print_test_info(path, hub_name, hub_id, port, mode, socket_id, relay_id_norm, relay_id_low, type_cable, distance):
    os.system('clear')
    print("Path: %s" % path)
    print("HUB: %s %s" % (hub_id, hub_name))
    print("Port: %s" % port)
    if mode == 1:
        print("Test mode: Auto")
        print("Socket: %s" % socket_id)
        print(colorama.Fore.GREEN + "Norm relay: %s" % relay_id_norm + colorama.Fore.RESET)
        print(colorama.Fore.RED + "Low relay: %s" % relay_id_low + colorama.Fore.RESET)
    if mode == 2:
        print("Test mode: Manual")
    print("Type cable: %s" % type_cable)
    print("Distance: %s" % distance)


def main():
    UART_SPEED = 115200
    port = input("Введите номер порта: ")
    serialport = set_os_serialport(port, UART_SPEED)
    path = set_os_path()
    mode = test_mode()
    hub_name, hub_id, socket_id, relay_id_norm, relay_id_low, exit_flag = get_info(serialport, mode)

    if exit_flag:
        print(colorama.Fore.YELLOW + "Check if the socket and relay are added to the hub" + colorama.Fore.RESET)
        sys.exit(0)

    sel1, sel2 = selector()

    distance = cable_distance()
    type_cable = cable_type()

    print_test_info(path, hub_name, hub_id, port, mode, socket_id, relay_id_norm, relay_id_low, type_cable, distance)

    match sel1:
        case 1:
            _220V_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)  # 220V Tests
            sel2 = 1
            _AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)  # Normal AKB Tests
            _LOW_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)  # LOW AKB Tests
            _Charge_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)  # Charge AKB Tests
        case 2:
            _AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)
            sel2 = 1
            _LOW_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)
            _Charge_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)
        case 3:
            _LOW_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)
            sel2 = 1
            _Charge_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)
        case 4:
            _Charge_AKB_test(serialport, port, type_cable, socket_id, relay_id_low, relay_id_norm, mode, sel2, hub_name, hub_id, distance, path)
    serialport.close()


if __name__ == '__main__':
    main()
