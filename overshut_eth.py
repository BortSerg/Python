#!/usr/bin/sudo python3
from my_logging import Logging
from time import time
from colorama import Fore


def main():
    port = input("port: ")
    hub = Logging(port, 115200)
    pause = 10
    count = 20
    condition = False
    start = int(time())
    while count > 0:
        line = hub.read_serial()
        print(line)

        if "eth on" in line:
            print(Fore.GREEN + line + Fore.RESET)
        if "eth off" in line:
            print(Fore.RED + line + Fore.RESET)

        if int(time()) - start > pause:
            hub.write_serial("conn eth on") if condition else hub.write_serial("conn eth off")
            condition = not condition
            start = int(time())
            count -= 1

    hub.write_serial("conn eth on")
    while True:
        line = hub.read_serial()
        if "eth on" in line:
            break

    hub.close_port()


if __name__ == "__main__":
    main()