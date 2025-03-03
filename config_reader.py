"""This module read configuration from config.json"""
import json
import os
from typing import Callable

class ConfigReaderError(Exception):
    """
        List code:
            12-000 - FileNotFoundError - if config.json does not exist
            12-001 - ValueError - if config.json format is not correct
            12-002 - KeyError - if config doesn't have required fields
            12-003 - FileNotFoundError - if the path to the com0com directory is incorrect
    """
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__()


class ConfigReader:
    def __init__(self, on_add_log: Callable[[int, str, str, str, bool], None]):
        """

        :param on_add_log:
        """
        self.__on_add_log: Callable[[int, str, str, str, bool], None] = on_add_log

    def get_configuration(self) -> dict:
        """
        This method get configuration from config.json

        :return: dict with config
        :logs:  CNF_PATH_NOTEXISTED (7), CNF_READ (2), CNF_PATH_OK (1)
        :raises:
            ConfigReaderError
                12-000 - FileNotFoundError - if config.json does not exist
                12-001 - ValueError - if config.json format is not correct
                12-002 - KeyError - if config doesn't have required fields
        """
        try:
            file = open("settings/config.json", encoding='utf8')
        except FileNotFoundError:
            raise ConfigReaderError("12-000", "Nie znaleziono pliku {}".format(os.path.abspath("settings/config.json")))
        try:
            data = json.load(file)
        except ValueError:
            raise ConfigReaderError("12-001", "Niewłaściwy format danych w pliku {}".format(os.path.abspath(
                "settings/config.json")))
        for key, val_type in self.__get_required_config_settings():
            if key not in data:
                raise ConfigReaderError("12-002", "KeyError - W pliku config.json nie ma: " + key)
            if val_type == "path_dir" or val_type == "path_file":
                is_file = (val_type == "path_file")
                data[key] = os.path.expandvars(data[key])
                self.__check_path(data[key], is_file)
        self.__on_add_log(2, "CNF_READ", "", "Pobrano konfigurację", False)
        return data

    @staticmethod
    def __get_required_config_settings() -> list:
        """
        This method return list of required keys

        :return: list of required key names that must be in config.json
        """
        list_settings = [
            ["minimum_number_of_lines_to_write_in_log_file", "int"],
            ["socket_timeout", "float"],
            ["number_of_lanes", "int"],
            ["dir_fonts", "path_dir"],
            ["dir_template_lane", "path_dir"],
            ["dir_template_main", "path_dir"],
            ["file_output_lane", "path_file"],
            ["file_output_main", "path_file"],
            ["dir_instructions_lane", "path_dir"],
            ["dir_instructions_main", "path_dir"],
            ["file_with_licenses_config", "path_file"],
            ["file_with_category_types", "path_file"],
            ["file_with_game_types", "path_file"],
            ["loop_interval_ms", "int"],
            ["server_ip", "str"],
            ["server_port", "str"]
            ["server_port", "str"],
        ]
        return list_settings

    def __check_path(self, path: str, is_file: bool) -> None:
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if is_file:
                with open(path, "w") as f:
                    pass
            self.__on_add_log(7, "CNF_PATH_NOTEXISTED", "", f"Nie istniałą ścieżka: {path}", True)
        else:
            self.__on_add_log(1, "CNF_PATH_OK", "", f"Ścieżka poprawna: {path}", True)
