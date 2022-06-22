#!/usr/bin/sudo python3
from my_logging import Logging
from time import time


def main():
    port = input("port: ")
    hub = Logging(port, 115200)
    hub.prefix_name_log_file = "devcom 1e"
    hub.print_data = True
    time_start = int(time())
    time_pause = 20
    flag = True

    while True:
        line = hub.write_log()
        if int(time()) - time_start >= time_pause:
            hub.write_serial(f"devcom 1E 21 {hub.hub_id} 0{int(flag)}")
            time_start = int(time())
            flag = not flag


if __name__ == '__main__':
    main()
