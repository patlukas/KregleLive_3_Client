#TODO Add comments
import json
import os


class CategoryTypesManagerError(Exception):
    """
        List code:
            16-000 - FileNotFoundError - if file does not exist
            16-001 - ValueError - if file format is not correct
            16-002 - KeyError - if file doesn't have required fields
            16-003 - TypeError - parameter has wrong type
            16-004 - KeyError - name of category type can't be empty string

    """
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__()

class CategoryType:
    def __init__(self, name: str, list_category: list[str], only_valid: bool, with_loaned: bool):
        self.name: str = name
        self.list_category: list[str] = list_category
        self.only_valid: bool = only_valid
        self.with_loaned: bool = with_loaned

class CategoryTypesManager:
    def __init__(self, path_to_category_type: str):
        self.__category_types: dict[str: CategoryType] = {}
        loaded_game_types: dict = self.__get_category_types(path_to_category_type)
        self.__check_correctness_data(loaded_game_types)
        for key, value in loaded_game_types.items():
            self.__category_types[key] = CategoryType(key, value["list_category"], value["only_valid"], value["with_loaned"])
        self.__selected_key: str = ""

    def get_list_category_type_name(self) -> list[str]:
        return [""] + list(self.__category_types.keys())

    def get_selected_category_type(self) -> CategoryType | None:
        if self.__selected_key in self.__category_types:
            return self.__category_types[self.__selected_key]
        return None

    def select_category_type(self, category_type_name: str) -> bool:
        if self.__selected_key == category_type_name:
            return False
        self.__selected_key = category_type_name
        return True

    @staticmethod
    def __get_category_types(path_to_category_type: str) -> dict:
        try:
            file = open(path_to_category_type, encoding='utf8')
        except FileNotFoundError:
            raise CategoryTypesManagerError("16-000", "Nie znaleziono pliku {}".format(os.path.abspath(path_to_category_type)))
        try:
            data = json.load(file)
        except ValueError:
            raise CategoryTypesManagerError("16-001", "Niewłaściwy format danych w pliku {}".format(os.path.abspath(path_to_category_type)))
        return data

    def __check_correctness_data(self, loaded_game_types: dict):
        for k, v in loaded_game_types.items():
            if k == "":
                raise CategoryTypesManagerError("16-004", f"Name of category type can't be empty")
            self.__check_value(k, v, "list_category", list, )
            self.__check_value(k, v, "only_valid", bool, )
            self.__check_value(k, v, "with_loaned", bool, )

    @staticmethod
    def __check_value(name: str, parameters: dict, parameter_name: str, parameter_type: type):
        if parameter_name not in parameters:
            raise CategoryTypesManagerError("16-002",f"In '{name}' there is no '{parameter_name}'")
        v = parameters[parameter_name]
        if not isinstance(parameters[parameter_name], parameter_type):
            raise CategoryTypesManagerError("16-003", f"In '{name}' the parameter '{parameter_name}' has the wrong type, it is '{type(v).__name__}' but should be '{parameter_type.__name__}'")
