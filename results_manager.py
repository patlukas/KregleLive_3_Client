import copy
from typing import Callable

from results_container import ResultsContainer


class ResultsManager:
    def __init__(self, results_container: ResultsContainer, transitions: list[list[(int, int, int)]], lanes: list[int], number_of_periods: int, on_add_log: Callable[[int, str, str, str], None]):
        """
        Jeżeli self.__period == self.__number_of_periods to znaczy że jest koniec
        :param transitions:
        :param lanes:
        :param number_of_periods:
        :param on_add_log:
        """
        self.__results_container: ResultsContainer = results_container
        self.__on_add_log: Callable[[int, str, str, str], None] = on_add_log
        self.__transitions: list[list[(int, int, int)] | int] = transitions
        self.__period: int = 0
        self.__period_is_running: bool = False
        self.__round: int = -1
        self.__number_of_periods: int = number_of_periods
        self.__number_of_team: int = 0
        self.__number_of_player_in_team_in_period: int = 0
        self.__status_on_lanes: list[list[int] | None] | None = None
        self.__init_variable(transitions, lanes)

    def __init_variable(self, transitions: list[list[(int, int, int)]], lanes: list[int]) -> bool:
        data = {}
        number_lane = 0
        for round_transition in transitions:
            for lane, lane_transition in enumerate(round_transition):
                if (lane_transition == -1 and lanes[lane] == 1) or (lane_transition != -1 and lanes[lane] == 0):
                    self.__on_add_log(10, "RST_TRAN_ERROR_LANE", "", f"Lista przejść nie pokrywa się z aktywnymi torami")
                if lane_transition == -1:
                    continue
                if len(lane_transition) != 3:
                    self.__on_add_log(10, "RST_TRAN_ERROR_LEN", "", f"Lista przejść ma element, który nie zawiera 3 pól: {lane_transition}")
                    return False
                if type(lane_transition[0]) != int or type(lane_transition[1]) != int or type(lane_transition[2]) != int:
                    self.__on_add_log(10, "RST_TRAN_ERROR_TYPE", "", f"Lista przejść ma pole, które nie jest liczbą: {lane_transition}")
                    return False
                team, player, lane = lane_transition
                if team not in data:
                    data[team] = {}
                if player not in data[team]:
                    if lane == 0:
                        data[team][player] = [0]
                    else:
                        self.__on_add_log(10, "RST_TRAN_ERROR_LANE_1", "", f"Zawodnik {player} drużyny {team} nie ma toru '0' jako pierwszego")
                        return False
                else:
                    if data[team][player][-1] + 1 == lane:
                        data[team][player].append(lane)
                        if lane + 1 > number_lane:
                            number_lane = lane + 1
                    else:
                        self.__on_add_log(10, "RST_TRAN_ERROR_LANE_2", "", f"Zawodnik {player} drużyny {team} nie ma toru nie ma torów w odpowiedniej kolejności")
                        return False
        self.__number_of_team = len(list(data.keys()))
        self.__number_of_player_in_team_in_period = len(list(data.values())[0])
        print("__number_of_player_in_team_in_period", self.__number_of_player_in_team_in_period)
        self.__results_container.init_struct(self.__number_of_team, self.__number_of_player_in_team_in_period, self.__number_of_periods, number_lane)
        self.__status_on_lanes = [([] if l == 1 else None) for l in lanes]
        return True

    def change_lane_status(self, lane: int, status_new: int):
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
                self.__on_add_log(9, "RST_STATUS_EQ", f"{lane + 1}", f"Status rundy na torze {lane + 1} nie zmienił się: poprzedni status {status_old}, nowy {status_new}")
            elif status_old + 1 < status_new or (status_new < 2 and status_old <= 2):
                self.__on_add_log(9, "RST_STATUS_JMP", f"{lane + 1}", f"Zmiana statusu rundy na torze {lane + 1}: poprzedni status {status_old}, nowy {status_new}")
                self.__status_on_lanes[lane][-1] = status_new
            else:
                self.__change_lane_status__add_new_round(lane, status_new)
        if status_new == 5:
            self.__check_end_period()
        elif status_new in [0, 3]:
            self.__check_start_period()

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
        if new_round != self.__round:
            self.__on_add_log(3, "RST_ROUND_CHANGE", f"", f"Zmiana rundy. Stara: {self.__round}, nowa: {new_round}")
            self.__round = new_round

    def __check_end_period(self):
        for list_status_lane in self.__status_on_lanes:
            if list_status_lane is None:
                continue
            round_on_lane = len(list_status_lane)
            if list_status_lane[-1] != 5 or round_on_lane % len(self.__transitions) != 0:
                return False
        self.__period_is_running = False
        self.__results_container.end_period()
        # TODO stworzenie nowych zawodników w classicc
        self.__on_add_log(6, "RST_PERIOD_END", f"", f"Zakończono okres: {self.__period}")
        return True

    def __check_start_period(self):
        if self.__period_is_running:
            return False
        for list_status_lane in self.__status_on_lanes:
            if list_status_lane is None:
                continue
            round_on_lane = len(list_status_lane)
            if len(list_status_lane) == 0:
                return False
            if list_status_lane[-1] == 5 or round_on_lane % len(self.__transitions) != 1:
                return False
        self.__period_is_running = True
        self.__period += 1
        self.__on_add_log(6, "RST_PERIOD_START", f"", f"Nowy okres: {self.__period}")
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
        status_on_lane = self.__status_on_lanes[lane]
        print("S", status_on_lane)
        round_on_lane = len(status_on_lane) - 1
        if status_on_lane is None or round_on_lane < 0:
            return False
        status = status_on_lane[-1]
        round_in_period = len(self.__transitions)
        period, round_on_period = round_on_lane // round_in_period, round_on_lane % round_in_period
        print(period, round_on_period)
        player = copy.deepcopy(self.__transitions[round_on_period][lane])
        print("P", player)
        if player == -1:
            return False
        if status < 3:
            player[2] = -1
        player[1] += period * self.__number_of_player_in_team_in_period
        print(player, period, self.__number_of_player_in_team_in_period)
        return status, player

    def __get_player_on_lane_for_results_or_time(self, lane: int) -> tuple[int, int, int] | bool:
        result = self.__get_player_on_lane(lane)
        if not result or result[0] in [0, 2, 3, 5]:
            return False
        return result[1]

    def __get_currently_playing_players(self) -> list[tuple[int, tuple[int, int, int]] | None] | None:
        if self.__status_on_lanes is None or self.__round == -1:
            return None
        list_playing_players = []
        for i, list_status_on_lane in enumerate(self.__status_on_lanes):
            round_in_period = len(self.__transitions)
            period, round_on_period = self.__round // round_in_period, self.__round % round_in_period
            if self.__transitions[round_on_period][i] == -1 or list_status_on_lane is None or len(list_status_on_lane) == 0:
                list_playing_players.append(None)
                continue
            player = copy.deepcopy(self.__transitions[round_on_period][i])
            player[1] += period * self.__number_of_player_in_team_in_period
            status = list_status_on_lane[self.__round]
            list_playing_players.append((status, player))
        return list_playing_players

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
        # currently_playing_players: list[tuple[int, tuple[int, int, int]] | None] | None = self.__get_currently_playing_players()
        # if currently_playing_players is None:
        #     return None
        # return_list = []
        # for lane, playing_players in enumerate(currently_playing_players):
        # if playing_players is None:
        #     return_list.append(None)
        # else:
        # status, who = playing_players
        print(self.__results_container.get_dict_with_results(list_of_result_names, (0, 0, 0), 0))
        return self.__results_container.get_dict_with_results(list_of_result_names, (0, 0, 0), 0)
        # return return_list