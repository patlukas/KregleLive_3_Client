from results_container_player import ResultsContainerPlayer


class ResultsContailerTeam:
    def __init__(self, number_player_in_team: int):
        """
        :param number_player_in_team: <int> number player in team in block

        self.__number_player_in_team: <int> number player in team in block
        self.name: <str> team name - default ""
        self.pd: <float> team points
        self.pm: <float> match points
        self.ps: <float> set points
        self.different: <int> difference between team totals, positive value i.e. team wins
        self.players: <list[PlayerResultsContainer]> players
        """
        self.__number_player_in_team: int = number_player_in_team
        self.name: str = ""
        self.pd: float = 0
        self.pm: int = 0
        self.ps: float = 0
        self.different: int = 0
        self.players: list[ResultsContainerPlayer] = []

    def init_block(self, number_lane: int) -> None:
        """
        This method creates a block of new players who will play "number_lane" number of lanes

        :param number_lane: <int> how many lanes will players play
        :return: None
        """
        for _ in range(self.__number_player_in_team):
            self.players.append(ResultsContainerPlayer(number_lane))

    def calculate_league_points(self, player: int, lane: int, rival_team_sum: int, rival_player_total_sum: int, rival_player_lane_sum: int) -> None:
        """
        This method calls the function to calculate the player's league points, and then calculates the team's league points.

        :param player: <int> player number
        :param lane: <int> lane number <0, ...>
        :param rival_team_sum: <int> second team sum
        :param rival_player_total_sum: <int> second player total sum
        :param rival_player_lane_sum: <int> second player lane sum
        :return: None
        """
        self.players[player].calculate_league_points(lane, rival_player_total_sum, rival_player_lane_sum)
        self.ps = sum([p.ps for p in self.players])
        self.pd = sum([p.pd for p in self.players])
        t_s = self.get_sum()
        self.pd += 2.0 if t_s > rival_team_sum else 1.0 if t_s == rival_team_sum else 0.0
        self.different = t_s - rival_team_sum

    def calculate_pm_points(self, rival_pd: float) -> None:
        """
        This method set match points

        :param rival_pd: <float> opposing team's team points
        :return: None
        """
        self.pm = 2 if self.pd > rival_pd else 1 if self.pd == rival_pd else 0

    def get_sum(self) -> int:
        """
        This method returns the sum of the team

        :return: <int> team sum
        """
        return sum([p.get_sum() for p in self.players])

    def get_stat(self, player: str, lane: str, stat: str, option: str) -> str:
        """
        This method returns the value of the statistic

        :param player: <int> player number
        :param lane: <int> lane number
        :param stat: <str> statistics name
        :param option: <str> "" or str(int) with option number - more in documentation
        :return: <str> "" or value
        """
        if option != "":
            option_int = int(option)
            result_value = 2 ** (16 if self.pm == 2 else 15 if self.pm == 1 else 14)
            diff_value = 2 ** (13 if self.different > 0 else 12 if self.different == 0 else 11)
            if (option_int & result_value) != result_value or (option_int & diff_value) != diff_value:
                return ""
        if player == "":
            if stat == "name":
                return self.name
            v = self.get_stat_value(stat)
            if v is None:
                return ""
            if v == 0 and option != "" and (int(option) & 2**17) != 2**17:
                return ""
            return str(v)
        else:
            return self.players[int(player)].get_stat(lane, stat, option)

    def get_stat_value(self, stat) -> int | float | None:
        """
        This method returns the value of the statistic

        :param stat: <str> statistics name
        :return: <int | float | None> int | float if statistics exists, None if not
        """
        if stat in ["s", "p", "z", "x", "number_throw"]:
            return self.__get_sum_stat_value(stat)
        match stat:
            case "is":
                return 1
            case "pm":
                return int(self.pm) if self.pm == int(self.pm) else self.pm
            case "pd":
                return int(self.pd) if self.pd == int(self.pd) else self.pd
            case "ps":
                return int(self.ps) if self.ps == int(self.ps) else self.ps
            case "different":
                return self.different
        return None

    def set_name(self, name: str) -> None:
        """
        This method set team name

        :param name: <str> team name
        :return: None
        """
        self.name = name

    def __get_sum_stat_value(self, stat) -> int | float:
        """
        This method returns the sum of all players' stats.

        :param stat: <str> statistics name
        :return: <int | float> statistics value
        """
        sum_v = 0
        for p in self.players:
            v = p.get_stat_value(stat)
            if v is not None:
                sum_v += v
        return sum_v
