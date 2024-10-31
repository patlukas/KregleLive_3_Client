from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView

from messages_interpreter import MessagesInterpreter


class StatisticsSection(QGroupBox):
    """
        TODO: Add comment
    """
    def __init__(self, number_of_lanes: int):
        super().__init__("Statystyki")
        self.__number_of_lanes: int = number_of_lanes
        self.__messages_interpreter: MessagesInterpreter | None = None
        self.__show_table_stat: bool = False

        self.__layout = QGridLayout()

        self.__label_number_unrecognized: QLabel = QLabel("Liczba nieraozpoznanych wiadomości: 0")
        self.__btn_show_list_stat: QPushButton = QPushButton("Pokaż szczegóły")
        self.__btn_hide_list_stat: QPushButton = QPushButton("Ukryj szczegóły")

        self.__table_stat = QTableWidget()
        self.__table_list_cells: list[list[QTableWidgetItem]] = []
        self.__timer: QTimer = QTimer()

        self.__set_layout()
        self.update_logs()

    def set_messages_interpreter(self, messages_interpreter: MessagesInterpreter):
        self.__messages_interpreter: MessagesInterpreter = messages_interpreter

    def __set_layout(self):
        font = QFont()
        font.setPointSize(8)

        self.__btn_show_list_stat.clicked.connect(self.__on_show_list_logs)
        self.__btn_hide_list_stat.clicked.connect(self.__on_hide_list_logs)

        list_col = [""] + [f"Tor {i+1}" for i in range(self.__number_of_lanes)] + ["∑"]

        self.__table_stat.setColumnCount(len(list_col))
        self.__table_stat.setHorizontalHeaderLabels(list_col)
        self.__table_stat.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(1, 8):
            self.__table_stat.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.__table_stat.verticalHeader().setVisible(False)
        self.__table_stat.setFont(font)
        height = self.__table_stat.horizontalHeader().height()
        for i, name in enumerate(["Od", "Do", "∑"]):
            list_item = []
            self.__table_stat.insertRow(i)
            height += self.__table_stat.rowHeight(i)
            self.__table_stat.setItem(i, 0, QTableWidgetItem(name))
            for j in range(self.__number_of_lanes + 1):
                item = QTableWidgetItem("0")
                item.setFont(font)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                list_item.append(item)
                self.__table_stat.setItem(i, 1 + j, item)
            self.__table_list_cells.append(list_item)

        self.__layout.addWidget(self.__label_number_unrecognized, 0, 0)
        self.__layout.addWidget(self.__btn_show_list_stat, 0, 1)
        self.__table_stat.setFixedHeight(height + 2 * self.__table_stat.frameWidth())

        self.setLayout(self.__layout)
        self.__timer.timeout.connect(self.update_logs)
        self.__timer.start(1000)

    def update_logs(self):
        if self.__messages_interpreter is None:
            return
        number_of_unrecognized = self.__messages_interpreter.get_number_of_unrecognized_messages()
        self.__label_number_unrecognized.setText(f"Liczba nieraozpoznanych wiadomości: {number_of_unrecognized}")
        if not self.__show_table_stat:
            return
        data = self.__messages_interpreter.get_statistics()
        for i, row in enumerate(self.__table_list_cells):
            for j, item in enumerate(row):
                item.setText(str(data[i][j]))
        # self.__table_stat.resizeColumnsToContents()

    def __on_show_list_logs(self):
        self.__show_table_stat = True
        self.__layout.addWidget(self.__table_stat, 1, 0, 1, 2)
        self.__layout.addWidget(self.__btn_hide_list_stat, 0, 1)
        self.__btn_show_list_stat.setParent(None)
        self.update_logs()

    def __on_hide_list_logs(self):
        self.__show_table_stat = False
        self.__table_stat.setParent(None)
        self.__layout.addWidget(self.__btn_show_list_stat, 0, 1)
        self.__btn_hide_list_stat.setParent(None)
