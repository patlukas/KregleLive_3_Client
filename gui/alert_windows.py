import winsound
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer, Qt


class AlertWindowWithSound(QMessageBox):
    def __init__(self, title: str, message: str):
        super().__init__()
        self.setModal(False)

        self.setWindowTitle(title)
        self.setGeometry(400, 300, 600, 300)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setText(message)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.buttonClicked.connect(self.close_alert)

        self.timer = QTimer()
        self.timer.timeout.connect(self.__play_sound)

    @staticmethod
    def __play_sound():
        winsound.MessageBeep(winsound.MB_ICONHAND)

    def closeEvent(self, event):
        self.close_alert()
        event.accept()

    def show_alert(self):
        self.timer.start(3000)
        self.show()

    def close_alert(self):
        self.timer.stop()
        self.hide()
