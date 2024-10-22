from typing import Callable

from results_container_team import ResultsContailerTeam


class ResultsContainer:
    def __init__(self, on_add_log: Callable[[int, str, str, str], None]):
        """
        :param on_add_log:  <Callable[[int, str, str, str], None]> function to add logs

        self.teams: <list[TeamsResultsContainer]> list of team
        """
        self.__on_add_log: Callable[[int, str, str, str], None] = on_add_log
        self.teams: list[ResultsContailerTeam] = []

    def init_struct(self, number_team: int, number_player_in_team: int) -> bool:
        """
        This method initializes the number of teams, later the number of teams cannot be changed

        :param number_team: <int> number of teams
        :param number_player_in_team: <int> number player in team in block
        :return: True
        """
        self.teams = [ResultsContailerTeam(number_player_in_team) for _ in range(number_team)]
        return True

    def init_block(self, number_lane: int) -> None:
        """
        This method create new block of players who will play 'number_lane' lanes

        :param number_lane: <int> how many lanes will the added players play
        :return: None
        """
        for team in self.teams:
            team.init_block(number_lane)

    def update_result(self, who: tuple[int, int, int], type_update: bytes, throw: int, throw_result: int, lane_sum: int,
                      total_sum: int, next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int) -> None:
        """
        This method updates the player's result on lane 'who[2]'

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :param type_update: <bytes> "g" was yellow card, "h" was red card, "f" was empty throw, "k" result was edit, "w"  was not special result
        :param throw: <int> number of throw on lane <1, ...>
        :param throw_result: <int> number of beaten pins on this throw <0..9>
        :param lane_sum: <int> result on this lane <0, ...>
        :param total_sum: <int> result on all game <0, ...>
        :param next_arrangements: <int> what arrangements will be next <0, 511>
        :param all_x: <int> number of empty throw in game <0, ...>
        :param time: <float> how much time is left <0.0, ...>
        :param beaten_arrangements: <int> what arrangements was beaten in this throw <0, 511>
        :param card: <int> 0 - no card, 1 - yellow card, 3 - red card
        :return: None
        """
        self.teams[who[0]].players[who[1]].update_result(
            who[2], type_update, throw, throw_result, lane_sum, total_sum, next_arrangements, all_x, time,
            beaten_arrangements, card
        )

    def update_time(self, who: tuple[int, int, int], time: float) -> None:
        """
        This method updates the player's time on lane 'who[2]'

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :param time: <float> how much time is left <0.0, ...>
        :return: None
        """
        self.teams[who[0]].players[who[1]].update_time(who[2], time)

    def init_setup_trial(self, who: tuple[int, int, int], max_throw: int, time: float) -> None:
        """
        This method initiates a player trial, the player can make "max_throw" throws or play for "time" amount of time

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :param max_throw: <int> max number of throws a player can play in trial
        :param time: <float> max time a player can play in trial
        :return: None
        """
        self.teams[who[0]].players[who[1]].trial.init_setup_trial(max_throw, time)

    def init_setup_game(self, who: tuple[int, int, int], number_p: int, number_z: int, time: float, total_sum: int, all_x: int, card: int) -> None:
        """
        This method initiates a player's lane

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :param number_p: <int> number of throws played to full
        :param number_z: <int> number of throws played to clear off
        :param time: <float> max time a player can play in trial
        :param total_sum: <int> number of pins knocked down from previous lanes
        :param all_x: <int> number of empty throws from previous lanes
        :param card: <int> <int> 0 - no card, 1 - yellow card, 3 - red card
        :return: None
        """
        self.teams[who[0]].players[who[1]].lanes[who[2]].init_setup(number_p, number_z, time, total_sum, all_x, card)

    def set_player_name_if_not_set(self,who: tuple[int, int, int], name: str) -> None:
        """
        This method sets the player name if it is not already set

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :param name: <str> player name
        :return: None
        """
        self.teams[who[0]].players[who[1]].set_name_if_not_set(name)

    def set_player_name(self, who: tuple[int, int], name: str) -> None:
        """
        This method sets the player name

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :param name: <str> player name
        :return: None
        """
        self.teams[who[0]].players[who[1]].set_name(name)

    def set_team_name(self, team: int, name: str) -> None:
        """
        This method sets the team name

        :param team: <int> number_team
        :param name: <str> team name
        :return: None
        """
        self.teams[team].set_name(name)

    def get_dict_with_results(self, list_of_result_names: list[str], who: tuple[int, int, int] = (0, 0, 0), status: int = 0) -> dict:
        """
        The method takes a list of keys 'list_of_result_names' and returns a dictionary where it adds a value to each key

        :param list_of_result_names: <list[str]> more in documentation - the function returns the results that are associated with these keys
        :param who: <tuple(int, int, int)> first int is team_number and replace "T", second is player number and replace "P", third is lane_number and replace "L"
        :param status: <int> status number - more in documentation
        :return: <dict[str - all str form list_of_result_names: values: str]>
        """
        status = 2**status
        dict_result = {}
        who_str = list(map(str, who))
        dict_result["status"] = str(status)
        for name in list_of_result_names:
            try:
                name_head = name.split("&")[0]
                if name_head == "":
                    dict_result[name] = "1"
                name_split = name_head.replace("T", who_str[0]).replace("P", who_str[1]).replace("L", who_str[2]).split("|")
                if len(name_split) != 6:
                    continue
                if status != 0 and name_split[5] != "" and (int(name_split[5]) & status) != status:
                    dict_result[name] = ""
                    continue
                dict_result[name] = self.__get_stat(name_split[0], name_split[1], name_split[2], name_split[3], name_split[4])
            except Exception:
                dict_result[name] = ""
        return dict_result

    def __get_stat(self, team: str, player: str, lane: str, stat: str, option: str) -> str:
        """
        This method returns the value of the statistic

        :param team: <int> team number
        :param player: <int> player number
        :param lane: <int> lane number
        :param stat: <str> statistics name
        :param option: <str> "" or str(int) with option number - more in documentation
        :return: <str> "" or value
        """
        return self.teams[int(team)].get_stat(player, lane, stat, option)


class ResultsContainerLeague(ResultsContainer):
    def init_struct(self, number_team: int, number_player_in_team: int) -> bool:
        """
        This method initializes the number of teams, later the number of teams cannot be changed

        :param number_team: <int> number of teams
        :param number_player_in_team: <int> number player in team in block
        :return: bool - False is wrong number_team should be 2, True - everything is ok
        """
        if number_team != 2:
            self.__on_add_log(10, "RCR_L_INIT_ERROR_TEAM", "", f"Liczba zespołów powinna być równa 2, a jest {number_team}")
            return False
        return super().init_struct(number_team, number_player_in_team)

    def update_result(self, who: tuple[int, int, int], type_update: bytes, throw: int, throw_result: int, lane_sum: int,
                        total_sum: int, next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int) -> None:
        """
        This method updates the player's result on lane 'who[2]', and calculate league points

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :param type_update: <bytes> "g" was yellow card, "h" was red card, "f" was empty throw, "k" result was edit, "w"  was not special result
        :param throw: <int> number of throw on lane <1, ...>
        :param throw_result: <int> number of beaten pins on this throw <0..9>
        :param lane_sum: <int> result on this lane <0, ...>
        :param total_sum: <int> result on all game <0, ...>
        :param next_arrangements: <int> what arrangements will be next <0, 511>
        :param all_x: <int> number of empty throw in game <0, ...>
        :param time: <float> how much time is left <0.0, ...>
        :param beaten_arrangements: <int> what arrangements was beaten in this throw <0, 511>
        :param card: <int> 0 - no card, 1 - yellow card, 3 - red card
        :return: None
        """
        super().update_result(who, type_update, throw, throw_result, lane_sum, total_sum, next_arrangements, all_x, time,beaten_arrangements, card)
        if who[2] != -1:
            self.__calculate_league_points(who)

    def __calculate_league_points(self, who: tuple[int, int, int]) -> None:
        """
        This method calculates the team's league points

        :param who: <tuple(int: number_team, int: number_player, int: number_lane)> if lane number is -1 it means trial
        :return: None
        """
        rival_team_sum = [t.get_sum() for t in self.teams]
        rival_player_total_sum = [t.players[who[1]].get_sum() for t in self.teams]
        rival_player_lane_sum = [t.players[who[1]].lanes[who[2]].get_sum() for t in self.teams]
        for i, t in enumerate(self.teams):
            t.calculate_league_points(who[1], who[2], rival_team_sum[1-i], rival_player_total_sum[1-i], rival_player_lane_sum[1-i])
        rival_pd = [t.pd for t in self.teams]
        for i, t in enumerate(self.teams):
            t.calculate_pm_points(rival_pd[1-i])




