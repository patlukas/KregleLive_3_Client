from time import sleep

from category_type_manager import CategoryTypesManager, CategoryTypesManagerError
from create_result_table import CreateTableMain, CreateTableLane
from game_type_manager import GameTypesManager, GameTypesManagerError, GameType
from log_management import LogManagement
from config_reader import ConfigReader, ConfigReaderError
from messages_interpreter import MessagesInterpreter
from player_licenses import PlayerLicenses, PlayerLicensesError
from results_container import ResultsContainerLeague, ResultsContainer
from results_manager import ResultsManager
from socket_manager import SocketManager
import time


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
        self.__player_licenses: None | PlayerLicenses = None
        self.__category_type_manager: None | CategoryTypesManager = None
        self.__init_program()
        self.__socket_manager.connect("localhost", 3000 ) # TODO: To można zrobić tylko jak nie jest None
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
            self.__player_licenses = PlayerLicenses(self.__config["file_with_licenses_config"])
            self.__category_type_manager = CategoryTypesManager(self.__config["file_with_category_types"])
            l = self.__category_type_manager.get_list_category_type_name()
            g = self.__category_type_manager.select_category_type(l[1])
            self.__player_licenses.set_category_type(g)

            self.__socket_manager = SocketManager(self.__config["socket_timeout"], self.__log_management.add_log)

            self.__game_type_manager = GameTypesManager()
            self.__game_type_manager.select_game_type("Liga 6-osobowa")
            game_type: GameType = self.__game_type_manager.game_type
            # game_type: GameType = self.__game_type_manager.get_game_type("Zawody")

            if game_type.type == "league":
                self.__results_container = ResultsContainerLeague(self.__log_management.add_log)
            elif game_type.type == "classic":
                self.__results_container = ResultsContainer(self.__log_management.add_log)

            self.__results_manager = ResultsManager(self.__results_container, game_type, self.__log_management.add_log)

            self.__message_interpreter = MessagesInterpreter(self.__results_manager, self.__log_management.add_log)

            self.__create_table_main = CreateTableMain(self.__results_manager,
                                                       self.__config["dir_fonts"],
                                                       self.__config["dir_template_main"],
                                                       self.__config["file_output_main"],
                                                       self.__config["dir_instructions_main"],
                                                       self.__log_management.add_log)
            self.__create_table_lane = CreateTableLane(self.__results_manager,
                                                       self.__config["dir_fonts"],
                                                       self.__config["dir_template_lane"],
                                                       self.__config["file_output_lane"],
                                                       self.__config["dir_instructions_lane"],
                                                       self.__config["number_of_lanes"],
                                                       self.__log_management.add_log)
        except ConfigReaderError as e:
            self.__log_management.add_log(10, "CNF_READ_ERROR", e.code, e.message)
        except GameTypesManagerError as e:
            self.__log_management.add_log(10, "GTM_READ_ERROR", e.code, e.message)
        except PlayerLicensesError as e:
            self.__log_management.add_log(10, "PLI_READ_ERROR", e.code, e.message)
        except CategoryTypesManagerError as e:
            self.__log_management.add_log(10, "CTM_READ_ERROR", e.code, e.message)

    def __loop(self):
        start_time = time.time()  # Pobierz czas rozpoczęcia
        index = 0
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

            current_time = time.time()  # Aktualny czas
            elapsed_seconds = int(current_time - start_time)  # Czas, który upłynął w sekundach
            if elapsed_seconds > 0 and elapsed_seconds >= 10:
                index = (index + 1) % 2
                self.__create_table_lane.change_instruction(index)
                start_time = current_time
            sleep(0.5)


Main()
