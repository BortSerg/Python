#!/usr/bin/sudo python3.10

from my_serialdata import Hub
from datetime import datetime
from colorama import Fore
from keyboard import is_pressed


def show_info(dev_list_status, frame):
    print(Fore.GREEN + f"Фрейм: {frame}" + Fore.RESET)
    for dev_data in dev_list_status:
        _dev_id_, _cmd_status_, _time_15_count_, _time_30_count_, _time_60_count_, _last_recv_ = dev_data
        print(f"{_dev_id_} {_cmd_status_} {_time_15_count_} {_time_30_count_} {_time_60_count_}")


def get_id_dev_on_hub(obj: Hub):
    dev_list_status = []
    obj.write_serial("show")
    while True:                                             # ожидание в строке слова "show"
        if "show" in obj.read_serial():
            break
    while True:
        line = obj.read_serial()
        line_parts = line.split()

        if "Hub" in line:
            obj.hub_id = line_parts[2]                      # 5й элемент строки это ID хаба

        if "Device" in line:
            dev_id = line_parts[2][2:] if line_parts[2][:2] == "00" else line_parts[2]
            type_dev = line_parts[1]
            dev_list_status.append([dev_id, Fore.RED + "CMD[20]" + Fore.RESET, 0, 0, 0, 0])  # добавляем в список состояния
            default_name_dev = f"{dev_id}{type_dev}0001"
            if default_name_dev.lower() not in line_parts[3]:   # если датчик приписан автоматом или руками, то в конце не будет "0001" как при fibra scan
                obj.id_dev_arr.append(line_parts[2])            # в этом элементе строки указан ID девайса

        if line_parts[0] not in {"Hub", "User", "Room", "Device"}:  # закончить функцию если закончен список команды "show"
            break

    if len(dev_list_status) == 0:
        empty_list = []
        empty_list.append([" ", " ", " ", " ", " ", " "])
        show_info(empty_list, obj.frame)
    else:
        show_info(dev_list_status, obj.frame)
    return dev_list_status


def check_change_frame(obj: Hub, line):                     # отслеживание изменения фрейма по hts команде
    write_param = f"WRITE_PARAM 21 0521 05{obj.hub_id} 0538"
    if write_param in line:
        sub_line = line.split(" ")
        frame = sub_line[18][2:]
        obj.frame = int(frame, 16)
        return True
    else:
        return False


def reset_statistic(dev_list_status):                       # сброс статистики при смене фрейма
    for idx, dev_data in enumerate(dev_list_status):
        _dev_id_, *_ = dev_data
        dev_data = [_dev_id_, Fore.RED + "CMD[20]" + Fore.RESET, 0, 0, 0, 0]
        dev_list_status[idx] = dev_data


def check_duplicate(id, id_list):
    duplicate = False
    for element in id_list:
        if id in element:
            duplicate = True
    return duplicate


def check_add_device(obj: Hub, line, dev_list_status):   # отслеживание добавления новых девайсов
    line_parts = line.split(";")

    if "CMD=14" in line:                                        # добавление в список состояний dev_list_status
        id_dev = line_parts[3]
        dev_data = [id_dev, Fore.RED + "CMD[20]" + Fore.RESET, 0, 0, 0, 0]
        duplicate = check_duplicate(id_dev, dev_list_status)    # проверка на дубликат, так как CMD[14] передается и при fibra scan и при приписывании
        if not duplicate:                                       # если не дубликат, то добавить в списки
            dev_list_status.append(dev_data)

    if "CMD=80" in line:                                        # добавление в список девайсов в атрибут объекта класса
        id_dev = line_parts[13][6:14]
        duplicate = check_duplicate(id_dev, obj.id_dev_arr)
        if not duplicate:
            obj.id_dev_arr.append(id_dev)

    obj.clear_console()
    show_info(dev_list_status, obj.frame)


def check_GoToFindSynchro(obj: Hub, line, dev_list_status):      # отслеживание получения команды на пересинхронизацию
    if "CMD=20" in line:
        line_parts = line.split(";")
        dev_id = line_parts[3]
        for idx, dev_data in enumerate(dev_list_status):
            _dev_id_, *_ = dev_data
            if dev_id == _dev_id_:
                temp_data = [dev_id, Fore.GREEN + "CMD[20]" + Fore.RESET, 0, 0, 0, 0]
                dev_list_status[idx] = temp_data
                obj.clear_console()
                show_info(dev_list_status, obj.frame)


def count_CheckSynchro(obj: Hub, line, dev_list_status):         # отслеживание с чет пакетов запроса поправки
    if "CMD=23" in line:
        line_parts = line.split(";")
        dev_id = line_parts[3]
        time_recv = int(line_parts[18])
        for idx, dev_data in enumerate(dev_list_status):
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
                    if (time_recv - _last_recv_ > 58000) and (time_recv - _last_recv_ < 62000):
                        _time_60_count += 1
                        _last_recv_ = int(time_recv)
                dev_data = _dev_id_, _cmd_status_, _time_15_count, _time_30_count, _time_60_count, _last_recv_
                dev_list_status[idx] = dev_data
                obj.clear_console()
                show_info(dev_list_status, obj.frame)


def check_delete_dev(obj: Hub, line, dev_list_status):   # отслеживание команды на удаление датчика
    if "05 DEV_REG 05 050635 05" in line:
        line_parts = line.split(" ")
        dev_id = line_parts[16][2:]
        for idx, element in enumerate(dev_list_status):
            if dev_id in element:
                dev_list_status.pop(idx)                         # удалить из списка ID датчка
                obj.id_dev_arr.remove(dev_id)                    # удалить из списка класса

        obj.clear_console()
        show_info(dev_list_status, obj.frame)


def check_end_scan_period(obj: Hub, line, dev_list_status):
    if "DEV_REG 0A 050A 0500 0500 05" in line:
        while len(dev_list_status) > len(obj.id_dev_arr):
            for element in dev_list_status:
                _dev_id_, *_ = element
                if _dev_id_ not in obj.id_dev_arr:
                    dev_list_status.pop(dev_list_status.index(element))

        if len(dev_list_status) == 0:
            empty_list = []
            empty_list.append(["", "", "", "", "", ""])
            show_info(empty_list, obj.frame)
        else:
            show_info(dev_list_status, obj.frame)


def main():
    frame = 0
    hub = Hub()
    port = input("Ведите номер порта: ")
    hub.set_serial_port(port, 115200)
    hub.crete_log_file(f"CheckSynchro {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}")
    dev_list_status = get_id_dev_on_hub(hub)

    while True:
        line = hub.read_serial()

        if check_change_frame(hub, line):                   # отслеживание смены фрейма
            reset_statistic(dev_list_status)                # сброс статистики по синхронизации
            hub.clear_console()
            show_info(dev_list_status, frame)

        check_add_device(hub, line, dev_list_status)
        check_GoToFindSynchro(hub, line, dev_list_status)
        count_CheckSynchro(hub, line, dev_list_status)
        check_delete_dev(hub, line, dev_list_status)
        check_end_scan_period(hub, line, dev_list_status)

        if is_pressed('ctrl+z'):
            break

    hub.close_port()


if __name__ == "__main__":
    main()