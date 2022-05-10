#!/usr/bin/sudo python3.9

import serial
import datetime
import colorama
import re
import sys
import time
import keyboard

UART_SPEED = 115200


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
        if power_reset_count > id_dev_arr[idx][1] or power_low_count > id_dev_arr[idx][2]:
            dev_id, *_ = dev_data
            if dev_id == dev_id_:
                dev_data = dev_id, power_reset_count, power_low_count
            id_dev_arr[idx] = dev_data


def wait_hts_power_test_status(serial_port, logs, HUB_ID, id_dev_arr):
    test_state_key_value = {
        "0500": colorama.Fore.YELLOW + "Test Stopped\n\r",
        "0501": colorama.Fore.BLUE + "Test Run\n\r",
        "0502": colorama.Fore.GREEN + "Test Finish\n\r",
        "0503": colorama.Fore.RED + "Test KZ\n\r",
    }
    flag = True
    while flag:
        line = read_serial_port(serial_port, logs)
        if "CMD=101" in line:
            power_anomaly_count(line, id_dev_arr)

        if ("0521 05" + HUB_ID + " 05E1") in line:
            stl = line.split(" ")[19]
            print(test_state_key_value[stl] + colorama.Fore.RESET)
            flag = False


def read_serial_port(serial_port, logs):
    line = serial_port.readline().decode('utf-8')
    line = anti_esc(line)
    logs.write('[' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ']' + ' ' + line)
    #print(line)
    return line


def get_hub_dev_id(serial_port, logs):
    serial_port.write("show\r\n".encode("UTF-8"))  # вывод списка устройств на хабе
    read_serial_port(serial_port, logs)
    flag = True
    id_dev_arr = []
    hub_id = None  # заменить на то что будет по умолчанию
    while flag:
        line = read_serial_port(serial_port, logs)
        line_parts = line.split(" ")
        if "Hub" in line:
            hub_id = line_parts[5]
        if "Device" in line:
            id_dev_arr.append((line_parts[2], 0, 0))
        if line_parts[0] not in {"Hub", "User", "Room", "Device"}:
            flag = False
    return hub_id, id_dev_arr


def start_power_test(serial_port, logs, HUB_ID, id_dev_arr):
    start_command = "devcom 1D 21 " + HUB_ID + " 1\r\n"
    serial_port.write(start_command.encode("UTF-8"))  # начать тест питания
    wait_hts_power_test_status(serial_port, logs, HUB_ID, id_dev_arr)


def state_test(serial_port, logs, id_dev_arr):
    test_state_command = "get hub.max*; get device*.max*\r\n"
    serial_port.write(test_state_command.encode("UTF-8"))  # состояние девайсов после теста

    flag = True
    while flag:
        if test_state_command in read_serial_port(serial_port, logs):
            flag = False

    flag = True
    while flag:
        line = read_serial_port(serial_port, logs)

        maxPowerTestState_key_value = {
            "0x00": colorama.Fore.YELLOW + "\tTest Stop\n",
            "0x01": colorama.Fore.GREEN + "\tTest OK\n",
            "0x02": colorama.Fore.GREEN + "\tTest Finish\n",
            "0x03": colorama.Fore.RED + "\tTest KZ Stop\n",
        }

        if "maxPowerTestState" in line:
            sub_line = line[: -2]
            state_key = sub_line.split(" ")[1]
            sub_line += maxPowerTestState_key_value[state_key]
            print(sub_line + colorama.Fore.RESET)

        maxPowerTestResult_key_value = {
            "0x00": colorama.Fore.YELLOW + "\tTest Stop" + colorama.Fore.RESET,
            "0x01": colorama.Fore.GREEN + "\tTest OK" + colorama.Fore.RESET,
            "0x02": colorama.Fore.RED + "\tLOW Power" + colorama.Fore.RESET,
            "0x03": colorama.Fore.RED + "\tPower RESET" + colorama.Fore.RESET,
        }
        if "maxPowerTestResult" in line:
            sub_line = line[:- 2]
            state_key = sub_line.split(" ")[1]
            sub_line += maxPowerTestResult_key_value[state_key]

            device_num = int(re.sub('[\D]', '', line.split(".")[0]))
            power_reset_count_str = colorama.Fore.MAGENTA + str(id_dev_arr[device_num][1] - 1)
            if power_reset_count_str == "-1":
                power_reset_count_str = "0"
            power_low_count_str = colorama.Fore.CYAN + str(id_dev_arr[device_num][2])

            print(sub_line + "\t" + power_reset_count_str + "\t" + power_low_count_str + "\n" + colorama.Fore.RESET)

        if line.split(" ")[1][:4] not in {"0x00", "0x01", "0x02", "0x03"}:
            flag = False


def start_stop_power_test(serial_port, logs, HUB_ID, id_dev_arr):
    start_command = "devcom 1D 21 " + HUB_ID + " 1\r\n"
    stop_command = "devcom 1D 21 " + HUB_ID + " 0\r\n"

    serial_port.write(start_command.encode("UTF-8"))  # начать тест питания
    wait_hts_power_test_status(serial_port, logs, HUB_ID, id_dev_arr)

    serial_port.write(stop_command.encode("UTF-8"))


def anti_esc(serial_port_date_line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    serial_port_date_line = ansi_escape.sub('', serial_port_date_line).replace('>\r', '>')
    return serial_port_date_line


def main():
    port = input('Введите номер порта: \r\n')

    if sys.platform in {"linux", "linux2"}:
        serial_port = serial.Serial("/dev/ttyUSB" + port, UART_SPEED)
    elif sys.platform == "win32":
        serial_port = serial.Serial("COM" + port, UART_SPEED)

    with open('/home/user/Log/PowerTest_' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.txt',
              'w') as logs:  # если для винды, то (r'path')
        HUB_ID, id_dev_arr = get_hub_dev_id(serial_port, logs)

        # Test 1 === Full normal power test
        print(colorama.Fore.RED + "Test #1 ==== Full normal power test" + colorama.Fore.RESET)
        start_power_test(serial_port, logs, HUB_ID, id_dev_arr)
        wait_hts_power_test_status(serial_port, logs, HUB_ID, id_dev_arr)
        state_test(serial_port, logs, id_dev_arr)

        # Test 2 === Start / Stop test
        print(colorama.Fore.RED + "Test #2 ==== Start / Stop test" + colorama.Fore.RESET)
        start_stop_power_test(serial_port, logs, HUB_ID, id_dev_arr)
        wait_hts_power_test_status(serial_port, logs, HUB_ID, id_dev_arr)
        state_test(serial_port, logs, id_dev_arr)

        # Test 3 === Power Reset / Low Power
        print(
            "1. Подключите датчики от ЛБП. \n2. Ожидайте сообщения о начале теста.\n3. С помощью ЛБП измените/сбросьте напряжение питания датчиков")
        print(colorama.Fore.GREEN + "\n\nЕсли готовы начать тест нажмите ENTER" + colorama.Fore.RESET)

        while True:
            if keyboard.is_pressed('enter'):
                break

        print(colorama.Fore.RED + "Test #3 ==== Power Low / Power Reset" + colorama.Fore.RESET)
        start_power_test(serial_port, logs, HUB_ID, id_dev_arr)
        wait_hts_power_test_status(serial_port, logs, HUB_ID, id_dev_arr)
        state_test(serial_port, logs, id_dev_arr)

        # Test 4 === Test stop KZ
        reset_anomaly_power_count(id_dev_arr)
        print(colorama.Fore.RED + "Test #4 ==== Stop KZ" + colorama.Fore.RESET)
        print(
            "1. Ожидайте сообщения о начале теста.\n2. Сделать короткое замыкание по питанию\n3. Тест отановится по КЗ")
        print(colorama.Fore.GREEN + "\n\nЕсли готовы начать тест нажмите ENTER" + colorama.Fore.RESET)

        while True:
            if keyboard.is_pressed('enter'):
                break

        start_power_test(serial_port, logs, HUB_ID, id_dev_arr)
        wait_hts_power_test_status(serial_port, logs, HUB_ID, id_dev_arr)
        state_test(serial_port, logs, id_dev_arr)
        logs.close()
    serial_port.close()


if __name__ == '__main__':
    main()
