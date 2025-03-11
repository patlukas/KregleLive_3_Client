from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QStackedLayout, QComboBox, QPushButton
from collections.abc import Callable

from game_type_manager import GameType
from gui.custom_widgets import QLineEditWithHistory, QComboBoxWithHistory, QCheckableGroupBoxWithHistory
from player_licenses import PlayerLicenses
from results_manager import ResultsManager


class _PlayersSectionLeagueTeam:
    def __init__(self, widget: QGroupBox, layout: QGridLayout, filter_team: QComboBox, team: QLineEditWithHistory):
        self.widget: QGroupBox = widget
        self.layout: QGridLayout = layout
        self.filter_team: QComboBox = filter_team
        self.team: QLineEditWithHistory = team
        self.list_players: list[QComboBoxWithHistory] = []
        self.list_changes: list[_PlayersSectionLeagueChanges] = []


class _PlayersSectionLeagueChanges:
    def __init__(self, widget: QCheckableGroupBoxWithHistory, player_out: QComboBoxWithHistory,
                 player_in: QComboBoxWithHistory, number_throw: QLineEditWithHistory):
        self.widget: QCheckableGroupBoxWithHistory = widget
        self.player_out: QComboBoxWithHistory = player_out
        self.player_in: QComboBoxWithHistory = player_in
        self.number_throw: QLineEditWithHistory = number_throw


class PlayersSectionLeague(QGroupBox):
    def __init__(self, results_manager: ResultsManager, game_type: GameType, player_licenses: PlayerLicenses,
                 on_refresh_tables: Callable[[], None]):
        super().__init__("Ustawianie nazw")
        self.__on_refresh_tables: Callable[[], None] = on_refresh_tables
        self.__results_manager: ResultsManager = results_manager
        self.__player_licenses: PlayerLicenses = player_licenses

        self.__stacked_layout: QStackedLayout = QStackedLayout()

        players_in_team = game_type.number_player_in_team_in_period * game_type.number_periods
        self.__columns = [
            self.__generate_column_widget("Gospodarze", players_in_team, game_type.number_of_changes),
            self.__generate_column_widget("Goście", players_in_team, game_type.number_of_changes)
        ]
        self.__button_save: QPushButton = QPushButton("Zapisz")
        self.__button_cancel: QPushButton = QPushButton("Anuluj")
        self.__layout = QGridLayout()
        self.__layout.addWidget(self.__columns[0].widget, 0, 0, 1, 2)
        self.__layout.addWidget(self.__columns[1].widget, 0, 2, 1, 2)
        self.__layout.addWidget(self.__button_save, 1, 1)
        self.__layout.addWidget(self.__button_cancel, 1, 2)
        self.__button_save.clicked.connect(self.__on_save_names)
        self.__button_cancel.clicked.connect(self.__on_cancel)
        self.__button_save.setEnabled(False)
        self.__button_cancel.setEnabled(False)

        self.setLayout(self.__layout)
        self.load_data_from_new_category()

    def __generate_column_widget(self, name: str, number_players: int, number_changes: int):
        x = _PlayersSectionLeagueTeam(QGroupBox(name), QGridLayout(), QComboBox(), QLineEditWithHistory(self.__check_are_new_values))
        x.widget.setLayout(x.layout)
        x.layout.addWidget(QLabel("Filtr drużyn"), 0, 0)
        x.layout.addWidget(x.filter_team, 0, 1)
        x.filter_team.currentTextChanged.connect(lambda: self.__after_select_team(x))

        x.layout.addWidget(QLabel("Nazwa drużyny"), 1, 0)
        x.layout.addWidget(x.team, 1, 1)

        row = 1
        list_players_title = [f"Gracz {i+1}" for i in range(number_players)]
        for title in list_players_title:
            row += 1
            player = QComboBoxWithHistory(self.__check_are_new_values)
            x.layout.addWidget(QLabel(title), row, 0)
            x.layout.addWidget(player, row, 1)
            x.list_players.append(player)
            player.setEditable(True)

        for i in range(number_changes):
            row += 1
            change_box = QCheckableGroupBoxWithHistory(f"Zmiana {i + 1}", self.__check_are_new_values, False)
            change_layout = QGridLayout()
            change_box.setLayout(change_layout)

            player_out = QComboBoxWithHistory(lambda: {print("EE"), self.__check_are_new_values()}, list_players_title)
            player_in = QComboBoxWithHistory(self.__check_are_new_values)
            number_throw = QLineEditWithHistory(self.__check_are_new_values)
            number_throw.setFixedWidth(40)
            player_in.setEditable(True)

            change_layout.addWidget(QLabel(f"Kto schodzi"), 0, 0)
            change_layout.addWidget(player_out, 0, 1)

            change_layout.addWidget(QLabel(f"Kiedy zmiena"), 0, 2)
            change_layout.addWidget(number_throw, 0, 3)
            change_layout.addWidget(QLabel(f"Kto wchodzi"), 1, 0)
            change_layout.addWidget(player_in, 1, 1, 1, 3)

            x.layout.addWidget(change_box, row, 0, 1, 2)
            x.list_changes.append(_PlayersSectionLeagueChanges(change_box, player_out, player_in, number_throw))
        return x

    def __check_are_new_values(self):
        are_new_values = self.__check_are_new_values__checking()
        self.__button_save.setEnabled(are_new_values)
        self.__button_cancel.setEnabled(are_new_values)

    def __check_are_new_values__checking(self):
        for column in self.__columns:
            if column.team.is_new_value():
                return True
            for player in column.list_players:
                if player.is_new_value():
                    return True
            for change in column.list_changes:
                if change.widget.is_new_value():
                    return True
                if change.player_out.is_new_value():
                    return True
                if change.player_in.is_new_value():
                    return True
                if change.number_throw.is_new_value():
                    return True
        return False

    def __on_cancel(self):
        for team_index, column in enumerate(self.__columns):
            column.team.rollback_value()

            for player in column.list_players:
                player.rollback_value()

            for change in column.list_changes:
                change.widget.rollback_value()
                change.player_out.rollback_value()
                change.player_in.rollback_value()
                change.number_throw.rollback_value()

    def load_data(self):
        pass # TODO #17

    def load_data_from_new_category(self):
        list_team = self.__player_licenses.get_teams()
        for i, column in enumerate(self.__columns):
            column.filter_team.blockSignals(True)
            column.filter_team.clear()
            column.filter_team.addItems(list_team)
            column.filter_team.blockSignals(False)
            self.__set_list_of_players(column, None)

    def __set_list_of_players(self, column: _PlayersSectionLeagueTeam, team: str | None):
        list_players = self.__player_licenses.get_list_players_name(team)
        if team is not None:
            column.team.setText(team)
        for player in column.list_players:
            old_text = player.currentText()
            player.clear()
            player.addItems(list_players)
            if team is None or old_text in list_players:
                player.setEditText(old_text)
        for change in column.list_changes:
            old_text = change.player_in.currentText()
            change.player_in.clear()
            change.player_in.addItems(list_players)
            if team is None or old_text in list_players:
                change.player_in.setEditText(old_text)

    def __after_select_team(self, x: _PlayersSectionLeagueTeam):
        team_filter = x.filter_team.currentText()
        self.__set_list_of_players(x, team_filter)

    def __on_save_names(self):
        for team_index, column in enumerate(self.__columns):
            column.team.save_value()
            self.__results_manager.set_team_name(team_index, column.team.text())

            list_players = []
            for player in column.list_players:
                player.save_value()
                list_players.append([(player.currentText(), 0)])
            for change in column.list_changes:
                change.widget.save_value()
                change.player_out.save_value()
                change.player_in.save_value()
                change.number_throw.save_value()

                if change.widget.isChecked():
                    index = change.player_out.currentIndex()
                    player_in = change.player_in.currentText()
                    throw = change.number_throw.text()
                    try:
                        throw_int = int(throw)
                    except ValueError:
                        throw_int = 60
                    list_players[index].append((player_in, throw_int))
            for i, player in enumerate(list_players):
                self.__results_manager.set_player_list_name(team_index, i, player)
        self.__check_are_new_values()
        self.__on_refresh_tables()
