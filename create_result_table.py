from methods_to_draw_on_image import MethodsToDrawOnImage
import copy

# TODO: Add comments

class CreateResultTable(MethodsToDrawOnImage):
    def __init__(self, table_settings: dict):
        super().__init__()
        self._table_settings: dict = table_settings
        self.__cells_metadata: {} = self.__get_cells_metadata()
        self._list_of_cell_names: list[str] = list(self.__cells_metadata.keys())
        self.__tables_clear: dict = self.__load_clear_images(table_settings["path_to_table"])

    def __load_clear_images(self, dict_wit_paths: dict) -> dict:
        return_dict = {}
        for key, path in dict_wit_paths.items():
            return_dict[key] = self.load_image(path)
        return return_dict

    def _make_table(self, now_results: dict, old_results: dict, old_img):
        i, clear_img = self.__get_clear_table(now_results["status"])
        if clear_img is None:
            return None
        if "status" not in old_results or int(i) & int(old_results["status"]) != int(old_results["status"]) or old_img is None:
            old_results = {}
            old_img = clear_img.copy()
        for name in self._list_of_cell_names:
            value_now = now_results.get(name, "")
            value_old = old_results.get(name, "")
            metadata = self.__cells_metadata[name]
            if not metadata["writeIfNoChange"] and value_now == value_old:
                continue

            if metadata["breakIfEmpty"] and value_now == "":
                continue

            cell = self.crop_img(clear_img, metadata["left"], metadata["top"], metadata["width"], metadata["height"])

            if metadata["background"] is not None:
                self.fill_cell_background(cell, metadata["background"])

            if value_now != "" and metadata["text"] is not None:
                value_now = metadata["text"]

            if value_now != "":
                cell = self.draw_text_in_cell(
                    cell, value_now, metadata["max_font_size"], metadata["font_path"],
                    metadata["font_color"], metadata["width"], metadata["height"], metadata["text_align"]
                )
            old_img = self.paste_img(old_img, cell, metadata["left"], metadata["top"])
        return old_img

    def __get_clear_table(self, status: str):
        status_int: int = int(status)
        for key, v in self.__tables_clear.items():
            if int(key) & status_int == status_int:
                return key, v
        return 0, None

    def __get_cells_metadata(self) -> list[str]:
        metadata = self._table_settings["cell_in_table"]["metadata_default"]
        cells = self._table_settings["cell_in_table"]["cells"]
        dict_metadata, _ = self.__x( metadata, cells, {}, {})
        return dict_metadata

    def __x(self, metadata: dict, cells: dict, dict_of_cells_metadata: dict, replace_key: dict):
        # TODO: Change func name
        for key, v in cells.items():
            if "for" in key:
                s = key.split("&")[0].split("|")
                for s_k, s_v in v["metadata"].items():
                    metadata[s_k] = s_v
                new_replace_key = copy.deepcopy(replace_key)
                for i in range(int(s[2]), int(s[3])+1):
                    new_replace_key[s[1]] = str(i)
                    dict_of_cells_metadata, metadata = self.__x(metadata, v["cells"], dict_of_cells_metadata, new_replace_key)
                    for s_k, s_v in v["metadata_step"].items():
                        metadata[s_k] += s_v
            else:
                for o, n in replace_key.items():
                    key = key.replace(o, n)
                for s_k, s_v in v.items():
                    metadata[s_k] = s_v
                dict_of_cells_metadata[key] = copy.deepcopy(metadata)
        return dict_of_cells_metadata, metadata

