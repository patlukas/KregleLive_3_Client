from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QGroupBox, QGridLayout, QLabel, QLineEdit, QStackedLayout
from socket_manager import SocketManager


class SocketSelection(QGroupBox):
    """
        TODO: Add comment
    """
    def __init__(self, socket_manager: SocketManager):
        super().__init__("Łączenie z serwerem")
        self.__socket_manager: SocketManager = socket_manager

        self.__stacked_layout: QStackedLayout = QStackedLayout()

        self.__widget_connect: QWidget = QWidget()
        self.__layout_connect = QGridLayout()
        self.__label_ip: QLabel = QLabel("IP serwera: ")
        self.__label_port: QLabel = QLabel("Port: ")
        self.__label_info: QLabel = QLabel("")
        self.__line_ip: QLineEdit = QLineEdit()
        self.__line_port: QLineEdit = QLineEdit()
        self.__button_connect: QPushButton = QPushButton("Połącz")

        self.__widget_connected: QWidget = QWidget()
        self.__layout_connected = QGridLayout()
        self.__label_connect_ip: QLabel = QLabel("")
        self.__label_failed: QLabel = QLabel("")
        self.__label_status: QLabel = QLabel("")
        self.__button_disconnect: QPushButton = QPushButton("Rozłącz")

        self.__timer: QTimer = QTimer()
        self.__layout_to_select_type()

    def __layout_to_select_type(self):
        """."""
        self.__button_connect.clicked.connect(self.__connect)
        self.__layout_connect.addWidget(self.__label_ip, 0, 0, Qt.AlignmentFlag.AlignRight)
        self.__layout_connect.addWidget(self.__line_ip, 0, 1)
        self.__layout_connect.addWidget(self.__label_port, 0, 3, Qt.AlignmentFlag.AlignRight)
        self.__layout_connect.addWidget(self.__line_port, 0, 4)
        self.__layout_connect.addWidget(self.__label_info, 1, 0, 1, 4)
        self.__layout_connect.addWidget(self.__button_connect, 1, 4)
        self.__layout_connect.setColumnMinimumWidth(2, 20)
        self.__layout_connect.setColumnStretch(1, 2)
        self.__layout_connect.setColumnStretch(4, 1)
        self.__widget_connect.setLayout(self.__layout_connect)
        self.__stacked_layout.addWidget(self.__widget_connect)

        self.__button_disconnect.clicked.connect(self.__disconnect)
        self.__layout_connected.addWidget(self.__label_connect_ip, 0, 0)
        self.__layout_connected.addWidget(self.__label_failed, 0, 1)
        self.__layout_connected.addWidget(self.__label_status, 1, 0)
        self.__layout_connected.addWidget(self.__button_disconnect, 1, 1)
        self.__widget_connected.setLayout(self.__layout_connected)
        self.__stacked_layout.addWidget(self.__widget_connected)

        self.setLayout(self.__stacked_layout)

        self.__timer.timeout.connect(self.__check_connection)

    def __connect(self):
        ip, port = self.__line_ip.text(), self.__line_port.text()
        status_code, status_comment = self.__socket_manager.connect(ip, port)
        if status_code == 1:
            self.__label_connect_ip.setText(f"Adres serwera {ip}:{port}")
            self.__label_status.setText(f"Status: połączono")
            self.__stacked_layout.setCurrentWidget(self.__widget_connected)
            self.__timer.start(2000)
        else:
            self.__label_info.setText(status_comment)

    def __disconnect(self):
        self.__socket_manager.disconnect()
        self.__stacked_layout.setCurrentWidget(self.__widget_connect)
        self.__label_info.setText("")
        self.__timer.stop()

    def __check_connection(self):
        self.__socket_manager.ping(2.00)
        status = self.__socket_manager.get_connection_status()
        if status == 1:
            self.__label_status.setText(f"Status: połączono")
        else:
            status_reconnect = self.__socket_manager.reconnect()
            self.__label_failed.setText(f"Liczba nieudanych prób połączenia: {self.__socket_manager.number_of_failed_reconnections}")
            if status_reconnect == 1:
                self.__label_status.setStyleSheet("")
                self.__label_status.setText(f"Status: ponownie połączono")
                self.__label_failed.setText("")
            else:
                self.__label_status.setStyleSheet("color: red;")
                self.__label_status.setText(f"Status: nie udane ponowne połączenie")
                self.__label_failed.setText(f"Liczba nieudanych prób połączenia: {self.__socket_manager.number_of_failed_reconnections}")
