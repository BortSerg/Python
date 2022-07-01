#!/usr/bin/sudo python3
from my_logging import Logging
from time import time
from keyboard import is_pressed
from colorama import Fore


def main():
    port = input("port: ")
    hub = Logging(port, 115200)
    time_pause = input("cycle time (sec): ")

    time_pause = 20 if time_pause == "" else int(time_pause)

    hub.prefix_name_log_file = "jwire_on_off"
    hub.print_data = True
    time_start = int(time())

    flag = False
    settings_flag = False

    settings_default = {"door": "00080000"}
    settings_custom = {"door": "01810101"}
    while True:
        line = hub.write_log()
        if int(time()) - time_start >= time_pause:
            hub.write_serial("jwl1 jwire* on") if flag else hub.write_serial("jwl1 jwire* off")

            if flag:
                for net_id in range(1, 40, 1):
                    hub.write_serial(f"jwl2 send_ed {net_id} 36 {settings_default['door']}") if settings_flag else hub.write_serial(f"jwl2 send_ed {net_id} 36 {settings_custom['door']}")
                settings_flag = not settings_flag

            flag = not flag
            time_start = int(time())

        if is_pressed(f"ctrl + alt + {port}"):
            hub.write_serial("jwl1 jwire* on")
            line = hub.write_log()
            hub.close_port()
            break

    print(Fore.RED + "STOP" + Fore.RESET)


if __name__ == '__main__':
    main()
