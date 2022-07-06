#!/usr/bin/sudo python3
# ver 2.0.2
from my_logging import Logging
from time import time
from keyboard import is_pressed
from colorama import Fore


def add_dev_to_list(obj: Logging, dev_list: list):
    dev_type_list = []
    dev_id_list = []
    dev_index_list = []
    count = 0

    obj.write_serial("jwl1 jwire* on")
    obj.write_serial("show")                                        # show all devices
    while True:
        if "show" in obj.write_log():                               # wait command in commandline
            break

    while True:
        line = obj.write_log()
        line_parts = line.split()
        if "Device" in line:                                        # add device type and id to lists
            count += 1
            dev_type = line_parts[3]
            dev_id = line_parts[4]
            dev_type_list.append(dev_type)
            dev_id_list.append(dev_id)

        if line_parts[2] not in {"Device", "Room", "Hub", "User"}:
            break

    obj.write_serial("get device*.deviceindex")                     # show net id device and add items to list
    while True:
        if "get device" in obj.write_log():                         # wait command in commandline
            break
    while True:
        line = obj.write_log()
        if "deviceindex" in line:
            line_parts = line.split("deviceindex")
        if "0x" in line_parts[1]:
            index = str(int(int(line_parts[1], 16)))
            dev_index_list.append(index)

        if "deviceindex" not in line:
            break

    for i in range(0, count, 1):  # add dev type, id, netIndex, ready to load settings and settings flag (True: default/False: custom) to device data list
        default_settings = False
        ready = True
        data = [dev_type_list[i], dev_id_list[i], dev_index_list[i], ready, default_settings]
        dev_list.append(data)


def change_ready_to_load_settings(obj: Logging, line: str, dev_list: list):  # permission load settings to devices
    if "CMD=36" in line:
        line_parts = line.split(";")
        net_id = line_parts[6]

        for index, data in enumerate(dev_list):
            dev_type, dev_id, dev_net_id, ready, default_settings = data
            if dev_net_id == net_id:
                ready = True
                data = [dev_type, dev_id, dev_net_id, ready, default_settings]
                dev_list[index] = data
                pass


def main():
    device_table = []
    port = input("port: ")
    hub = Logging(port, 115200)
    time_pause = input("cycle time (sec): ")

    time_pause = 20 if time_pause == "" else int(time_pause)  # set cycle time

    hub.prefix_name_log_file = "jwire_on_off"  # prefix name log file
    hub.print_data = True  # print hub logs in console

    add_dev_to_list(hub, device_table)

    time_start = int(time())

    permission_send_settings = False  # permission send settings when bus power is on

    settings_default = {"door": "00080000",  # dict default settings for fibra device
                        "door_plus": "018A0505",
                        "motion_protect": "01800000",
                        "glass_protect": "01800000",
                        "combi_protect": "05820000",
                        "keyboard": "F5800000",
                        "motion_cam": "",
                        "motion_protect_plus": "01800000",
                        "street_siren": "",                 # siren use CMD=22 command [0600{packet_number}{settings_byte}]
                        "home_siren": "",
                        "street_siren_double_deck": ""
                        }

    settings_custom = {"door": "01810101",  # dict custom settings for fibra device
                       "door_plus": "918B2585",
                       "motion_protect": "",
                       "glass_protect": "02810180",
                       "combi_protect": "",
                       "keyboard": "",
                       "motion_cam": "",
                       "motion_protect_plus": "",
                       "street_siren": "",          # siren use CMD=22 command [0600{packet_number}{settings_byte}]
                       "home_siren": "",
                       "street_siren_double_deck": ""
                       }

    dev_type_name = {"61": 'door',  # dict  fibra code name and name (dev_num : dev name)
                     "6F": "door_plus",
                     "62": "motion_protect",
                     "64": "glass_protect",
                     "68": "combi_protect",
                     "6A": "keyboard",
                     "6D": "motion_cam",
                     "6E": "motion_protect_plus",
                     "74": "street_siren",
                     "75": "home_siren",
                     "7B": " "
                     }

    while True:
        line = hub.write_log()
        if int(time()) - time_start >= time_pause:
            hub.write_serial("jwl1 jwire* on") if permission_send_settings else hub.write_serial("jwl1 jwire* off")

            if permission_send_settings:
                for index, data in enumerate(device_table):
                    dev_type, dev_id, dev_net_id, ready, default_settings = data
                    if ready and (dev_net_id is not None):
                        hub.write_serial(f"jwl2 send_ed {dev_net_id} 36 {settings_default[dev_type_name[dev_type]]}") if default_settings \
                            else hub.write_serial(f"jwl2 send_ed {dev_net_id} 36 {settings_custom[dev_type_name[dev_type]]}")
                        default_settings = not default_settings
                        ready = False
                        data = [dev_type, dev_id, dev_net_id, ready, default_settings]
                        device_table[index] = data
                        pass

            permission_send_settings = not permission_send_settings     # revert permission in next cycle
            time_start = int(time())                                    # new time count

        change_ready_to_load_settings(hub, line, device_table)

        if is_pressed(f"ctrl + alt + {port}"):
            hub.write_serial("jwl1 jwire* on")
            line = hub.write_log()
            hub.close_port()
            break

    print(Fore.RED + "STOP" + Fore.RESET)


if __name__ == '__main__':
    main()
