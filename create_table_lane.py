from time import sleep

from create_result_table import CreateResultTable
from create_table_main import CreateTableMain
from results_container import ResultsContainer, ResultsContainerLeague
from results_manager import ResultsManager
import json

# TODO: MAny lines to del

class CreateTableLane(CreateResultTable):
    def __init__(self, results_manager: ResultsManager | None, fonts_dir: str, template_dir: str, output_path: str,
                     instruction_dir: str, table_settings: dict):
        super().__init__(table_settings, fonts_dir, template_dir, output_path, instruction_dir)
        self.__number_of_lane: int = len(table_settings["table_cords"])
        self.__results_manager: ResultsManager | None = results_manager
        self.__list_results: list[dict] = [{}] * self.__number_of_lane
        self.__list_of_now_showing_tables: list = [None] * self.__number_of_lane

    def make_table(self):
        new_list_results: list[dict | None] | None = self.__results_manager.get_scores_of_players_now_playing(self._list_of_cell_names)
        final_img = self.create_img(self._table_settings["width"], self._table_settings["height"], self._table_settings["background_color"])
        if new_list_results is not None:
            table_cords = self._table_settings["table_cords"]
            for i, results in enumerate(new_list_results):
                if i >= len(table_cords):
                    # TODO: ERROR Więcej graczy niż torów w json
                    continue
                if results is not None:
                    old_results = self.__list_results[i]
                    old_table_img = self.__list_of_now_showing_tables[i]
                    table = self._make_table(results, old_results, old_table_img)
                    self.__list_results[i] = results
                    self.__list_of_now_showing_tables[i] = table
                    if table is None:
                        continue
                    final_img = self.paste_img(final_img, table, table_cords[i]["left"], table_cords[i]["top"])
        self.save_image(final_img, self._output_path)


# log = lambda a, b, c, d: print(a, b, c, d)
# results_container = ResultsContainerLeague(log)
# results_container.init_struct(2, 3, 2, 4)
#
# file_gametype = open("game_types.json", encoding='utf8')
# json_gametype = json.load(file_gametype)
# gametype = json_gametype["Liga 6-osobowa"]
# results_manager = ResultsManager(results_container, gametype["transitions"], gametype["lanes"], gametype["number_periods"], log)
#
# # results_manager.change_lane_status(0, 3)
# # results_manager.game_setup_on_lane(0, 15, 15, 12.0, 100, 10, 0)
# # results_manager.change_lane_status(0, 4)
# # results_manager.change_lane_status(1, 3)
# # results_manager.game_setup_on_lane(1, 15, 15, 12.0, 100, 10, 0)
# # results_manager.change_lane_status(1, 4)
# # results_manager.add_result_to_lane(0, b"w", 1, 3, 3, 3, 0, 0, 11.5, 222, 0)
# # results_manager.add_result_to_lane(0, b"w", 1, 3, 3, 3, 0, 0, 11.5, 222, 0)
#
# file = open("table_for_results/lane_league_light.json", encoding='utf8')
# b = json.load(file)
# print(b)
#
# a = CreateTableLane(results_manager, b)
#
# file2 = open("table_for_results/main_league_6_light.json", encoding='utf8')
# b2 = json.load(file2)
# print(b2)
# aa = CreateTableMain(results_manager, b2)
# # a.make_table()
#
# # sleep(1)
# # results_manager.add_result_to_lane(0, b"w", 2, 9, 12, 3, 0, 0, 11.5, 222, 0)
# # a.make_table()
# #
# # sleep(1)
# # results_manager.add_result_to_lane(1, b"w", 1, 7, 7, 8, 0, 0, 11.5, 222, 0)
# # a.make_table()
# #
# # sleep(1)
# # results_manager.add_result_to_lane(0, b"w", 3, 8, 20, 8, 0, 0, 11.5, 222, 0)
# # a.make_table()
# # a.make_table()
# # sleep(5)
# s = [0] * 6
# for j in range(2):
#     results_manager.set_team_name(j, f"Team {j}")
#     for i in range(6):
#         results_manager.set_player_name(j, i, f"{j} -  {i}")
#
# for k in range(8):
#     for i in range(-1, 31):
#         for j in range(6):
#             if i == -1 and k % 4 == 0:
#                 results_manager.change_lane_status(j, 0)
#                 results_manager.trial_setup_on_lane(j, 20, 5.0)
#                 results_manager.change_lane_status(j, 1)
#             elif i == 0:
#                 results_manager.change_lane_status(j, 2)
#                 results_manager.change_lane_status(j, 3)
#                 results_manager.game_setup_on_lane(j, 15, 15, 12.0, 100, 10, 0)
#                 results_manager.change_lane_status(j, 4)
#             else:
#                 x = j
#                 s[j] += x
#                 results_manager.add_result_to_lane(j, b"w", i, x, s[j], 8, 0, 0, 11.5, 222, 0)
#                 if i == 30:
#                     results_manager.change_lane_status(j, 5)
#             if (i % 15 == 0 or (i == -1 and k % 4 == 0)) and j == 5:
#                 a.make_table()
#                 aa.make_table()
#                 sleep(1)
#             # sleep(0.1)
# # aa.make_table()
# sleep(5)
#
#
#




