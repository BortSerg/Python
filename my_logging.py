from sys import platform
from os import getlogin, getcwd, system
from datetime import datetime
from pathlib import Path
from os import chown, chmod


class Logging(object):

    def __init__(self):
        self.__path = None
        self.__name_log_file = None
        self.os_system = platform

    def clear_console(self):
        if self.os_system in {"linux", "linux2"}:
            system('clear')
        if self.os_system == "win32":
            system('cls')

    def get_name_log_file(self):
        return self.__name_log_file

    def get_path_log_file(self):
        if self.__path is None:
            self.__get_path()
        return self.__path

    def __get_path(self):
        path = None

        if self.os_system in {'linux', 'linux2'}:
            path = f"/home/{getlogin()}/Log/"

        if self.os_system == 'win32':
            path_line = getcwd().split("\\")
            path = path_line[0] + "\\Log\\"

        Path(path).mkdir(0o777, parents=True, exist_ok=True)
        self.__path = path

    def crete_log_file(self, name_log_file=None):
        self.__name_log_file = name_log_file
        self.__get_path()
        self.__name_log_file = name_log_file if name_log_file is not None else f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"
        file = open(self.__path + self.__name_log_file, 'w')
        file.close()

        chmod(file.name, 0o777)
        chown(file.name, 1000, 1000)

    def write_log(self, message: str):
        if self.get_name_log_file() is None:
            self.__get_path()
        with open(f"{self.__path}{self.__name_log_file}", 'a') as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] {message}")
