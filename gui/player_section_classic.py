from PyQt6.QtWidgets import QGroupBox, QLabel, QPushButton, QComboBox, QGridLayout, QLineEdit, QHBoxLayout, QWidget, \
    QCheckBox
from collections.abc import Callable
from PyQt6.QtCore import Qt

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


class _SectionSelectMethodCalculateTotalSum(QGroupBox):
    def __init__(self, on_select: Callable[[bool], None]):
        super().__init__("Sposób liczenia sumy całkowitej")
        options: list[str] = ["Wynik eliminacji + Wynik z totalizatora", "Wynik z totalizatora"]
        self.__dropdown: QComboBox = QComboBox()
        self.__dropdown.addItems(options)
        self.__dropdown.currentIndexChanged.connect(lambda: on_select(self.__dropdown.currentIndex() == 0))

        self.__layout = QGridLayout()
        self.__layout.addWidget(self.__dropdown, 0, 0)
        self.setLayout(self.__layout)


class _SectionSetName(QGroupBox):
    def __init__(self, name: str, number_player: int, with_previous_result: bool,
                 on_save_players_data: Callable[[list[tuple[str, int, bool]]], None],
                 on_get_players_data: Callable[[], None | list[tuple[str, int, bool]]]):
        super().__init__(name)
        self.__on_save_players_data: Callable[[list[tuple[str, int, bool]]], None] = on_save_players_data
        self.__on_get_players_data: Callable[[], None | list[tuple[str, int, bool]]] = on_get_players_data
        self.__with_previous_result: bool = with_previous_result
        self.__list_row: list[tuple[QLabel, QComboBox, QLineEdit, QCheckBox]] = []
        self.__buttons: QWidget = QWidget()
        layout_buttons: QHBoxLayout = QHBoxLayout()
        self.__buttons.setLayout(layout_buttons)
        self.__btn_save: QPushButton = QPushButton("Zapisz")
        self.__btn_save.clicked.connect(self.__on_save)
        self.__btn_cancel: QPushButton = QPushButton("Anuluj")
        self.__btn_cancel.clicked.connect(self.load_players_data)
        layout_buttons.addWidget(self.__btn_save)
        layout_buttons.addWidget(self.__btn_cancel)
        self.__layout = QGridLayout()
        self.__number_players = number_player

        label_name = QLabel("Nazwisko i imię")
        label_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__layout.addWidget(label_name, 0, 2)

        if self.__with_previous_result:
            label_previous_result = QLabel("Wynik eliminacji")
            label_previous_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__layout.addWidget(label_previous_result, 0, 2)

        for i in range(number_player):
            label = QLabel(f"Tor {i+1}")
            dropdown: QComboBox = QComboBox()
            line_previous_result: QLineEdit = QLineEdit()
            checkbox_is_player: QCheckBox = QCheckBox()
            dropdown.setEditable(True)
            self.__layout.addWidget(label, i+1, 0)
            self.__layout.addWidget(checkbox_is_player, i+1, 1)
            self.__layout.addWidget(dropdown, i+1, 2)
            if self.__with_previous_result:
                line_previous_result.setFixedWidth(90)
                self.__layout.addWidget(line_previous_result, i+1, 3)
            dropdown.currentIndexChanged.connect(self.__check_is_new_value)
            dropdown.currentTextChanged.connect(self.__check_is_new_value)
            line_previous_result.textChanged.connect(self.__check_is_new_value)
            checkbox_is_player.stateChanged.connect(self.__checkbox_state_changed)
            self.__list_row.append((label, dropdown, line_previous_result, checkbox_is_player))
        self.__layout.addWidget(self.__buttons, self.__number_players + 1, 0, 1, 4)
        self.__on_disable_buttons()
        self.setLayout(self.__layout)

    def refresh_list_players(self, list_players):
        buttons_is_visible = self.__buttons.isVisible()
        for _, dropdown, _, _ in self.__list_row:
            name = dropdown.currentText()
            dropdown.clear()
            dropdown.addItems(list_players)
            dropdown.setCurrentText(name)
        if not buttons_is_visible:
            self.__on_disable_buttons()

    def __on_save(self):
        list_player_data = []
        for _, dropdown, line_previous_result, checkbox_is_player in self.__list_row:
            name = dropdown.currentText()
            previous_result = line_previous_result.text()
            show_player_in_lane_table = checkbox_is_player.isChecked()
            try:
                previous_result_int = int(previous_result)
            except (ValueError, TypeError):
                previous_result_int = 0
            list_player_data.append((name, previous_result_int, show_player_in_lane_table))
        self.__on_save_players_data(list_player_data)
        self.__on_disable_buttons()

    def load_players_data(self):
        list_player_data: list[tuple[str, int, bool]] = self.__on_get_players_data()
        if list_player_data is None:
            return
        for i, [name, previous_result, show_player_in_lane_table] in enumerate(list_player_data):
            self.__list_row[i][1].setCurrentText(name)
            self.__list_row[i][2].setText(str(previous_result))
            self.__list_row[i][3].setChecked(show_player_in_lane_table)
            if show_player_in_lane_table:
                self.__layout.addWidget(self.__list_row[i][1], i + 1, 2)
                if self.__with_previous_result:
                    self.__layout.addWidget(self.__list_row[i][2], i + 1, 3)
            else:
                self.__list_row[i][1].setParent(None)
                self.__list_row[i][2].setParent(None)
        self.__on_disable_buttons()

    def __on_disable_buttons(self):
        self.__btn_save.setEnabled(False)
        self.__btn_cancel.setEnabled(False)

    def __on_enable_buttons(self):
        self.__btn_save.setEnabled(True)
        self.__btn_cancel.setEnabled(True)

    def __check_is_new_value(self):
        list_player_data: list[tuple[str, int, bool]] = self.__on_get_players_data()
        if list_player_data is None:
            return
        for i, [name, previous_result, show_player_in_lane_table] in enumerate(list_player_data):
            name_in_form = self.__list_row[i][1].currentText()
            previous_result_in_form = self.__list_row[i][2].text()
            show_player_in_lane_table_in_form = self.__list_row[i][3].isChecked()
            if (not show_player_in_lane_table_in_form and show_player_in_lane_table) or (show_player_in_lane_table_in_form and not show_player_in_lane_table):
                self.__on_enable_buttons()
                return
            if not show_player_in_lane_table:
                continue
            if name != name_in_form or str(previous_result) != previous_result_in_form:
                self.__on_enable_buttons()
                return
        self.__on_disable_buttons()

    def __checkbox_state_changed(self):
        for i, (_, dropdown, line_previous_result, checkbox_is_player) in enumerate(self.__list_row):
            if checkbox_is_player.isChecked():
                self.__layout.addWidget(dropdown, i + 1, 2)
                if self.__with_previous_result:
                    self.__layout.addWidget(line_previous_result, i + 1, 3)
            else:
                dropdown.setParent(None)
                line_previous_result.setParent(None)
        self.__check_is_new_value()


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
        self.__with_previous_result: bool = game_type.with_previous_result

        self.__section_select_method_calculate_total_sum: _SectionSelectMethodCalculateTotalSum = _SectionSelectMethodCalculateTotalSum(self.__results_manager.set_method_of_calculate_total_sum)
        self.__section_next_set_name: _SectionSetName = _SectionSetName(
            "Następny blok",
            self.__number_player_in_period,
            self.__with_previous_result,
            lambda list_player_data: self.__set_players_data_in_relative_block(1, list_player_data),
            lambda: self.__get_players_data_in_relative_block(1)
        )
        self.__section_now_set_name: _SectionSetName = _SectionSetName(
            "Aktualny blok",
            self.__number_player_in_period,
            self.__with_previous_result,
            lambda list_player_data: self.__set_players_data_in_relative_block(0, list_player_data),
            lambda: self.__get_players_data_in_relative_block(0)
        )
        self.__section_next_select_block: _SectionChooseTransition = _SectionChooseTransition("Następny blok", self.__transitions, self.__select_transition)

        self.__layout = QGridLayout()
        if self.__with_previous_result:
            self.__layout.addWidget(self.__section_select_method_calculate_total_sum, 0, 0, 1, 2)
        self.__layout.addWidget(self.__section_now_set_name, 1, 0)
        self.__layout.addWidget(self.__section_next_set_name, 1, 1)
        self.__layout.addWidget(self.__section_next_select_block, 1, 1)
        self.setLayout(self.__layout)

        self.on_after_new_block()
        self.load_data_from_new_category()

    def __select_transition(self, transition: str):
        self.__results_manager.add_block(transition)
        self.__section_next_set_name.load_players_data()
        if self.__results_manager.get_number_of_blocks() == 1:
            self.__section_now_set_name.setParent(None)
            self.__layout.addWidget(self.__section_next_set_name, 1, 1)
            self.__section_next_select_block.setParent(None)
        else:
            self.__layout.addWidget(self.__section_now_set_name, 1, 0)
            self.__layout.addWidget(self.__section_next_set_name, 1, 1)
            self.__section_next_select_block.setParent(None)

    def on_after_new_block(self):
        if len(self.__transitions) > 1:
            if self.__results_manager.get_number_of_blocks() == 0:
                self.__section_now_set_name.setParent(None)
                self.__section_next_set_name.setParent(None)
                self.__layout.addWidget(self.__section_next_select_block, 1, 1)
            else:
                self.__layout.addWidget(self.__section_now_set_name, 1, 0)
                self.__section_next_set_name.setParent(None)
                self.__layout.addWidget(self.__section_next_select_block, 1, 1)
        else:
            self.__select_transition(self.__transitions[0])
        self.__section_now_set_name.load_players_data()

    def load_data(self):
        self.__section_now_set_name.load_players_data()

    def load_data_from_new_category(self):
        list_payers = self.__player_licenses.get_list_players_name(None)
        self.__section_now_set_name.refresh_list_players(list_payers)
        self.__section_next_set_name.refresh_list_players(list_payers)

    def __set_players_data_in_relative_block(self, relative_block: int, list_data: list[tuple[str, int, bool]]) -> None:
        for i, [name, previous_sum, show_player_in_lane_table] in enumerate(list_data):
            self.__results_manager.set_player_name_in_relative_block(0, i, relative_block, name)
            self.__results_manager.set_player_previous_sum_in_relative_block(0, i, relative_block, previous_sum)
            self.__results_manager.set_show_player_in_lane_table_in_relative_block(0, i, relative_block, show_player_in_lane_table)
        self.__on_refresh_tables()

    def __get_players_data_in_relative_block(self, relative_block: int) -> list[tuple[str, int, bool]] | None:
        list_data = []
        for i in range(self.__number_player_in_period):
            name = self.__results_manager.get_player_name_in_relative_block(0, i, relative_block)
            previous_sum = self.__results_manager.get_player_previous_sum_in_relative_block(0, i, relative_block)
            show_player_in_lane_table = self.__results_manager.get_show_player_in_lane_table_in_relative_block(0, i, relative_block)
            if name is None or previous_sum is None or show_player_in_lane_table is None:
                return None
            list_data.append((name, previous_sum, show_player_in_lane_table))
        return list_data
