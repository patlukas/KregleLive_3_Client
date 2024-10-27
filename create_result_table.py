from typing import Callable
from methods_to_draw_on_image import MethodsToDrawOnImage
from PIL import Image
import os

from results_manager import ResultsManager
from table_instruction import TableInstruction, TableInstructionError


# TODO: Add comments

class _CreateResultTable(MethodsToDrawOnImage):
    def __init__(self, table_type: str, font_path: str, template_dir: str, output_path: str, instructions_path: str,
                 number_tables: int, get_results: Callable[[list[str]], list[dict | None]],
                 on_add_log: Callable[[int, str, str, str], None]):
        """

        """
        super().__init__()
        self.__on_add_log: Callable[[int, str, str, str], None] = on_add_log
        self.__get_results: Callable[[list[str]], list[dict | None]] = get_results
        self.__number_images: int = number_tables
        self.__old_results: list[dict] = [{}] * number_tables
        self.__old_tables: list[Image.Image | None] = [None] * number_tables
        self.__font_dir: str = font_path
        self.__output_path: str = output_path
        self.__instructions: list[TableInstruction] = self.__load_instructions(table_type, instructions_path, template_dir)
        self.__instructions_index: int = 0

    def change_instruction(self, index: int) -> None:
        if self.__instructions_index == index:
            return
        if index < 0 or index >= len(self.__instructions):
            return
        self.__instructions_index = index
        for i in range(self.__number_images):
            self.__old_results[i] = {}
            self.__old_tables[i] = None

    def make_table(self):
        if self.__instructions_index >= len(self.__instructions):
            return None
        instruction = self.__instructions[self.__instructions_index]

        new_list_results: list[dict | None] | None = self.__get_results(instruction.list_of_cell_names)
        [width, height, background] = instruction.get_background_settings()
        final_img = self.create_img(width, height, background)
        if new_list_results is not None:
            for i, results in enumerate(new_list_results):
                if results is not None:
                    table = self.__make_single_table(instruction, results, i)
                    if table is None:
                        continue
                    [left, top] = instruction.list_table_cords[i]
                    final_img = self.paste_img(final_img, table, left, top)
        self.save_image(final_img, self.__output_path)

    def __load_instructions(self, table_type: str, dir_instruction: str, dir_template: str) -> list[TableInstruction]:
        instruction_files: list[str] = [file for file in os.listdir(dir_instruction) if file.endswith('.json')]
        return_list = []
        for file_path in instruction_files:
            try:
                instruction = TableInstruction(table_type,dir_instruction + file_path, dir_template, self.load_image)
                return_list.append(instruction)
            except TableInstructionError as e:
                self.__on_add_log(10, "CRT_LOAD_ERROR", e.code, e.message)
        return return_list

    def __make_single_table(self, instruction: TableInstruction, now_results: dict, table_index: int):
        if instruction is None:
            return None
        old_results, old_table = self.__old_results[table_index], self.__old_tables[table_index]
        img_key, clear_img = instruction.get_img_template(now_results["status"])
        if clear_img is None:
            return None
        if "status" not in old_results or int(img_key) & int(old_results["status"]) != int(old_results["status"]) or old_table is None:
            old_results = {}
            old_table = clear_img.copy()
        for name in instruction.list_of_cell_names:
            value_now, value_old = now_results.get(name, ""), old_results.get(name, "")
            metadata = instruction.cells_metadata[name]
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
                    cell, value_now, metadata["max_font_size"], self.__font_dir + metadata["font_path"],
                    metadata["font_color"], metadata["width"], metadata["height"], metadata["text_align"]
                )
            old_table = self.paste_img(old_table, cell, metadata["left"], metadata["top"])
        self.__old_tables[table_index] = old_table
        self.__old_results[table_index] = now_results
        return old_table

class CreateTableMain(_CreateResultTable):
    def __init__(self, results_manager: ResultsManager | None, fonts_dir: str, template_dir: str, output_path: str,
                 instruction_dir: str, on_add_log: Callable[[int, str, str, str], None]):
        super().__init__("main", fonts_dir, template_dir, output_path, instruction_dir, 1,
                         results_manager.get_scores, on_add_log)


class CreateTableLane(_CreateResultTable):
    def __init__(self, results_manager: ResultsManager | None, fonts_dir: str, template_dir: str, output_path: str,
                 instruction_dir: str, number_of_lanes: int, on_add_log: Callable[[int, str, str, str], None]):
        super().__init__("lane", fonts_dir, template_dir, output_path, instruction_dir, number_of_lanes,
                         results_manager.get_scores_of_players_now_playing, on_add_log)
