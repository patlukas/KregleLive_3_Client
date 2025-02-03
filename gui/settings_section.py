from collections.abc import Callable
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLabel, QStackedLayout, QComboBox, QPushButton

from category_type_manager import CategoryTypesManager
from create_result_table import CreateTableLane, CreateTableMain


class SettingsSection(QGroupBox):
    """
        TODO: Add comment
    """
    def __init__(self, category_type_manager: CategoryTypesManager, on_change_category_type: Callable[[], None],
                 create_table_lane: CreateTableLane, on_change_table_lane: Callable[[], None],
                 create_table_main: CreateTableMain, on_change_table_main: Callable[[], None]):
        super().__init__("Ustawienia")
        self.__category_type_manager: CategoryTypesManager = category_type_manager
        self.__create_table_lane: CreateTableLane = create_table_lane
        self.__create_table_main: CreateTableMain = create_table_main
        self.__on_after_change_category_type: Callable[[], None] = on_change_category_type
        self.__on_after_change_table_lane: Callable[[], None] = on_change_table_lane
        self.__on_after_change_table_main: Callable[[], None] = on_change_table_main

        self.__stacked_layout: QStackedLayout = QStackedLayout()

        self.__layout = QGridLayout()
        self.__label_category: QLabel = QLabel("Filtr zawodników:")
        self.__combo_category: QComboBox = QComboBox()
        self.__button_category: QPushButton = QPushButton("Wybierz")

        self.__label_lane: QLabel = QLabel("Tabelki z wynikami na torach:")
        self.__combo_lane: QComboBox = QComboBox()

        self.__label_main: QLabel = QLabel("Główna tabela z wynikami:")
        self.__combo_main: QComboBox = QComboBox()

        self.__set_layout()

    def __set_layout(self):
        """."""
        self.__layout.addWidget(self.__label_category, 0, 0)
        self.__layout.addWidget(self.__combo_category, 0, 1, 1, 2)
        self.__layout.addWidget(self.__button_category, 0, 3)
        self.__layout.addWidget(self.__label_lane, 1, 0, 1, 2)
        self.__layout.addWidget(self.__combo_lane, 1, 2, 1, 2)
        self.__layout.addWidget(self.__label_main, 2, 0, 1, 2)
        self.__layout.addWidget(self.__combo_main, 2, 2, 1, 2)

        self.__combo_category.addItems(self.__category_type_manager.get_list_category_type_name())
        self.__combo_category.currentIndexChanged.connect(self.__check_is_new_category)
        self.__button_category.clicked.connect(self.__on_change_category)
        self.__button_category.setEnabled(False)

        self.__combo_lane.addItems(self.__create_table_lane.get_list_instructions_name())
        self.__combo_lane.currentTextChanged.connect(self.__on_change_lane)

        self.__combo_main.addItems(self.__create_table_main.get_list_instructions_name())
        self.__combo_main.currentTextChanged.connect(self.__on_change_main)

        self.setLayout(self.__layout)

    def __check_is_new_category(self):
        selected_key = self.__combo_category.currentText()
        if self.__category_type_manager.get_selected_key() == selected_key:
            self.__button_category.setEnabled(False)
        else:
            self.__button_category.setEnabled(True)

    def __on_change_category(self):
        selected_option = self.__combo_category.currentText()
        if self.__category_type_manager.select_category_type(selected_option):
            self.__on_after_change_category_type()
        self.__button_category.setEnabled(False)

    def __on_change_lane(self):
        index_selected_option = self.__combo_lane.currentIndex()
        if self.__create_table_lane.change_instruction(index_selected_option):
            self.__on_after_change_table_lane()

    def __on_change_main(self):
        index_selected_option = self.__combo_main.currentIndex()
        if self.__create_table_main.change_instruction(index_selected_option):
            self.__on_after_change_table_main()
