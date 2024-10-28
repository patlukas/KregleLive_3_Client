import sys

from PyQt6.QtWidgets import QWidget, QPushButton, QApplication, QGroupBox, QGridLayout, QLabel, QComboBox, QHBoxLayout

from gui.socket_selection import SocketSelection
from socket_manager import SocketManager


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.__layout = QHBoxLayout()
        self.setLayout(self.__layout)
        self.init_gui()


    def init_gui(self):
        game_type_selection = GameTypeSelection()
        socket_section = SocketSelection(SocketManager(1, lambda a,b,c,d: print(a,b,c,d)))

        column1 = QWidget()
        column1_layout = QGridLayout()
        column1.setLayout(column1_layout)

        column1_layout.addWidget(game_type_selection, 0, 0)
        column1_layout.addWidget(socket_section, 1, 0)
        self.__layout.addWidget(column1)


        self.setGeometry(300, 300, 350, 250)
        self.show()

class GameTypeSelection(QGroupBox):
    """."""

    def __init__(self):
        super().__init__("Wybór rodzaju gry")
        self.__layout = QGridLayout()
        self.__label_types: QLabel | None = None
        self.__label_sequence: QLabel | None = None
        self.__combobox_types: QComboBox | None = None
        self.__combobox_column_sequence: QComboBox | None = None
        self.__button_start: QPushButton | None = None
        self.__button_end: QPushButton | None = None
        self.__label_name_type: QLabel | None = None
        self.__create_widgets()
        self.setLayout(self.__layout)
        self.__layout_to_select_type()

    def __create_widgets(self):
        self.__label_types = QLabel("Rodzaj gry: ")
        self.__label_sequence = QLabel("Jakie kolumny są w pobieranej tabeli z wynikami: ")
        self.__combobox_types = QComboBox()
        self.__combobox_types.addItems(["a", "b"])
        self.__combobox_types.currentTextChanged.connect(lambda x: print("x", x))

        self.__button_start = QPushButton("Rozpocznij")
        self.__button_start.clicked.connect(lambda: print("start"))

        self.__button_end = QPushButton("Zakończ")
        self.__button_end.clicked.connect(lambda: print("stop"))

        self.__label_name_type = QLabel()

        self.__combobox_column_sequence = QComboBox()
        self.__combobox_column_sequence.addItems(
            ["x", "y", "z"]
        )
        self.__combobox_column_sequence.currentTextChanged.connect(
            lambda: print("???")
        )
        self.__combobox_types.setToolTip("Wybór rodzaju gry")
        self.__combobox_column_sequence.setToolTip("Wybór jakie kolumny znajdują się w tabeli")

    def __layout_to_select_type(self):
        """."""
        self.__button_end.setParent(None)
        self.__label_name_type.setParent(None)
        self.__layout.addWidget(self.__label_types, 0, 0)
        self.__layout.addWidget(self.__combobox_types, 0, 1)
        self.__layout.addWidget(self.__label_sequence, 1, 0)
        self.__layout.addWidget(self.__combobox_column_sequence, 1, 1)
        self.__layout.addWidget(self.__button_start, 2, 0, 1, 2)

    def __layout_after_start(self):
        """."""

        self.__button_start.setParent(None)
        self.__combobox_types.setParent(None)
        self.__combobox_column_sequence.setParent(None)
        self.__label_sequence.setParent(None)
        self.__label_types.setParent(None)
        self.__layout.addWidget(self.__label_name_type, 0, 0)
        self.__layout.addWidget(self.__button_end, 0, 1)


def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()