#!/usr/bin/sudo python3
from my_logging import Logging
from time import time


def main():
    port = input("port: ")
    hub = Logging(port, 115200)
    time_pause = input("cycle time (sec): ")
    time_pause = 20 if time_pause == "" else int(time_pause)

    hub.prefix_name_log_file = "jwire_on_off"
    hub.print_data = True
    time_start = int(time())
    flag = False

    while True:
        line = hub.write_log()
        if int(time()) - time_start >= time_pause:
            hub.write_serial("jwl1 jwire* on") if flag else hub.write_serial("jwl1 jwire* off")
            time_start = int(time())
            flag = not flag


if __name__ == '__main__':
    main()
