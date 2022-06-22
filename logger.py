#!/usr/bin/sudo python3

from my_logging import Logging

def main():
    port = input('Введите номер порта: ')
    hub = Logging(port, 115200)
    hub.print_data = True
    while True:
        hub.write_log()


if __name__ == "__main__":
    main()
