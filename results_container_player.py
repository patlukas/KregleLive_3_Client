from results_container_lane import ResultsContainerTrial, ResultsContainerLane


class ResultsContainerPlayer:
    def __init__(self, number_lane: int):
        """
        :param number_lane: <int> number of lanes

        self.__number_player_in_team: <int> number player in team in block
        self.list_name: <str> player name, e.g. [("a", 0), ("b", 61)] player "a" started, "b" replaced him and played from throw 61
        self.pd: <float> team points [0, 0.5, 1]
        self.ps: <float> set points <0, number_lane>
        self.different: <int> difference between players' sum, positive value, i.e. player has higher sum
        self.__started: <bool> False - False - the player has not started yet, True - the player has started
        self.list_raw_messages: <list[bytes]> a list of raw messages received from lanes regarding a player's game
        self.list_raw_messages_trial: <list[bytes]> a list of raw messages received from lane regarding a player's trial
        self.previous_sum: <int> a field for storing e.g. the result from the elimination
        self.final_sum_is_result_of_adding: <bool> then total_sum = previous + actual, otherwise total = actual
        self.show_in_lane_table: <bool> default True
        self.trial: <LaneTrialContainer> trial
        self.players: <list[PlayerResultsContainer]> lanes
        """
        self.list_name: list[tuple[str, int]] = [("", 0)]
        self.team_name: str = ""
        self.pd: float = 0
        self.ps: float = 0
        self.different: int = 0
        self.__started = False
        self.list_raw_messages: list[bytes] = []
        self.list_raw_messages_trial: list[bytes] = []
        self.previous_sum: int = 0
        self.final_sum_is_result_of_adding: bool = True
        self.show_in_lane_table: bool = True
        self.trial: ResultsContainerTrial = ResultsContainerTrial()
        self.lanes: list[ResultsContainerLane] = [ResultsContainerLane() for _ in range(number_lane)]

    def calculate_league_points(self, lane: int, rival_player_total_sum: int, rival_player_lane_sum: int) -> None:
        """
        This method calls the function to calculate the lane's league points, and then calculates the player's league points.

        :param lane: <int> lane number <0, ...>
        :param rival_player_total_sum: <int> second player total sum
        :param rival_player_lane_sum: <int> second player lane sum
        :return: None
        """
        self.lanes[lane].calculate_league_points(rival_player_lane_sum)
        t_s = self.get_sum()
        self.ps = sum([l.ps for l in self.lanes])
        self.different = t_s - rival_player_total_sum
        if self.ps == (lane+1) / 2:
            self.pd = 1.0 if t_s > rival_player_total_sum else 0.5 if t_s == rival_player_total_sum else 0.0
        else :
            self.pd = 1.0 if self.ps > (lane+1)/2 else 0.0

    def get_sum(self) -> int:
        """
        This method returns the sum of the player

        :return: <int> team sum
        """
        return sum([l.get_sum() for l in self.lanes])

    def update_result(self, lane: int, type_update: bytes, throw: int, throw_result: int, lane_sum: int, total_sum: int,
                      next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int, raw_message: bytes) -> None:
        """
        This method updates result on lane

        :param lane: lane number
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
        :param raw_message <bytes> raw message received from the lane
        :return: None
        """
        if not self.__started:
            self.__started = True
        x = self.trial if lane == -1 else self.lanes[lane]
        if lane == -1:
            self.list_raw_messages_trial.append(raw_message)
        else:
            self.list_raw_messages.append(raw_message)
        x.update_result(type_update, throw, throw_result, lane_sum, total_sum, next_arrangements, all_x, time, beaten_arrangements, card)

    def update_time(self, lane: int, time: float) -> None:
        """
        This method updates time on lane

        :param lane: lane number
        :param time: <float> how much time is left <0.0, ...>
        :return: None
        """
        x = self.trial if lane == -1 else self.lanes[lane]
        x.update_time(time)

    def set_name_if_not_set(self, name: str) -> bool:
        """
        This method sets the player name if it is not already set

        :param name: <str> player name
        :return: <bool> new name set or not
        """
        if len(self.list_name) == 1 and self.list_name[0][0] == "":
            self.set_name(name)
            return True
        return False

    def set_name(self, name: str) -> None:
        """
        This method sets the player name

        :param name: <str> player name
        :return: None
        """
        self.list_name[0] = (name, 0)

    def set_list_name(self, list_name: list[tuple[str, int]]) -> None:
        """
        This method set player name or player's if was playing more than one player

        :param list_name: <list[tuple[str, int]]> player name and throw number when he started playing
        :return: None
        """
        list_name.sort(key=lambda x: x[1])
        self.list_name = list_name

    def get_stat(self, lane: str, stat: str, option: str) -> str:
        """
        This method returns the value of the statistic

        :param lane: <int> lane number
        :param stat: <str> statistics name
        :param option: <str> "" or str(int) with option number - more in documentation
        :return: <str> "" or value
        """
        if option != "":
            option_int = int(option)
            result_value = 2 ** (10 if self.pd == 1.0 else 9 if self.pd == 0.5 else 8)
            diff_value = 2 ** (7 if self.different > 0 else 6 if self.different == 0 else 5)
            if (option_int & result_value) != result_value or (option_int & diff_value) != diff_value:
                return ""
            if not self.__started and (option_int & 2 ** 4) != 2 ** 4:
                return ""
        if lane == "":
            if stat == "name_now_playing_player":
                return self.list_name[-1][0]
            # if stat == "show_on_lane_table":
            #     print(self.show_in_lane_table)
            #     if self.show_in_lane_table:
            #         return "1"
            #     return "0"
            if stat == "name":
                return self.get_name()
            if stat == "previous_sum":
                return str(self.previous_sum)
            if stat == "total_sum":
                if self.final_sum_is_result_of_adding:
                    return str(self.previous_sum + self.__get_sum_stat_value("s"))
                else:
                    return str(self.__get_sum_stat_value("s"))
            if stat == "s":
                if self.final_sum_is_result_of_adding:
                    return str(self.__get_sum_stat_value("s"))
                else:
                    return str(self.__get_sum_stat_value("s") - self.previous_sum)
            v = self.get_stat_value(stat)
            if v is None:
                return ""
            if v == 0 and option != "" and (int(option) & 2**15) != 2**15:
                return ""
            return str(v)
        elif lane == "trial":
            return self.trial.get_stat(stat, option)
        else:
            return self.lanes[int(lane)].get_stat(stat, option)

    def get_stat_value(self, stat) -> int | float | None:
        """
        This method returns the value of the statistic

        :param stat: <str> statistics name
        :return: <int | float | None> int | float if statistics exists, None if not
        """
        if stat in ["p", "z", "x", "number_throw"]:
            return self.__get_sum_stat_value(stat)
        match stat:
            case "is":
                return 1
            case "pd":
                return int(self.pd) if self.pd == int(self.pd) else self.pd
            case "ps":
                return int(self.ps) if self.ps == int(self.ps) else self.ps
            case "different":
                return self.different
        return None

    def __get_sum_stat_value(self, stat) -> int | float:
        """
        This method returns the sum of all lanes' stats.

        :param stat: <str> statistics name
        :return: <int | float> statistics value
        """
        sum_v = 0
        for l in self.lanes:
            v = l.get_stat_value(stat)
            if v is not None:
                sum_v += v
        return sum_v

    def get_name(self) -> str:
        """
        This method return player name, i more then one player was playing, give first letter of firstname and surname, and separate players by "/"

        :return: <str> players names
        """
        if len(self.list_name) == 1:
            return self.list_name[0][0]

        string = ""
        for name, _ in self.list_name:
            list_word = name.split()
            string += "/"
            if len(list_word) == 0:
                continue
            string += list_word[0]
            if len(list_word) > 1:
                string += " " + list_word[1][0]+"."
        else:
            string = string[1:]
        return string
