from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt



class SplashScreen:
    def __init__(self, version: str):
        self.pixmap = QPixmap("icon/splash.png")
        self.__splash_screen: QSplashScreen = QSplashScreen(self.pixmap)

        self.__splash_screen.setFont(QFont("Arial", 16))
        self.__splash_screen.showMessage(f"v. {version}", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, QColor("white"))

        self.__splash_screen.show()

    def finish(self, main_window):
        self.__splash_screen.finish(main_window)