from collections.abc import Callable
from PyQt6.QtWidgets import QWidget, QPushButton, QGroupBox, QGridLayout, QLabel, QLineEdit, QStackedLayout, QComboBox, \
    QMessageBox

from game_type_manager import GameTypesManager


class GameTypeSection(QGroupBox):
    """
        TODO: Add comment
    """
    def __init__(self, game_type_manager: GameTypesManager, on_selected_game_type: Callable[[], None]):
        super().__init__("Rodzaj gry")
        self.__game_type_manager: GameTypesManager = game_type_manager
        self.__on_after_selected_game_type: Callable[[], None] = on_selected_game_type

        self.__stacked_layout: QStackedLayout = QStackedLayout()

        self.__layout = QGridLayout()
        self.__label_main: QLabel = QLabel("Rodzaj gry:")
        self.__label_game_type: QLabel = QLabel("")
        self.__combo_game_type: QComboBox = QComboBox()
        self.__button_select: QPushButton = QPushButton("Wybierz")

        self.__set_layout()

    def __set_layout(self):
        """."""
        self.__layout.addWidget(self.__label_main, 0, 0)
        self.__layout.addWidget(self.__combo_game_type, 0, 1)
        self.__layout.addWidget(self.__button_select, 1, 0, 1, 2)
        self.__layout.setColumnStretch(1, 2)

        self.__combo_game_type.addItems(self.__game_type_manager.get_list_game_type_name())
        self.__button_select.clicked.connect(self.__on_selected_game_type)

        self.setLayout(self.__layout)

    def __on_selected_game_type(self):
        selected_option = self.__combo_game_type.currentText()

        reply = QMessageBox.question(
            self,
            'Potwierdzenie wyboru rodzaju gry',
            'Czy na pewno chcesz wybrać ten rodzaj gry?\nNie będzie można zmienić wyboru bez ponownego uruchomienia programu.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        if self.__game_type_manager.select_game_type(selected_option):
            self.__on_after_selected_game_type()
            self.__label_game_type.setText(selected_option)
            self.__layout.addWidget(self.__label_game_type, 0, 1)
            self.__button_select.setParent(None)
            self.__combo_game_type.setParent(None)

    # def __connect(self):

