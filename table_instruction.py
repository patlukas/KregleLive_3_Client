import copy
import json
import os
from types import NoneType
from typing import Callable
from PIL import Image

class TableInstructionError(Exception):
    """
        List code:
            14-000 - FileNotFoundError - if table instruction not found
            14-001 - ValueError - if table instruction format is not correct
            14-002 - KeyError - if table instruction doesn't have required fields
    """
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__()


class TableInstruction:
    def __init__(self, table_type: str, path: str, dir_img_template: str, on_load_img: Callable[[str], Image.Image]):
        self.__dir_img_template: str = dir_img_template
        self.__dict_img_template: dict = {}
        self.__instruction = self.__load_instruction(table_type, path)
        self.__on_load_img: Callable[[str], Image.Image] = on_load_img

        self.cells_metadata: dict = self.__get_cells_metadata()
        self.list_of_cell_names: list[str] = list(self.cells_metadata.keys())
        self.list_table_cords: list[tuple[int, int]] = self.__get_list_table_cords()

    def get_img_template(self, status: str):
        status_int: int = int(status)
        for key, [img_path, img] in self.__dict_img_template.items():
            if int(key) & status_int == status_int:
                if img is None:
                    img = self.__on_load_img(self.__dir_img_template + img_path)
                    self.__dict_img_template[key] = [img_path, img]
                return key, img
        return 0, None

    def get_background_settings(self) -> tuple[int, int, tuple[int, int, int]]:
        w, h, b = self.__instruction["width"], self.__instruction["height"], self.__instruction["background_color"]
        return w, h, b

    def __load_instruction(self, table_type: str, path: str) -> dict:
        try:
            file = open(path, encoding='utf8')
        except FileNotFoundError:
            raise TableInstructionError("14-000", "Nie znaleziono instrukcji tabeli pod ścieżką: {}".format(os.path.abspath(path)))
        try:
            table_instruction = json.load(file)
        except ValueError:
            raise TableInstructionError("14-001", "Niewłaściwy format danych w instrukcji tabeli: {}".format(os.path.abspath(path)))
        check_result, check_comment = self.__check_file_structure(table_type, table_instruction)
        if not check_result:
            raise TableInstructionError("14-002", "Niepoprawne pola w {}: {}".format(os.path.abspath(path), check_comment))
        for status, path_img_template in table_instruction["path_to_table"].items():
            self.__dict_img_template[status] = [path_img_template, None]
        return table_instruction
    def __check_file_structure(self, table_type: str, table_instruction: dict) -> (bool, str):
        dict_key_type = {
            "": [
                ["type", str],
                ["name", str],
                ["path_to_table", dict],
                ["background_color", list],
                ["width", int],
                ["height", int],
                ["table_cords", list],
                ["cell_in_table", dict]
            ],
            "cell_in_table": [
                ["metadata_default", dict],
                ["cells", dict]
            ],
            "cell_in_table|metadata_default": [
                ["font_path", str],
                ["font_color", list],
                ["max_font_size", int],
                ["left", int],
                ["top", int],
                ["width", int],
                ["height", int],
                ["text_align", str],
                ["writeIfNoChange", bool],
                ["breakIfEmpty", bool],
                ["text", [str, NoneType]],
                ["background", [list, NoneType]]
            ]
        }
        for key, value in dict_key_type.items():
            obj = table_instruction
            if key != "":
                keys = key.split("|")
                for k in keys:
                    obj = obj[k]
            for field_key, field_type in value:
                if not self.__check_field(obj, field_key, field_type):
                    return False, f"Nie istnieje lub błędny typ pola: {key}.{field_key}, powinien być typ {field_type}"

        for i, table_coord in enumerate(table_instruction["table_cords"]):
            for field_key, field_type in [["top", int], ["left", int]]:
                if not self.__check_field(table_coord, field_key, field_type):
                    return False, f"Nie istnieje lub błędny typ pola: table_cords[{i}].{field_key}, powinien być typ {field_type}"

        if table_instruction["type"] != table_type:
            return False, f"Błędny typ, powinien być {table_type} a jest {table_instruction["type"]}"
        return True, ""

    @staticmethod
    def __check_field(table_instruction: dict, key: str, filed_type: type | list[type]) -> bool:
        if key not in table_instruction:
            return False
        if isinstance(filed_type, type):
            filed_type = [filed_type]
        for t in filed_type:
            if isinstance(table_instruction[key], t):
                return True
        return False

    def __get_list_table_cords(self) -> list[tuple[int, int]]:
        return_list = []
        for table_cord in self.__instruction["table_cords"]:
            return_list.append((table_cord["left"], table_cord["top"]))
        return return_list

    def __get_cells_metadata(self) -> dict[str]:
        metadata = self.__instruction["cell_in_table"]["metadata_default"]
        cells = self.__instruction["cell_in_table"]["cells"]
        dict_metadata, _ = self.__get_cells_metadata__recursive(metadata, cells, {}, {})
        return dict_metadata

    def __get_cells_metadata__recursive(self, metadata: dict, cells: dict, dict_of_cells_metadata: dict,
                                        replace_key: dict):
        for key, v in cells.items():
            if "for" in key:
                s = key.split("&")[0].split("|")
                for s_k, s_v in v["metadata"].items():
                    metadata[s_k] = s_v
                new_replace_key = copy.deepcopy(replace_key)
                for i in range(int(s[2]), int(s[3]) + 1):
                    new_replace_key[s[1]] = str(i)
                    dict_of_cells_metadata, metadata = self.__get_cells_metadata__recursive(metadata, v["cells"], dict_of_cells_metadata, new_replace_key)
                    for s_k, s_v in v["metadata_step"].items():
                        metadata[s_k] += s_v
            else:
                for o, n in replace_key.items():
                    key = key.replace(o, n)
                for s_k, s_v in v.items():
                    metadata[s_k] = s_v
                dict_of_cells_metadata[key] = copy.deepcopy(metadata)
        return dict_of_cells_metadata, metadata
