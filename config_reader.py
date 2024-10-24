"""This module read configuration from config.json"""
import json
import os

# TODO: Dodaj do config informacje o innych plikach i katalogach
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
    def get_configuration(self) -> dict:
        """
        This method get configuration from config.json

        :return: dict with config
        :raises:
            ConfigReaderError
                12-000 - FileNotFoundError - if config.json does not exist
                12-001 - ValueError - if config.json format is not correct
                12-002 - KeyError - if config doesn't have required fields
        """
        try:
            file = open("settings/config.json")
        except FileNotFoundError:
            raise ConfigReaderError("12-000", "Nie znaleziono pliku {}".format(os.path.abspath("settings/config.json")))
        try:
            data = json.load(file)
        except ValueError:
            raise ConfigReaderError("12-001", "Niewłaściwy format danych w pliku {}".format(os.path.abspath(
                "settings/config.json")))
        for key in self.__get_required_config_settings():
            if key not in data:
                raise ConfigReaderError("12-002", "KeyError - W pliku config.json nie ma: " + key)
        return data

    @staticmethod
    def __get_required_config_settings() -> list:
        """
        This method return list of required keys

        :return: list of required key names that must be in config.json
        """
        list_settings = [
            "minimum_number_of_lines_to_write_in_log_file",
            "socket_timeout",
            "dir_fonts",
            "dir_template_lane",
            "dir_template_main",
            "file_output_lane",
            "file_output_main",
            "dir_instructions_lane",
            "dir_instructions_main"
        ]
        return list_settings