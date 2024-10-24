import json
from time import sleep

from create_table_lane import CreateTableLane
from create_table_main import CreateTableMain
from game_type_manager import GameTypesManager, GameTypesManagerError, GameType
from log_management import LogManagement
from config_reader import ConfigReader, ConfigReaderError
from messages_interpreter import MessagesInterpreter
from results_container import ResultsContainerLeague, ResultsContainer
from results_manager import ResultsManager
from socket_manager import SocketManager

class Main():
    def __init__(self):
        self.__log_management = None
        self.__socket_manager: None | SocketManager = None
        self.__results_container: None | ResultsContainer = None
        self.__results_manager: None | ResultsManager = None
        self.__create_table_lane: None | CreateTableLane = None
        self.__create_table_main: None | CreateTableMain = None
        self.__message_interpreter: None | MessagesInterpreter = None
        self.__game_type_manager: None | GameTypesManager = None
        self.__init_program()
        self.__socket_manager.connect("localhost", 3000 )
        self.__loop()

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

            self.__game_type_manager = GameTypesManager()
            game_type: GameType = self.__game_type_manager.get_game_type("Liga 6-osobowa")

            # game_type: GameType = self.__game_type_manager.get_game_type("Zawody")

            # self.__results_container = ResultsContainer(self.__log_management.add_log)
            self.__results_container = ResultsContainerLeague(self.__log_management.add_log)
            # self.__results_container.init_struct(game_type.number_team)

            self.__results_manager = ResultsManager(self.__results_container, game_type, self.__log_management.add_log)

            self.__message_interpreter = MessagesInterpreter(self.__results_manager, self.__log_management.add_log)

            b = json.load(open("table_for_results/lane_table_settings3.json", encoding='utf8'))
            b2 = json.load(open("table_for_results/six_player_league2.json", encoding='utf8'))
            self.__create_table_main = CreateTableMain(self.__results_manager, b2)
            self.__create_table_lane = CreateTableLane(self.__results_manager, b)
        except ConfigReaderError as e:
            self.__log_management.add_log(10, "CNF_READ_ERROR", e.code, e.message)
        except GameTypesManagerError as e:
            self.__log_management.add_log(10, "GTM_READ_ERROR", e.code, e.message)

    def __loop(self):
        while True:
            socket_status = self.__socket_manager.get_connection_status()
            if socket_status == 1:
                recv_code, recv_data = self.__socket_manager.recv()
                if recv_code > 0:
                    self.__message_interpreter.add_messages(recv_data)
                    self.__message_interpreter.interpret_messages()
            elif socket_status == 0:
                if self.__socket_manager.reconnect() < 0:
                    pass
            self.__create_table_main.make_table()
            self.__create_table_lane.make_table()
            sleep(0.5)


Main()
