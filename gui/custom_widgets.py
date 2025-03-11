from PyQt6.QtWidgets import QComboBox, QLineEdit, QGroupBox


class QComboBoxWithHistory(QComboBox):
    def __init__(self, event_after_change, items = ()):
        super().__init__()
        self.addItems(items)
        self.__saved = "" if len(items) == 0 else items[0]
        self.currentTextChanged.connect(event_after_change)

    def is_new_value(self):
        return self.currentText() != self.__saved

    def save_value(self):
        self.__saved = self.currentText()

    def rollback_value(self):
        self.setCurrentText(self.__saved)


class QLineEditWithHistory(QLineEdit):
    def __init__(self, event_after_change):
        super().__init__()
        self.__saved = ""
        self.textChanged.connect(event_after_change)

    def is_new_value(self):
        return self.text() != self.__saved

    def save_value(self):
        self.__saved = self.text()

    def rollback_value(self):
        self.setText(self.__saved)


class QCheckableGroupBoxWithHistory(QGroupBox):
    def __init__(self, title, event_after_change, default_value):
        super().__init__(title)
        self.__saved = default_value
        self.setCheckable(True)
        self.setChecked(default_value)
        self.toggled.connect(event_after_change)

    def is_new_value(self):
        return self.isChecked() != self.__saved

    def save_value(self):
        self.__saved = self.isChecked()

    def rollback_value(self):
        self.setChecked(self.__saved)