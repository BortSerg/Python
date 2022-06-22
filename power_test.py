#!/usr/bin/sudo python3
from colorama import Fore
import keyboard
import re

from my_logging import Logging


def reset_anomaly_power_count(id_dev_arr):
    for idx, dev_data in enumerate(id_dev_arr):
        dev_id, *_ = dev_data
        dev_data = dev_id, int(0), int(0)
        id_dev_arr[idx] = dev_data


def power_anomaly_count(line, id_dev_arr):
    line_parts = line.split(";")
    dev_id_ = line_parts[3]
    payload = line_parts[27]
    power_reset_count = int(payload[16:18])
    power_low_count = int(payload[18:20])

    for idx, dev_data in enumerate(id_dev_arr):
        if power_reset_count > int(id_dev_arr[idx][1]) or power_low_count > int(id_dev_arr[idx][2]):
            dev_id, *_ = dev_data
            if dev_id == dev_id_:
                dev_data = dev_id, power_reset_count, power_low_count
            id_dev_arr[idx] = dev_data


def wait_hts_power_test_status(obj: Logging, id_dev_arr):
    test_state_key_value = {
        "0500": Fore.YELLOW + "Test Stopped\n\r",
        "0501": Fore.BLUE + "Test Run\n\r",
        "0502": Fore.GREEN + "Test Finish\n\r",
        "0503": Fore.RED + "Test KZ\n\r",
    }
    while True:
        line = obj.write_log()
        if "CMD=101" in line:
            power_anomaly_count(line, id_dev_arr)

        if f"0521 05{obj.hub_id} 05E1" in line:
            stl = line.split(" ")[21]
            print(test_state_key_value[stl] + Fore.RESET)
            break


def get_hub_dev_id(obj: Logging):
    obj.write_serial("show")
    while True:
        if "show" in obj.write_log():
            break

    id_dev_arr = []
    while True:
        line = obj.write_log()
        line_parts = line.split()

        if "Device" in line:
            id_dev_arr.append((line_parts[4], 0, 0))
        if line_parts[2] not in {"Hub", "User", "Room", "Device"}:
            break
    return id_dev_arr


def start_power_test(obj, id_dev_arr):
    start_command = f"devcom 1D 21 {obj.hub_id} 1"
    obj.write_serial(start_command)
    wait_hts_power_test_status(obj, obj. id_dev_arr)


def state_test(obj: Logging, id_dev_arr):
    test_state_command = "get hub.max*; get device*.max*"
    obj.write_serial(test_state_command)                                # состояние девайсов после теста

    while True:                                                         # ожидание команды в консоли
        if test_state_command in obj.write_log():
            break

    maxPowerTestState_key_value = {                                     # словарь состояний хаба в тесте питания
        "0x00": Fore.YELLOW + "\tTest Stop\n",
        "0x01": Fore.GREEN + "\tTest OK\n",
        "0x02": Fore.GREEN + "\tTest Finish\n",
        "0x03": Fore.RED + "\tTest KZ Stop\n",
    }

    maxPowerTestResult_key_value = {                                    # словарь состояний девайсов в тесте питания
        "0x00": Fore.YELLOW + "\tTest Stop" + Fore.RESET,
        "0x01": Fore.GREEN + "\tTest OK" + Fore.RESET,
        "0x02": Fore.RED + "\tLOW Power" + Fore.RESET,
        "0x03": Fore.RED + "\tPower RESET" + Fore.RESET,
    }

    while True:
        line = obj.write_log()

        if "maxPowerTestState" in line:                                 # вывод статуса хаба
            sub_line = line[: -2].split()[2:]
            state_key = sub_line[1]                                     # получить ключ состояния
            sub_line[0] += maxPowerTestState_key_value[state_key]       # выбор состояния из словаря по ключу
            print(sub_line[0] + Fore.RESET)

        if "maxPowerTestResult" in line:
            sub_line = line[: -2].split()[2:]
            state_key = sub_line[1]                      # получить ключ состояния
            sub_line[0] += maxPowerTestResult_key_value[state_key]     # выбор состояния из словаря по ключу

            device_num = int(re.sub('[\D]', '', sub_line[0].split(".")[0]))
            power_reset_count_str = str(id_dev_arr[device_num][1])

            power_reset_count_str = Fore.MAGENTA + "0" if power_reset_count_str == "1" else Fore.MAGENTA + power_reset_count_str

            power_low_count_str = Fore.CYAN + str(id_dev_arr[device_num][2])

            print(f"{sub_line[0]} \t{power_reset_count_str} \t{power_low_count_str}\n" + Fore.RESET)

        if line.split(" ")[3][:4] not in {"0x00", "0x01", "0x02", "0x03"}:
            break


def wait_enter():
    while True:
        if keyboard.is_pressed('enter'):
            break


def start_stop_power_test(obj: Logging, id_dev_arr):
    start_command = f"devcom 1D 21 {obj.hub_id} 1"
    stop_command = f"devcom 1D 21 {obj.hub_id} 0"
    obj.write_serial(start_command)                         # начать тест питания
    wait_hts_power_test_status(obj, id_dev_arr)
    obj.write_serial(stop_command)


def main():
    port = input('Введите номер порта: \r\n')
    hub = Logging(port, 115200)                             # параметры порта для объекта класса
    hub.prefix_name_log_file = "PowerTest"
    id_dev_arr = get_hub_dev_id(hub)                        # получение ID хаба и списка девайсов на хабе
    hub.clear_console()                                     # очистка экрана консоли
    hub.write_serial(f"devcom 1d 21 {hub.hub_id} 0")
    """
    # Test 1 === Full normal power test
    print(Fore.RED + "Test #1 ==== Full normal power test" + Fore.RESET)
    start_power_test(hub, id_dev_arr)                       # начало теста
    wait_hts_power_test_status(hub, id_dev_arr)             # ожидание конца теста по HTS команде
    state_test(hub, id_dev_arr)                             # вывод результатов теста

    # Test 2 === Start / Stop test
    print(Fore.RED + "Test #2 ==== Start / Stop test" + Fore.RESET)
    start_stop_power_test(hub, id_dev_arr)
    wait_hts_power_test_status(hub, id_dev_arr)
    state_test(hub, id_dev_arr)
    """
    # Test 3 === Power Reset / Low Power
    print("1. Подключите датчики от ЛБП. \n2. Ожидайте сообщения о начале теста.\n3. С помощью ЛБП измените/сбросьте напряжение питания датчиков")
    print(Fore.GREEN + "\n\nЕсли готовы начать тест нажмите ENTER" + Fore.RESET)

    #wait_enter()

    print(Fore.RED + "Test #3 ==== Power Low / Power Reset" + Fore.RESET)
    start_power_test(hub, id_dev_arr)
    wait_hts_power_test_status(hub, id_dev_arr)
    state_test(hub, id_dev_arr)
    """
    # Test 4 === Test stop KZ
    reset_anomaly_power_count(id_dev_arr)
    print(Fore.RED + "Test #4 ==== Stop KZ" + Fore.RESET)
    print("1. Ожидайте сообщения о начале теста.\n2. Сделать короткое замыкание по питанию\n3. Тест отановится по КЗ")
    print(Fore.GREEN + "\n\nЕсли готовы начать тест нажмите ENTER" + Fore.RESET)

    wait_enter()

    start_power_test(hub, id_dev_arr)
    wait_hts_power_test_status(hub, id_dev_arr)
    state_test(hub, id_dev_arr)
    hub.close_port()
    """

if __name__ == '__main__':
    main()
