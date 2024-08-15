from log_management import LogManagement
from config_reader import ConfigReader, ConfigReaderError
from socket_manager import SocketManager

class Main():
    def __init__(self):
        self.__log_management = None
        self.__socket_manager = None
        self.__init_program()

    def __init_program(self):
        """

        :return:
        :logs:  CNF_READ_ERROR (10), CNF_READ (2), START (0)
        """
        self.__log_management = LogManagement()
        self.__log_management.add_log(0, "START", "", "Aplikacja została uruchomiona")

        try:
            self.__config = ConfigReader().get_configuration()
            self.__log_management.add_log(2, "CNF_READ", "", "Pobrano konfigurację")
            self.__log_management.set_minimum_number_of_lines_to_write(
                self.__config["minimum_number_of_lines_to_write_in_log_file"]
            )

            self.__socket_manager = SocketManager(self.__config["socket_timeout"], self.__log_management.add_log)
        except ConfigReaderError as e:
            self.__log_management.add_log(10, "CNF_READ_ERROR", e.code, e.message)

    def __loop(self):
        while True:
            socket_status = self.__socket_manager.get_connection_status()
            if socket_status == 1:
                recv_code, recv_data = self.__socket_manager.recv()
                if recv_code > 0:
                    pass
                    #recv
            elif socket_status == 0:
                if self.__socket_manager.reconnect() < 0:
                    pass
                    #sleep


Main()
