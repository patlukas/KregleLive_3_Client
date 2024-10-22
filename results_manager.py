import copy
from typing import Callable

from game_type_manager import GameType, Transition
from results_container import ResultsContainer
# TODO add comments

class ResultsManager:
    def __init__(self, results_container: ResultsContainer, game_type: GameType, on_add_log: Callable[[int, str, str, str], None]):
        """
        Jeżeli self.__period == self.__number_of_periods to znaczy że jest koniec
        :param game_type:
        :param on_add_log:

        Jeżeli nie ma graczy to odrzucane są przychodzące wyniki
        """
        self.__results_container: ResultsContainer = results_container
        self.__on_add_log: Callable[[int, str, str, str], None] = on_add_log
        self.__game_type: GameType = game_type
        self.__list_of_blocks: list[Transition] = []
        self.__block_number: int = -1
        self.__max_block_number: int = -1
        self.__block_is_running: bool = False
        self.__round: int = -1
        self.__number_of_periods: int = game_type.number_periods
        self.__status_on_lanes = [([] if l == 1 else None) for l in game_type.lanes]
        self.__results_container.init_struct(self.__game_type.number_team, self.__game_type.number_player_in_team)
        if self.__game_type.type == "league":
            for _ in range(self.__game_type.number_periods):
                self.add_block("")

    def add_block(self, transitions_name: str):
        if transitions_name not in self.__game_type.transitions:
            return
        transition: Transition = self.__game_type.transitions[transitions_name]
        self.__list_of_blocks.append(transition)
        self.__results_container.init_block(transition.number_lane)

    def change_lane_status(self, lane: int, status_new: int):
        if self.__block_number == self.__game_type.number_periods - 1and not self.__block_is_running:
            return
        if self.__status_on_lanes is None:
            return
        if self.__status_on_lanes[lane] is None:
            return

        if len(self.__status_on_lanes[lane]) == 0:
            self.__change_lane_status__add_new_round(lane, status_new)
        else:
            status_old = self.__status_on_lanes[lane][-1]
            if status_old + 1 == status_new:
                self.__on_add_log(3, "RST_STATUS_OK", f"{lane + 1}", f"Poprawna zmiana statusu rundy na torze {lane + 1}: poprzedni status {status_old}, nowy {status_new}")
                self.__status_on_lanes[lane][-1] = status_new
            elif status_old == status_new:
                if status_old != 3: #Because status 3 is set when is recv message with name player and setup lane
                    self.__on_add_log(9, "RST_STATUS_EQ", f"{lane + 1}", f"Status rundy na torze {lane + 1} nie zmienił się: poprzedni status {status_old}, nowy {status_new}")
            elif status_old + 1 < status_new or (status_new < 2 and status_old <= 2):
                self.__on_add_log(9, "RST_STATUS_JMP", f"{lane + 1}", f"Zmiana statusu rundy na torze {lane + 1}: poprzedni status {status_old}, nowy {status_new}")
                self.__status_on_lanes[lane][-1] = status_new
            else:
                self.__change_lane_status__add_new_round(lane, status_new)
        if status_new == 5:
            self.__check_end_block()

    def __change_lane_status__add_new_round(self, lane: int, status_new: int):
        if status_new == 0 or status_new == 3:
            self.__on_add_log(3, "RST_STATUS_OK", f"{lane + 1}", f"Nowa runda na torze {lane + 1}. Status: {status_new}")
        else:
            self.__on_add_log(9, "RST_STATUS_JMP", f"{lane + 1}", f"Nowa runda na torze {lane + 1}. Status: {status_new}, powinien być 0 lub 3")
        self.__status_on_lanes[lane].append(status_new)

        new_round = len(self.__status_on_lanes[lane]) - 1
        for list_status_lane in self.__status_on_lanes:
            if list_status_lane is None:
                continue
            new_round = min(new_round, len(list_status_lane) - 1)

        if len(self.__status_on_lanes[lane]) - 1 >= sum([block.number_lane for block in self.__list_of_blocks[:self.__max_block_number+1]]):
            self.__max_block_number += 1
            if self.__max_block_number == len(self.__list_of_blocks):
                self.add_block(self.__game_type.default_transitions)

        if new_round != self.__round:
            self.__on_add_log(3, "RST_ROUND_CHANGE", f"", f"Zmiana rundy. Stara: {self.__round}, nowa: {new_round}")
            self.__round = new_round
            if self.__round == sum([block.number_lane for block in self.__list_of_blocks[:self.__block_number+1]]):
                self.__block_number += 1
                self.__block_is_running = True

    def __check_end_block(self):
        if len(self.__list_of_blocks) <= self.__block_number or self.__block_number == -1:
            return
        round_to_end_block = sum([block.number_lane for block in self.__list_of_blocks[:self.__block_number + 1]])
        for list_status_lane in self.__status_on_lanes:
            if list_status_lane is not None:
                if list_status_lane[-1] != 5 or len(list_status_lane) < round_to_end_block:
                    return False
        self.__block_is_running = False
        self.__on_add_log(6, "RST_PERIOD_END", f"", f"Zakończono okres: {self.__block_number}")
        return True

    def change_time_on_lane(self, lane: int, time: float):
        who = self.__get_player_on_lane_for_results_or_time(lane)
        if not who:
            return
        self.__results_container.update_time(who, time)

    def add_result_to_lane(self, lane, type_update: bytes, throw: int, throw_result: int, lane_sum: int, total_sum: int,
                      next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int):
        who = self.__get_player_on_lane_for_results_or_time(lane)
        if not who:
            return
        self.__results_container.update_result(who, type_update, throw, throw_result, lane_sum, total_sum,
                      next_arrangements, all_x, time, beaten_arrangements, card)

    def trial_setup_on_lane(self, lane: int, max_throw: int, time: float):
        result = self.__get_player_on_lane(lane)
        if not result or result[0] != 0:
            return
        self.__results_container.init_setup_trial(result[1], max_throw, time)

    def game_setup_on_lane(self, lane: int, number_p: int, number_z: int, time: float, total_sum: int, all_x: int, card: int):
        result = self.__get_player_on_lane(lane)
        if not result or result[0] != 3:
            return
        self.__results_container.init_setup_game(result[1], number_p, number_z, time, total_sum, all_x, card)

    def set_player_name_if_not_set(self, lane: int, name: str):
        result = self.__get_player_on_lane(lane)
        if not result:
            return
        self.__results_container.set_player_name_if_not_set(result[1], name)

    def set_player_name(self, team: int, player: int, name: str):
        self.__results_container.set_player_name((team, player), name)

    def set_team_name(self, team: int, name: str):
        self.__results_container.set_team_name(team, name)

    def __get_player_on_lane(self, lane: int) -> tuple[int, tuple[int, int, int]] | bool:
        if self.__block_number == self.__game_type.number_periods - 1 and not self.__block_is_running:
            return False
        status_on_lane = self.__status_on_lanes[lane]
        if status_on_lane is None or len(status_on_lane) == 0:
            return False

        status: int = status_on_lane[-1]
        block, round_on_block = self.__get_block_and_round(len(status_on_lane) - 1)

        player = copy.deepcopy(self.__list_of_blocks[block].schema[round_on_block][lane])
        if player == -1 or isinstance(player, int):
            return False
        if status < 3:
            player[2] = -1
        player[1] += block * self.__game_type.number_player_in_team
        return status, tuple(player)

    def __get_player_on_lane_for_results_or_time(self, lane: int) -> tuple[int, int, int] | bool:
        result = self.__get_player_on_lane(lane)
        if not result or result[0] in [0, 2, 3, 5]:
            return False
        return result[1]

    def __get_currently_playing_players(self) -> list[tuple[int, tuple[int, int, int]] | None] | None:
        if self.__status_on_lanes is None or self.__round == -1 or len(self.__list_of_blocks) <= self.__block_number or self.__block_number == -1:
            return None
        list_playing_players = []
        for i, list_status_on_lane in enumerate(self.__status_on_lanes):
            if list_status_on_lane is None or len(list_status_on_lane) == 0:
                list_playing_players.append(None)
                continue
            block, lane_in_block = self.__get_block_and_round(self.__round)
            if len(self.__list_of_blocks) <= block:
                return None
            player = copy.deepcopy(self.__list_of_blocks[block].schema[lane_in_block][i])
            player[1] += self.__block_number * self.__game_type.number_player_in_team
            status = list_status_on_lane[self.__round]
            list_playing_players.append((status, player))
        return list_playing_players

    def __get_block_and_round(self, round_number: int) -> tuple[int, int]:
        block_number = 0
        for block in self.__list_of_blocks:
            if round_number >= block.number_lane:
                round_number -= block.number_lane
                block_number += 1
        return block_number, round_number

    def get_scores_of_players_now_playing(self, list_of_result_names: list[str]) -> list[dict | None] | None:
        currently_playing_players: list[tuple[int, tuple[int, int, int]] | None] | None = self.__get_currently_playing_players()
        if currently_playing_players is None:
            return None
        return_list = []
        for lane, playing_players in enumerate(currently_playing_players):
            if playing_players is None:
                return_list.append(None)
            else:
                status, who = playing_players
                return_list.append(self.__results_container.get_dict_with_results(list_of_result_names, who, status))
        return return_list

    def get_scores(self, list_of_result_names: list[str]) -> dict | None:
        return self.__results_container.get_dict_with_results(list_of_result_names, (0, 0, 0), 0)
