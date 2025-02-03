from PyQt6.QtWidgets import QGroupBox, QLabel, QPushButton, QComboBox, QGridLayout
from collections.abc import Callable

from game_type_manager import GameType
from player_licenses import PlayerLicenses
from results_manager import ResultsManager


class _SectionChooseTransition(QGroupBox):
    def __init__(self, name: str, list_transitions: list[str], on_select_transition: Callable[[str], None]):
        super().__init__(name)
        self.__list_transitions: list[str] = list_transitions
        self.__label: QLabel = QLabel("Rodzaj bloku")
        self.__dropdown: QComboBox = QComboBox()
        self.__btn: QPushButton = QPushButton("Wybierz")
        self.__dropdown.addItems(list_transitions)
        self.__btn.clicked.connect(lambda: on_select_transition(self.__dropdown.currentText()))

        self.__layout = QGridLayout()
        self.__layout.addWidget(self.__label, 0, 0)
        self.__layout.addWidget(self.__dropdown, 0, 1)
        self.__layout.addWidget(self.__btn, 0, 2)
        self.setLayout(self.__layout)


class _SectionSetName(QGroupBox):
    def __init__(self, name: str, number_player: int, on_save_names: Callable[[list[str]], None], on_get_names: Callable[[], None | list[str]]):
        super().__init__(name)
        self.__on_save_names: Callable[[list[str]], None] = on_save_names
        self.__on_get_names: Callable[[], None | list[str]] = on_get_names
        self.__list_row: list[tuple[QLabel, QComboBox]] = []
        self.__btn: QPushButton = QPushButton("Zapisz")
        self.__btn.clicked.connect(self.__on_save)
        self.__layout = QGridLayout()

        for i in range(number_player):
            l = QLabel(f"Tor {i+1}")
            d: QComboBox = QComboBox()
            d.setEditable(True)
            self.__layout.addWidget(l, i, 0)
            self.__layout.addWidget(d, i, 1)
            self.__list_row.append((l, d))

        self.__layout.addWidget(self.__btn, number_player, 1)
        self.setLayout(self.__layout)

    def refresh_list_players(self, list_players):
        for _, dropdown in self.__list_row:
            dropdown.clear()
            dropdown.addItems(list_players)

    def __on_save(self):
        list_name = []
        for _, dropdown in self.__list_row:
            list_name.append(dropdown.currentText())
        self.__on_save_names(list_name)

    def load_players_data(self):
        list_name = self.__on_get_names()
        if list_name is None:
            return
        for i, name in enumerate(list_name):
            self.__list_row[i][1].setCurrentText(name)


class PlayersSectionClassic(QGroupBox):
    """
        TODO: Add comment
    """
    def __init__(self, results_manager: ResultsManager, game_type: GameType, player_licenses: PlayerLicenses,
                 on_refresh_tables: Callable[[], None]):
        super().__init__("Ustawianie nazw")
        self.__on_refresh_tables: Callable[[], None] = on_refresh_tables
        self.__results_manager: ResultsManager = results_manager
        self.__player_licenses: PlayerLicenses = player_licenses
        self.__transitions: list[str] = game_type.get_list_transitions_name()
        self.__default_transitions: str = game_type.default_transitions
        self.__number_player_in_period: int = game_type.number_player_in_team_in_period


        self.__section_next_set_name: _SectionSetName = _SectionSetName(
            "Następny blok",
            self.__number_player_in_period,
            lambda list_name: self.__set_players_names_in_relative_block(1, list_name),
            lambda: self.__get_players_names_in_relative_block(1)
        )
        self.__section_now_set_name: _SectionSetName = _SectionSetName(
            "Aktualny blok",
            self.__number_player_in_period,
            lambda list_name: self.__set_players_names_in_relative_block(0, list_name),
            lambda: self.__get_players_names_in_relative_block(0)
        )
        self.__section_next_select_block: _SectionChooseTransition = _SectionChooseTransition("Następny blok", self.__transitions, self.__select_transition)

        self.__layout = QGridLayout()
        self.__layout.addWidget(self.__section_now_set_name, 0, 0)
        self.__layout.addWidget(self.__section_next_set_name, 0, 1)
        self.__layout.addWidget(self.__section_next_select_block, 0, 1)
        self.setLayout(self.__layout)

        self.on_after_new_block()
        self.load_data_from_new_category()

    def __select_transition(self, transition: str):
        self.__results_manager.add_block(transition)
        self.__section_next_set_name.load_players_data()
        if self.__results_manager.get_number_of_blocks() == 1:
            self.__section_now_set_name.setParent(None)
            self.__layout.addWidget(self.__section_next_set_name, 0, 1)
            self.__section_next_select_block.setParent(None)
        else:
            self.__layout.addWidget(self.__section_now_set_name, 0, 0)
            self.__layout.addWidget(self.__section_next_set_name, 0, 1)
            self.__section_next_select_block.setParent(None)

    def on_after_new_block(self):
        if len(self.__transitions) > 1:
            if self.__results_manager.get_number_of_blocks() == 0:
                self.__section_now_set_name.setParent(None)
                self.__section_next_set_name.setParent(None)
                self.__layout.addWidget(self.__section_next_select_block, 0, 1)
            else:
                self.__layout.addWidget(self.__section_now_set_name, 0, 0)
                self.__section_next_set_name.setParent(None)
                self.__layout.addWidget(self.__section_next_select_block, 0, 1)
        else:
            self.__select_transition(self.__transitions[0])
        self.__section_now_set_name.load_players_data()

    def load_data_from_new_category(self):
        list_payers = self.__player_licenses.get_list_players_name(None)
        self.__section_now_set_name.refresh_list_players(list_payers)
        self.__section_next_set_name.refresh_list_players(list_payers)

    def __set_players_names_in_relative_block(self, relative_block: int, list_name: list[str]) -> None:
        for i, name in enumerate(list_name):
            r = self.__results_manager.set_player_name_in_relative_block(0, i, relative_block, name)
            print(i, name, relative_block, r)

    def __get_players_names_in_relative_block(self, relative_block: int) -> list[str] | None:
        list_name = []
        for i in range(self.__number_player_in_period):
            name = self.__results_manager.get_player_name_in_relative_block(0, i, relative_block)
            if name is None:
                return None
            list_name.append(name)
        return list_name

