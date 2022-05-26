#!/usr/bin/sudo python3.10

from my_serialdata import Hub
from colorama import Fore
from os import system
from keyboard import is_pressed
from tqdm import tqdm
from datetime import datetime
from time import time


def eth_off(obj: Hub):
    obj.write_serial("conn eth off")


def eth_on(obj: Hub):
    obj.write_serial("conn eth on")


def gsm_off(obj: Hub):
    obj.write_serial("conn gprs off")


def gsm_on(obj: Hub):
    obj.write_serial("conn gprs on")


def relay_on(obj: Hub, relay_id):
    obj.write_serial("jwl3 ws %s 1" % relay_id)
    wait(obj, relay_id)


def relay_off(obj: Hub, relay_id):
    obj.write_serial("jwl3 ws %s 2" % relay_id)
    wait(obj, relay_id)


def socket_on(obj: Hub, socket_id):
    obj.write_serial("jwl3 ws %s 1" % socket_id)
    wait(obj, socket_id)


def socket_off(obj: Hub, socket_id):
    obj.write_serial("jwl3 ws %s 2" % socket_id)
    wait(obj, socket_id)


def wait(obj: Hub, id):                                          # wait some time after commutation
    time_send_command = None
    while True:
        line = obj.read_serial()
        if f"{id};CMD=105" in line:
            time_send_command = int(time())
        if time_send_command is not None and int(time() - time_send_command) > 5:
            break


def selector():                                                     # test parts selector
    while True:
        sel1 = int(input("\nКакие тесты проводить? \n1. 220В/АКБ/LOW_AKB/Charge \n2. АКБ/LOW_AKB/Charge \n3. LOW_AKB/Charge \n4. Charge \t\t"))
        if (sel1 >= 1) and (sel1 < 5):
            break
    while True:
        sel2 = int(input("\nПодтесты: \n1. GSM/GSM+ETH/ETH \n2. GSM+ETH \n3. ETH \t\t"))
        if (sel2 >= 1) and (sel2 < 4):
            break
    return sel1, sel2


def test_mode():                                                    # test mode selector (auto/manual)
    while True:
        mode = int(input("\n1. Авто режим теста \n2. Ручной режим: \t\t"))
        if mode == 1 or mode == 2:
            break
    return mode


def cable_distance():       # enter cable distance
    distance = str(input("\nДлина кабеля: \t\t"))
    return distance


def cable_type():                                                   # select cable type
    while True:
        type = input("\nТип кабеля:\n1. Alarm\n2. UTP \t\t")
        if type == "1":
            type_cable = "Alarm"
            break
        if type == "2":
            type_cable = "UTP"
            break
    return type_cable


def clear_screen(os_system):                                        # clear console screen
    if str(os_system) in {'linux2', 'linux'}:
        system('clear')
    if os_system == 'win32':
        system('cls')


def wait_enter():                                                   # wait press enter
    while True:
        if is_pressed('enter'):
            break


def get_info(obj: Hub, mode):
    obj.set_autolog(False)
    obj.write_serial("show")
    while True:
        if "show" in obj.read_serial():
            break

    exit_flag = False

    while True:
        line = obj.read_serial()
        line_parts = line.split(" ")
        if "Hub" in line:
            hub_name = ""
            for i in line_parts[6:]:
                hub_name += i
            obj.hub_name = hub_name[:-1]
            obj.hub_id = line_parts[5]

        if mode == 1:
            if "Device 1E" in line:
                obj.socket_id = line_parts[2][2:].upper()

            if "Device 12" in line:
                if "LOW" in line_parts[3].upper():
                    obj.relay_low_id = line_parts[2][2:].upper()
                if "NOR" in line_parts[3].upper():
                    obj.relay_norm_id = line_parts[2][2:].upper()

        if mode == 2:
            obj.socket_id = "000000"
            obj.relay_norm_id = "000000"
            obj.relay_low_id = "000000"

        if line_parts[0] not in {"Hub", "User", "Room", "Device"}:
            break
    obj.set_autolog(True)
    conditions = (obj.socket_id, obj.relay_low_id, obj.relay_norm_id)
    descriptions = [
        "Error socket_id! Please add a socket",
        "Error relay_id_low! Please add a relay and name it 'LOW'",
        "Error socket_id! Please add a socket"
    ]
    for cond, descr in zip(conditions, descriptions):
        if cond is None:
            exit_flag = True
            print(descr)

    if exit_flag:
        print(Fore.YELLOW + "Check if the socket and relay are added to the hub" + Fore.RESET)
        exit(0)


def print_test_info(obj: Hub, type_cable, distance, mode):
    clear_screen(obj.os_system)
    print("Path: %s" % obj.get_path_log_file())
    print("HUB: %s %s" % (obj.hub_id, obj.hub_name))
    print("Port: %s" % obj.get_port())
    if mode == 1:
        print("Test mode: Auto")
        print("Socket: %s" % obj.socket_id)
        print(Fore.GREEN + "Norm relay: %s" % obj.relay_norm_id + Fore.RESET)
        print(Fore.RED + "Low relay: %s" % obj.relay_low_id + Fore.RESET)
    if mode == 2:
        print("Test mode: Manual")
    print("Type cable: %s" % type_cable)
    print("Distance: %s" % distance)


def start_test(obj: Hub, distance, type_cable, name_test):
    obj.crete_log_file(f"{type_cable} {distance} {obj.hub_name} {obj.hub_id} {name_test}_USB{obj.get_port()}.txt")

    time_start = int(time())
    print(Fore.CYAN + f"Start time {type_cable} {name_test} {str(datetime.now())}")
    obj.write_serial("show")
    for i in tqdm(range(0, 60), desc=Fore.RED + f"Progress {name_test}"):
        while True:
            line = obj.read_serial()
            time_now = int(time())
            if abs(time_now - time_start) > 60:
                time_start = time_now
                break
    print(Fore.GREEN + f"\rTest {name_test} Finish at {str(datetime.now())}" + Fore.RESET + "\n")


def _220V_test(obj: Hub, mode, sel2, distance, type_cable):
    if mode == 2:
        print(Fore.YELLOW + "Отключите АКБ и нажмите ENTER для продолжения тестов " + Fore.RESET)
        wait_enter()
    elif mode == 1:
        socket_on(obj, obj.socket_id)
        relay_off(obj, obj.relay_norm_id)
        relay_off(obj, obj.relay_low_id)
    match sel2:
        case 1:
            # GSM Only
            gsm_on(obj)
            eth_off(obj)
            start_test(obj, distance, type_cable, "220V_GSM")

            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "220V_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "220V_ETH")
        case 2:
            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "220V_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "220V_ETH")
        case 3:
            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "220V_ETH")


def _AKB_test(obj: Hub, mode, sel2, distance, type_cable):
    # Normal AKB Test
    if mode == 2:
        print(Fore.YELLOW + "1. Подключите заряженый АКБ")
        print("2. Отключите питание 220В и нажмите ENTER для продолжения тестов" + Fore.RESET)
        wait_enter()
    elif mode == 1:
        relay_on(obj, obj.relay_norm_id)
        socket_off(obj, obj.socket_id)
    match sel2:
        case 1:
            # GSM Only
            gsm_on(obj)
            eth_off(obj)
            start_test(obj, distance, type_cable, "AKB_GSM")

            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "AKB_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "AKB_ETH")
        case 2:
            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "AKB_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "AKB_ETH")
        case 3:
            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "AKB_ETH")


def _LOW_AKB_test(obj: Hub, mode, sel2, distance, type_cable):
    # LOW Power AKB Test
    if mode == 2:
        print(Fore.YELLOW + "1. Подключите питание 220В")
        print("2. Подключите разряженый АКБ")
        print("3. Отключите питание 220В и нажмите ENTER для продолжения тестов" + Fore.RESET)
        wait_enter()
    elif mode == 1:
        socket_on(obj, obj.socket_id)
        relay_off(obj, obj.relay_norm_id)
        relay_on(obj, obj.relay_low_id)
        socket_off(obj, obj.socket_id)

    match sel2:
        case 1:
            # GSM Only
            gsm_on(obj)
            eth_off(obj)
            start_test(obj, distance, type_cable, "LOW_AKB_GSM")

            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "LOW_AKB_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "LOW_AKB_ETH")
        case 2:
            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "LOW_AKB_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "LOW_AKB_ETH")
        case 3:
            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "LOW_AKB_ETH")


def _Charge_AKB_test(obj: Hub, mode, sel2, distance, type_cable):
    # Charge AKB
    if mode == 2:
        print(Fore.YELLOW + "1. Подключите питание 220В и нажмите ENTER для продолжения тестов" + Fore.RESET)
        wait_enter()
    elif mode == 1:
        socket_on(obj, obj.socket_id)
    match sel2:
        case 1:
            # GSM Only
            gsm_on(obj)
            eth_off(obj)
            start_test(obj, distance, type_cable, "Charge_AKB_GSM")

            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "Charge_AKB_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "Charge_AKB_ETH")
        case 2:
            # GSM + ETH
            eth_on(obj)
            start_test(obj, distance, type_cable, "Charge_AKB_GSM+ETH")

            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "Charge_AKB_ETH")
        case 3:
            # ETH Only
            gsm_off(obj)
            start_test(obj, distance, type_cable, "Charge_AKB_ETH")

    eth_on(obj)
    gsm_on(obj)

    if mode == 1:
        relay_off(obj, obj.relay_low_id)


def main():
    UART_SPEED = 115200
    hub = Hub()
    port = input("Введите номер порта: ")
    hub.set_serial_port(port, UART_SPEED)                              # set UART port and SPEED for class object

    mode = test_mode()
    get_info(hub, mode)                                                # checking for devices on the hub if automatic test mode is selected

    sel1, sel2 = selector()
    distance = cable_distance()
    type_cable = cable_type()

    print_test_info(hub, type_cable, distance, mode)                    # console print some parameters test and devises in the hub

    match sel1:
        case 1:
            _220V_test(hub, mode, sel2, distance, type_cable)           # 220V Test
            sel2 = 1
            _AKB_test(hub, mode, sel2, distance, type_cable)            # Normal AKB Tests
            _LOW_AKB_test(hub, mode, sel2, distance, type_cable)        # LOW AKB Tests
            _Charge_AKB_test(hub, mode, sel2, distance, type_cable)     # Charge AKB Tests

        case 2:
            _AKB_test(hub, mode, sel2, distance, type_cable)
            sel2 = 1
            _LOW_AKB_test(hub, mode, sel2, distance, type_cable)
            _Charge_AKB_test(hub, mode, sel2, distance, type_cable)

        case 3:
            _LOW_AKB_test(hub, mode, sel2, distance, type_cable)
            sel2 = 1
            _Charge_AKB_test(hub, mode, sel2, distance, type_cable)

        case 4:
            _Charge_AKB_test(hub, mode, sel2, distance, type_cable)


if __name__ == '__main__':
    main()
