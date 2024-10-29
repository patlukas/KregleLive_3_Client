import sys

from PyQt6.QtWidgets import QWidget, QPushButton, QApplication, QGroupBox, QGridLayout, QLabel, QComboBox, QHBoxLayout

from category_type_manager import CategoryTypesManager
from game_type_manager import GameTypesManager
from gui.game_type_section import GameTypeSection
from gui.category_type_section import MainSection
from gui.socket_selection import SocketSelection
from socket_manager import SocketManager


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.__layout = QHBoxLayout()
        self.setLayout(self.__layout)
        self.init_gui()


    def init_gui(self):
        game_type_selection = GameTypeSection(GameTypesManager(), lambda: print("Sukces"))
        # game_type_selection = MainSection(GameTypesManager(), CategoryTypesManager("settings/category_types.json"))
        socket_section = SocketSelection(SocketManager(1, lambda a,b,c,d: print(a,b,c,d)))

        column1 = QWidget()
        column1_layout = QGridLayout()
        column1.setLayout(column1_layout)

        column1_layout.addWidget(socket_section, 0, 0)
        column1_layout.addWidget(game_type_selection, 1, 0)

        self.__layout.addWidget(column1)


        self.setGeometry(300, 300, 350, 250)
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()