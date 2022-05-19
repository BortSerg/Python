import re
import serial

from os import getcwd, getlogin
from sys import platform
from pathlib import Path
from datetime import datetime


class SerialDataRead:

    def __init__(self):
        self.__port = None
        self.__speed = None
        self.__serial_port = None
        self.__name_log_file = None
        self.__path = None
        self.__auto_log = True
        self.__print_console = False

    def get_all_data_about_class(self):
        print("Port №: " + str(self.__port))
        print("Speed: " + str(self.__speed))
        print("Path: " + self.__path)
        print("Name log file: " + self.__name_log_file)

        return self.__port, self.__speed, self.__path, self.__name_log_file

    def auto_log(self, flag: bool):
        self.__auto_log = flag

    def set_serial_port(self, port, speed: int):
        self.__serial_port = serial.Serial("/dev/ttyUSB" + str(port), speed)
        self.__port = port
        self.__speed = speed
        self.__create_log_file()

    def print_console(self, flag: bool):
        self.__print_console = flag

    def read_serial_data(self):
        def anti_esc(line):
            ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
            line = ansi_escape.sub('', line).replace('>\r', '>')
            return line

        line = self.__serial_port.readline().decode('utf-8')
        line = anti_esc(line)

        if self.__auto_log:
            self.write_log(line)
        if self.__print_console:
            print(line)
        return line

    def write_serial_data(self, message: str):
        self.__serial_port.write((message + "\r\n").encode('UTF-8'))

    def __get_path(self):
        path = None
        file_name = None

        if platform in {'linux', 'linux2'}:
            path = f"/home/{getlogin()}/Log/"  # there is os.walk for this
            file_name = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.txt"

        if platform == 'win32':
            path_line = getcwd().split("\\")
            path = path_line[0] + "\\Log\\"
            f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"

        Path(path).mkdir(0o777, parents=True, exist_ok=True)
        self.__path = path
        self.__name_log_file = file_name

    def __create_log_file(self):
        self.__get_path()
        file = open(self.__path + self.__name_log_file, 'w')
        file.close()

    def write_log(self, message: str):
        with open(self.__path + self.__name_log_file, 'a') as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] {message}")
