from os import getlogin, getcwd
from datetime import datetime
from pathlib import Path
from os import chown, chmod
from my_serialdata import SerialData


class Logging(SerialData):
    def __init__(self, port: str, speed: int):
        SerialData.__init__(self)
        self.__path = None
        self.__name_log_file = None
        self.prefix_name_log_file = None
        self.time_stamp_in_name_log_file = True
        self.hub_info_in_name_log_file = True
        self.set_serial_port(port, speed)
        self.get_hub_info()

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

    def crete_log_file(self):
        self.__get_path()

        if self.time_stamp_in_name_log_file:
            if self.hub_info_in_name_log_file:
                self.__name_log_file = f"{self.hub_name}_{self.hub_id}_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt" if self.prefix_name_log_file is None \
                    else f"{self.prefix_name_log_file}_{self.hub_name}_{self.hub_id}_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"
            else:
                self.__name_log_file = f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt" if self.prefix_name_log_file is None \
                    else f"{self.prefix_name_log_file}_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"

        else:
            if self.hub_info_in_name_log_file:
                self.__name_log_file = f"{self.hub_name}_{self.hub_id}.txt" if self.prefix_name_log_file is None \
                    else f"{self.prefix_name_log_file}_{self.hub_name}_{self.hub_id}.txt"
            else:
                self.__name_log_file = f"NotPrefix_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt" if self.prefix_name_log_file is None \
                    else f"{self.prefix_name_log_file}.txt"

        file = open(self.__path + self.__name_log_file, 'w')
        file.close()

        chmod(file.name, 0o777)
        chown(file.name, 1000, 1000)

    def get_hub_info(self):
        self.write_serial("show")

        while True:
            if "show" in self.read_serial():
                break

        while True:
            line = self.read_serial()
            parts_line = line.split()

            if "Hub" in line:
                hub_name = ""
                for i in parts_line[3:]:
                    hub_name += i + "_"
                self.hub_name = hub_name
                self.hub_id = parts_line[2]

            if "Device" in line:
                self.id_dev_arr.append(parts_line[2])

            if parts_line[0] not in {"Hub", "User", "Room", "Device"}:
                if self.hub_id is None:
                    self.get_hub_info()
                else:
                    break

    def write_log(self):
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = date_time.split()[0]
        message = f"[{date_time}] {self.read_serial()}"

        if self.__name_log_file is None:
            self.crete_log_file()

        if self.time_stamp_in_name_log_file:            #разбивка файла по суткам. Происходит в 00:00 часов
            if date not in self.__name_log_file:
                self.crete_log_file()
                self.write_serial("show")

        with open(f"{self.__path}{self.__name_log_file}", 'a') as log:
            log.write(message)

        if self.print_data:
            print(message)

        return message
