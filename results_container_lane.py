class _LaneContainer:
    def __init__(self):
        """
        self._number_p <int> number of throws during the game to full
        self._number_z <int> number of throws during the game to clear off
        self.number_of_throw <int> number of throws on lane
        self.sums <tuple[int, int, int]> result to full, result on lane, result on game
        self.x <int> number of empty throw on lane
        self.all_X <int> number of empty throw on game
        self.time <float> how much time is left
        self.list_results <list[int, None]> None - not have information about result on throw, int - number of beaten pins in specified throw
        self.list_arrangements <list[tuple[int, int], None]> None - not have information about throw, tuple - beaten arrangements, next arrangements
        self.card <int> 0 - no card, 1 - yellow, 3 - red
        self.list_card <list[tuple[int, int]]> first int - throw number, second int - 1 - yellow card, 2 - red card
        """
        self._number_p: int = 0
        self._number_z: int = 0
        self.number_of_throw: int = 0
        self.sums: tuple[int, int, int] = (0, 0, 0)
        self.x: int = 0
        self.all_x: int = 0
        self.ps: float = 0
        self.different: int = 0
        self.time: float = 0
        self.list_results: list[int | None] = []
        self.list_arrangements: list[tuple[int, int] | None] = []
        self.card: int = 0
        self.list_cards: list[tuple[int, int]] = []
        self.__started = False

    def update_result(self, type_update: bytes, throw: int, throw_result: int, lane_sum: int, total_sum: int,
                      next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int) -> None:
        """
        Method to add new result

        :param type_update: <bytes> "g" was yellow card, "h" was red card, "f" was empty throw, "k" result was edit, "w"  was not special result
        :param throw: <int> number of throw on lane <1, ...>
        :param throw_result: <int> number of beaten pins on this throw
        :param lane_sum: <int> result on this lane
        :param total_sum: <int> result on all game
        :param next_arrangements: <int> what arrangements will be next
        :param all_x: <int> number of empty throw in game
        :param time: <float> how much time is left
        :param beaten_arrangements: <int> what arrangements was beaten in this throw
        :param card: <int> 0 - no card, 1 - yellow card, 3 - red card
        :return: None
        """
        self.number_of_throw = throw
        self.card = card
        self.all_x = all_x
        self.time = time

        if not self.__started:
            self.__started = True

        if type_update == b"g":
            self.list_cards.append((throw, 1))
        elif type_update == b"h":
            self.list_cards.append((throw, 2))

        if throw <= self._number_p:
            self.sums = [lane_sum, lane_sum, total_sum]
        else:
            self.sums = [self.sums[0], lane_sum, total_sum]

        if type_update == b"f":
            self.x += 1
        if type_update != b"k" and 0 < throw <= self._number_p + self._number_z:
            self.list_results[throw-1] = throw_result
            self.list_arrangements[throw-1] = (beaten_arrangements, next_arrangements)

    def update_time(self, time: float) -> None:
        """
        Method to update time on lane

        :param time: <float> remaining lane time
        :return: <None>
        """
        self.time = time

    def get_sum(self) -> int:
        """
        Method to get the sum on lane

        :return: <int> sum on lane
        """
        return self.sums[1]

    def init_setup(self, number_p: int, number_z: int, time: float, total_sum: int, all_x: int, card: int) -> None:
        """
        This method sets the game time, initializes the result lists and set other parameters

        :param number_p: <int> number of throws during the game to full
        :param number_z: <int> number of throws during the game to clear away
        :param time: <float> time limit
        :param total_sum: <int> total score
        :param all_x: <int> number of missed throws
        :param card: <int> 0 - no card, 1 - yellow card, 3 - red card
        :return: None
        """
        self._number_p, self._number_z, self.time, self.all_x, self.card = number_p, number_z, time, all_x, card
        self.sums = (0, 0, total_sum)
        self.list_results: list[int | None] = [None] * (number_p + number_z)
        self.list_arrangements: list[tuple[int, int] | None] = [None] * (number_p + number_z)

    def get_stat(self, stat: str, option: str) -> str:
        """
        This method returns the value of the statistic

        :param stat: <str> statistics name
        :param option: <str> "" or str(int) with option number - more in documentation
        :return: <str> "" or value
        """
        if option != "":
            option_int = int(option)
            result_value = 2 ** (3 if self.ps == 1.0 else 2 if self.ps == 0.5 else 1)
            if (option_int & result_value) != result_value:
                return ""
            if not self.__started and (option_int & 2 ** 0) != 2 ** 0:
                return ""
        stat_split = stat.split("-")

        if len(stat_split) == 1:
            v = self.get_stat_value(stat)
            if v is None:
                return ""
            if v == 0 and option != "" and (int(option) & 2**15) != 2**15:
                return ""
            return str(v)
        else:
            match stat_split[0]:
                case "throw":
                    second = stat_split[1]
                    if second == "last":
                        t = self.number_of_throw - 1
                    else:
                        t = int(stat_split[1]) - 1
                    if t < 0 or t > len(self.list_results) or self.list_results[t] is None:
                        return ""
                    return str(self.list_results[t])
        return ""

    def get_stat_value(self, stat) -> int | float | None:
        """
        This method returns the value of the statistic

        :param stat: <str> statistics name
        :return: <int | float | None> int | float if statistics exists, None if not
        """
        match stat:
            case "is":
                return 1
            case "s":
                return self.sums[1]
            case "p":
                return self.sums[0]
            case "z":
                return self.sums[1] - self.sums[0]
            case "x":
                return self.x
            case "number_throw":
                return self.number_of_throw
            case "ps":
                return int(self.ps) if self.ps == int(self.ps) else self.ps
            case "different":
                return self.different
            case "time":
                return self.time
        return None

class ResultsContainerLane(_LaneContainer):
    def __init__(self) -> None:
        """
        self.ps <float> 0.0 - loses on lane, 0.5 - draws on lane, 1.0 - wins on lane
        """
        super().__init__()
        self.ps: float = 0

    def calculate_league_points(self, rival_player_lane_sum: int) -> None:
        """
        This method is used to calculate set points on a lane

        :param rival_player_lane_sum: <int> rival's score on this lane
        :return: None
        """
        t_s = self.get_sum()
        self.different = t_s - rival_player_lane_sum
        if t_s > 0 or rival_player_lane_sum > 0:
            self.ps = 1.0 if t_s > rival_player_lane_sum else 0.5 if t_s == rival_player_lane_sum else 0.0

class ResultsContainerTrial(_LaneContainer):
    def init_setup_trial(self, max_number_throw: int, time: float) -> None:
        """
        This method sets the trial time and initializes the result lists

        :param max_number_throw: <int> throw limit (number of throw when will be end trial)
        :param time: <float> time limit
        :return: None
        """
        super().init_setup(max_number_throw, 0, time, 0, 0, 0)
