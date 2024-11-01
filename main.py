import sys
from PyQt6 import QtGui
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout, QSizePolicy, QMessageBox, QStatusBar, \
    QMenuBar

from category_type_manager import CategoryTypesManager, CategoryTypesManagerError
from create_result_table import CreateTableMain, CreateTableLane
from game_type_manager import GameTypesManager, GameTypesManagerError
from gui.logs_section import LogsSection
from gui.players_section import PlayersSectionLeague
from gui.statistics_section import StatisticsSection
from log_management import LogManagement
from config_reader import ConfigReader, ConfigReaderError
from messages_interpreter import MessagesInterpreter
from player_licenses import PlayerLicenses, PlayerLicensesError
from results_container import ResultsContainerLeague, ResultsContainer
from results_manager import ResultsManager

from gui.settings_section import SettingsSection
from gui.game_type_section import GameTypeSection
from gui.socket_selection import SocketSelection
from socket_manager import SocketManager

APP_VERSION = "1.0.1"

class WorkerThread(QThread):
    def __init__(self, log_management: LogManagement, socket_manager: SocketManager, messages_interpreter: MessagesInterpreter,
                 create_table_main: CreateTableMain, create_table_lane: CreateTableLane):
        super().__init__()
        self.__log_management: LogManagement = log_management
        self.__socket_manager: SocketManager = socket_manager
        self.__message_interpreter: MessagesInterpreter = messages_interpreter
        self.__create_table_main: CreateTableMain = create_table_main
        self.__create_table_lane: CreateTableLane = create_table_lane
        self.__running: bool = False

    def run(self):
        self.__log_management.add_log(7, "LOOP_START", "", "Uruchomiono pętlę główną aplikacji", False)
        self.__running = True
        while self.__running:
            socket_status = self.__socket_manager.get_connection_status()
            if socket_status == 1:
                recv_code, recv_data = self.__socket_manager.recv()
                if recv_code > 0:
                    self.__message_interpreter.add_messages(recv_data)
                    self.__message_interpreter.interpret_messages()
                    self.create_table_lane()
                    self.create_table_main()
            self.msleep(250)

    def stop(self):
        self.__log_management.add_log(7, "LOOP_STOP", "", "Zatrzymano pętlę główną aplikacji", False)
        self.__running = False

    def create_table_lane(self):
        self.__create_table_lane.make_table()

    def create_table_main(self):
        self.__create_table_main.make_table()

class Main(QWidget):
    def __init__(self):
        super().__init__()
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
        self.__thread: WorkerThread | None = None
        self.__player_section: None | PlayersSectionLeague = None
        self.__statistics_section: None | StatisticsSection = None

        self.__init_program()
        self.__layout = QGridLayout()
        self.setLayout(self.__layout)
        self.__loop_is_running: bool = False
        self.__button_start: QPushButton = QPushButton("Rozpocznij")
        self.__button_stop: QPushButton = QPushButton("Zatrzymaj")
        self.__column1_layout = QGridLayout()
        self.__column2_layout = QGridLayout()

        self.init_gui()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        reply = QMessageBox.question(self, 'Potwierdź zamknięcie',
                                     'Czy na pewno chcesz zamknąć aplikację?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def __init_program(self):
        """

        :return:
        :logs:  CNF_READ_ERROR (10), CNF_READ (2), START (0)
        """
        self.__log_management = LogManagement()
        self.__log_management.add_log(0, "START", "", "Aplikacja została uruchomiona", False)
        try:
            self.__config = ConfigReader().get_configuration()
            self.__log_management.add_log(2, "CNF_READ", "", "Pobrano konfigurację", False)
            self.__log_management.set_minimum_number_of_lines_to_write(self.__config["minimum_number_of_lines_to_write_in_log_file"])
            self.__player_licenses = PlayerLicenses(self.__config["file_with_licenses_config"], self.__log_management.add_log)
            self.__category_type_manager = CategoryTypesManager(self.__config["file_with_category_types"])

            self.__socket_manager = SocketManager(self.__config["socket_timeout"], self.__log_management.add_log)

            self.__game_type_manager = GameTypesManager()

            self.__create_table_main = CreateTableMain(self.__config["dir_fonts"],
                                                       self.__config["dir_template_main"],
                                                       self.__config["file_output_main"],
                                                       self.__config["dir_instructions_main"],
                                                       self.__log_management.add_log)
            self.__create_table_lane = CreateTableLane(self.__config["dir_fonts"],
                                                       self.__config["dir_template_lane"],
                                                       self.__config["file_output_lane"],
                                                       self.__config["dir_instructions_lane"],
                                                       self.__config["number_of_lanes"],
                                                       self.__log_management.add_log)
        except ConfigReaderError as e:
            self.__log_management.add_log(10, "CNF_READ_ERROR", e.code, e.message, True)
        except GameTypesManagerError as e:
            self.__log_management.add_log(10, "GTM_READ_ERROR", e.code, e.message, True)
        except PlayerLicensesError as e:
            self.__log_management.add_log(10, "PLI_READ_ERROR", e.code, e.message, True)
        except CategoryTypesManagerError as e:
            self.__log_management.add_log(10, "CTM_READ_ERROR", e.code, e.message, True)

    def init_gui(self):
        self.setWindowTitle("Kręgle Live - Klient")
        self.setWindowIcon(QtGui.QIcon('icon/icon.ico'))
        game_type_selection = GameTypeSection(self.__game_type_manager, self.__on_select_game_type)
        settings_section = SettingsSection(
            self.__category_type_manager, self.__on_change_category_type,
            self.__create_table_lane, self.__on_change_table_lane,
            self.__create_table_main, self.__on_change_table_main)
        socket_section = SocketSelection(self.__socket_manager)
        logs_section = LogsSection(self.__log_management)
        self.__statistics_section = StatisticsSection(6)

        column1 = QWidget()
        column1.setLayout(self.__column1_layout)
        column1.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)

        column2 = QWidget()
        column2.setLayout(self.__column2_layout)
        column2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)

        self.__layout.setMenuBar(self.__create_menu_bar())

        self.__column1_layout.addWidget(socket_section, 0, 0)
        self.__column1_layout.addWidget(settings_section, 1, 0)
        self.__column1_layout.addWidget(game_type_selection, 2, 0)
        self.__column1_layout.addWidget(self.__button_start, 3, 0)
        self.__column1_layout.addWidget(self.__statistics_section, 4, 0)
        self.__column1_layout.addWidget(logs_section, 5, 0)

        self.__button_start.setEnabled(False)
        self.__button_start.setToolTip("Aby uruchomić musisz wybrać rodzaj gry")
        self.__button_start.clicked.connect(self.__on_start_loop)
        self.__button_stop.clicked.connect(self.__on_stop_loop)

        self.__layout.addWidget(column1, 0, 0)
        self.__layout.addWidget(column2, 0, 1)

        self.setGeometry(300, 300, 350, 250)
        self.show()

    def __create_menu_bar(self) -> QMenuBar:
        menu_bar = QMenuBar(self)
        licenses_menu = menu_bar.addMenu("Licencje")
        refresh_licenses_action = QAction("Odśwież listę licencji", self)
        refresh_licenses_action.triggered.connect(self.__refresh_licenses)
        licenses_menu.addAction(refresh_licenses_action)

        help_menu = menu_bar.addMenu("Pomoc")
        about_action = QAction("O aplikacji", self)
        about_action.triggered.connect(self.__show_about)
        help_menu.addAction(about_action)

        return menu_bar

    def __show_about(self):
        about_text = (
            f"<h3>Kręgle Live - Klient</h3>"
            f"<p>Wersja: {APP_VERSION}</p>"
            "<p>Aplikacja wykonana w PyQt6.</p>"
        )
        QMessageBox.information(self, "O aplikacji", about_text)

    def __refresh_licenses(self):
        if self.__player_licenses is not None:
            self.__player_licenses.load_licenses()
        if self.__player_section is None:
            return
        self.__player_section.load_data_from_new_category()

    def __on_start_loop(self):
        #TODO: Check nic nie jest None
        try:
            self.__button_start.setParent(None)
            self.__column1_layout.addWidget(self.__button_stop, 3, 0)
            if self.__game_type_manager.game_type is None:
                return
            self.__thread.start()
        except Exception as e:
            print("=", e)

    def __on_stop_loop(self):
        reply = QMessageBox.question(
            self,
            'Zatrzymanie pętli',
            'Czy na pewno chcesz zatrzymać pętlę?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return
        self.__button_stop.setParent(None)
        self.__column1_layout.addWidget(self.__button_start, 3, 0)
        self.__thread.stop()

    def __on_select_game_type(self):
        self.__button_start.setToolTip("")
        self.__button_start.setEnabled(True)
        game_type = self.__game_type_manager.game_type
        if game_type is None:
            return
        self.__log_management.add_log(7, "GTP_SELECT", "", f"Wybrano rodzaj gry: {game_type.name}", False)
        if game_type.type == "league":
            self.__results_container = ResultsContainerLeague(self.__log_management.add_log)
        elif game_type.type == "classic":
            self.__results_container = ResultsContainer(self.__log_management.add_log)

        self.__results_manager = ResultsManager(self.__results_container, game_type, self.__log_management.add_log)
        self.__message_interpreter = MessagesInterpreter(self.__results_manager, self.__config["number_of_lanes"], self.__log_management.add_log)
        self.__create_table_main.add_func_to_get_results(self.__results_manager.get_scores)
        self.__create_table_lane.add_func_to_get_results(self.__results_manager.get_scores_of_players_now_playing)

        self.__statistics_section.set_messages_interpreter(self.__message_interpreter)

        if game_type.type == "league":
            self.__player_section = PlayersSectionLeague(self.__results_manager, game_type, self.__player_licenses)
        elif game_type.type == "classic":
            self.__player_section = None # TODO

        self.__column2_layout.addWidget(self.__player_section, 4, 0)

        self.__thread = WorkerThread(self.__log_management, self.__socket_manager, self.__message_interpreter,
                                     self.__create_table_main, self.__create_table_lane)

    def __on_change_table_lane(self):
        if self.__thread is None:
            return
        self.__thread.create_table_lane()

    def __on_change_table_main(self):
        if self.__thread is None:
            return
        self.__thread.create_table_main()

    def __on_change_category_type(self):
        self.__player_licenses.set_category_type(self.__category_type_manager.get_selected_category_type())
        if self.__player_section is None:
            return
        self.__player_section.load_data_from_new_category()

def main():
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()