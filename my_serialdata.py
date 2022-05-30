import serial
import re
from my_logging import Logging


class SerialData(Logging):

    def __init__(self):
        Logging.__init__(self)
        self.__port = None
        self.__speed = None
        self.__serial_port = None
        self.__autolog = True
        self.__print_data = False

    def close_port(self):
        self.__serial_port.close()

    def set_autolog(self, flag: bool):
        self.__autolog = flag

    def set_print_data(self, flag: bool):
        self.__print_data = flag

    def get_port(self):
        return self.__port

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
        if self.__autolog:
            self.write_log(line)
        if self.__print_data:
            print(line)
        return line

    def write_serial(self, message: str):
        self.__serial_port.write((message + "\r\n").encode('UTF-8'))


class Hub(SerialData):
    def __init__(self):
        SerialData.__init__(self)
        self.hub_id = None
        self.hub_name = None
        self.frame = 0
        self.relay_norm_id = None
        self.relay_low_id = None
        self.socket_id = None
        self.id_dev_arr = []
