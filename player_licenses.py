import json
import os
import pandas as pd

from category_type_manager import CategoryType


# TODO: Add comments
class PlayerLicensesError(Exception):
    """
        List code:
            15-000 - FileNotFoundError - if config.json does not exist
            15-001 - ValueError - if config.json format is not correct
            15-002 - KeyError - if config doesn't have required fields
            15-003 - FileNotFoundError - if the path to the com0com directory is incorrect
    """
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__()

class _Player:
    def __init__(self, license_number: str, team: str, name: str, category: str, valid: bool):
        self.license_number: str = license_number
        self.team: str = team
        self.name: str = name
        self.category: str = category
        self.valid: bool = valid

class PlayerLicenses:
    def __init__(self, path_to_config: str):
        self.__players_not_loaned: list[_Player] = []
        self.__players_loaned_lending: list[_Player] = []
        self.__players_loaned_loaning: list[_Player] = []
        self.__settings: dict = self.__load_settings(path_to_config)
        self.load_licenses()
        self.__category_type: None | CategoryType = None

    def get_players(self, team: str | None) -> list[_Player]:
        with_loaned, list_category, only_valid = False, None, False
        if self.__category_type is not None:
            with_loaned, list_category, only_valid = self.__category_type.with_loaned, self.__category_type.list_category, self.__category_type.only_valid
        return_list: list[_Player] = []
        for player in self.__players_not_loaned + (self.__players_loaned_lending if with_loaned else self.__players_loaned_loaning):
            if team is not None and player.team != team:
                continue
            if list_category is not None and player.category not in list_category:
                continue
            if only_valid and not player.valid:
                continue
            return_list.append(player)
        return_list.sort(key=lambda e: e.name)
        return return_list

    def get_teams(self) -> list[str]:
        list_players = self.get_players(None)
        list_teams: list[str] = []
        for player in list_players:
            if player.team not in list_teams:
                list_teams.append(player.team)
        return list_teams

    @staticmethod
    def __load_settings(path_to_config: str) -> dict:
        try:
            file = open(path_to_config)
        except FileNotFoundError:
            raise PlayerLicensesError("15-000", "Nie znaleziono pliku {}".format(os.path.abspath(path_to_config)))
        try:
            data = json.load(file)
        except ValueError:
            raise PlayerLicensesError("15-001", "Niewłaściwy format danych w pliku {}".format(os.path.abspath(path_to_config)))
        keys = [
            "path", "team_column", "name_column","category_column", "valid_license_column", "where_loaned_column",
            "license_is_valid_when_there_is_text", "license_column"
        ]
        for key in keys:
            if key not in data:
                raise PlayerLicensesError("15-002", "KeyError - W pliku licenses.json nie ma: " + key)
        return data

    def load_licenses(self):
        self.__players_not_loaned = []
        self.__players_loaned_loaning = []
        self.__players_loaned_lending = []
        data = pd.read_csv(self.__settings["path"])
        for index, row in data.iterrows():
            lic = row.iloc[self.__settings["license_column"]]
            t = row.iloc[self.__settings["team_column"]]
            n = row.iloc[self.__settings["name_column"]]
            c = row.iloc[self.__settings["category_column"]]
            v = row.iloc[self.__settings["valid_license_column"]] in self.__settings["license_is_valid_when_there_is_text"]
            l = row.iloc[self.__settings["where_loaned_column"]]
            if pd.isna(l):
                self.__players_not_loaned.append(_Player(lic, t, n, c, v))
            else:
                self.__players_loaned_loaning.append(_Player(lic, t, n, c, v))
                self.__players_loaned_lending.append(_Player(lic, l, n, c, v))

    def set_category_type(self, category_type: CategoryType | None):
        self.__category_type = category_type
