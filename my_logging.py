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
        self.__get_path()
        return self.__path

    def __get_path(self):
        path = None
        name = self.get_name_log_file()
        file_name = None

        if self.os_system in {'linux', 'linux2'}:
            path = f"/home/{getlogin()}/Log/"
            if name is None:
                file_name = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.txt"
            else:
                file_name = name

        if self.os_system == 'win32':
            path_line = getcwd().split("\\")
            path = path_line[0] + "\\Log\\"
            if name is None:
                file_name = f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"
            else:
                file_name = name

        Path(path).mkdir(0o777, parents=True, exist_ok=True)
        self.__path = path
        self.__name_log_file = file_name

    def __create_auto_log_file(self):
        file = open(self.__path + self.__name_log_file, 'w')
        file.close()

    def crete_log_file(self, name_log_file=None):
        self.__get_path()
        if name_log_file is None:
            self.__create_auto_log_file()

        else:
            self.__name_log_file = name_log_file
            file = open(self.__path + self.__name_log_file, 'w')
            file.close()

        chmod(file.name, 0o777)
        chown(file.name, 1000, 1000)

    def write_log(self, message: str):
        if self.get_name_log_file() is None:
            self.__get_path()
            self.__create_auto_log_file()
        with open(self.__path + self.__name_log_file, 'a') as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] {message}")