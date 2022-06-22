import serial
import re
from my_hub import Hub
from sys import platform
from os import system


class SerialData(Hub):
    def __init__(self):
        Hub.__init__(self)
        self.__port = None
        self.__speed = None
        self.__serial_port = None
        self.__autolog = True
        self.__print_data = False
        self.os_system = platform
        self.print_data = False

    def clear_console(self):
        system('clear') if self.os_system in {"linux", "linux2"} else system('cls')
        """
        if self.os_system in {"linux", "linux2"}:
            system('clear')
        if self.os_system == "win32":
            system('cls')
        """

    def set_serial_port(self, port, speed: int):
        self.__serial_port = serial.Serial("/dev/ttyUSB" + str(port), speed)
        self.__port = port
        self.__speed = speed

    def read_serial(self):
        def anti_esc(line):
            ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
            line = ansi_escape.sub('', line).replace('>\r', '>')
            return line

        line = self.__serial_port.readline().decode('utf-8')
        line = anti_esc(line)

        return line

    def write_serial(self, message: str):
        self.__serial_port.write((message + "\r\n").encode('UTF-8'))

    def close_port(self):
        self.__serial_port.close()

    def get_port(self):
        return self.__port
