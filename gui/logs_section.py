from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QStackedLayout, QPushButton, QTableWidget, QTableWidgetItem

from log_management import LogManagement

class LogsSection(QGroupBox):
    """
        TODO: Add comment
    """
    def __init__(self, log_management: LogManagement):
        super().__init__("Logi")
        self.__log_management: LogManagement = log_management
        self.__show_list_logs: bool = False

        self.__layout = QGridLayout()

        self.__label_number_error: QLabel = QLabel("Liczba błędów: 0")
        self.__label_number_logs: QLabel = QLabel("Liczba logów: 0")
        self.__btn_show_list_logs: QPushButton = QPushButton("Pokaż listę logów")
        self.__btn_hide_list_logs: QPushButton = QPushButton("Ukryj listę logów")

        self.__table_logs = QTableWidget()
        self.__timer: QTimer = QTimer()

        self.__set_layout()
        self.update_logs()

    def __set_layout(self):
        font = QFont()
        font.setPointSize(8)

        self.__btn_show_list_logs.clicked.connect(self.__on_show_list_logs)
        self.__btn_hide_list_logs.clicked.connect(self.__on_hide_list_logs)

        self.__table_logs.setRowCount(0)
        self.__table_logs.setColumnCount(6)
        self.__table_logs.setHorizontalHeaderLabels(["Id", "Godzina", "Priorytet", "Kod", "Port", "Wiadomość"])
        self.__table_logs.verticalHeader().setVisible(False)
        self.__table_logs.setFont(font)
        self.__table_logs.resizeColumnsToContents()

        self.__layout.addWidget(self.__label_number_error, 0, 0)
        self.__layout.addWidget(self.__label_number_logs, 0, 1)
        self.__layout.addWidget(self.__btn_show_list_logs, 0, 2)
        self.__table_logs.setFixedHeight(130)

        self.setLayout(self.__layout)
        self.__timer.timeout.connect(self.update_logs)
        self.__timer.start(1000)

    def update_logs(self):
        data = self.__log_management.get_logs(0, 250, 100)
        number_of_errors = 0
        for index, log in enumerate(data):
            if int(log[2]) == 10:
                number_of_errors += 1
        self.__label_number_error.setText(f"Liczba błędów: {number_of_errors}")
        self.__label_number_logs.setText(f"Liczba logów: {len(data)}")

        if self.__show_list_logs:
            self.__table_logs.setRowCount(0)
            font = QFont()
            font.setPointSize(7)
            for index, log in enumerate(data):
                if int(log[2]) == 10:
                    number_of_errors += 1
                self.__table_logs.insertRow(index)
                for j, val in enumerate(log):
                    item = QTableWidgetItem(str(val))
                    item.setFont(font)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    self.__table_logs.setItem(index, j, item)
                    if int(log[2]) == 10:
                        item.setBackground(QtGui.QColor(128, 0, 0))
                    elif int(log[2]) >= 7:
                        item.setBackground(QtGui.QColor(0, 0, 128))
            self.__table_logs.resizeColumnsToContents()

    def __on_show_list_logs(self):
        self.__show_list_logs = True
        self.__layout.addWidget(self.__table_logs, 1, 0, 1, 3)
        self.__layout.addWidget(self.__btn_hide_list_logs, 0, 2)
        self.__btn_show_list_logs.setParent(None)
        self.update_logs()

    def __on_hide_list_logs(self):
        self.__show_list_logs = False
        self.__table_logs.setParent(None)
        self.__layout.addWidget(self.__btn_show_list_logs, 0, 2)
        self.__btn_hide_list_logs.setParent(None)
