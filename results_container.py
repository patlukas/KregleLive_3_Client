from typing import Callable


class ResultsContainer:
    def __init__(self, on_add_log: Callable[[int, str, str, str], None]):
        """

        classic (wtedy oprócz poprzednich bloków, aktualnego, jest jeszcze przyszły)
        league - jest tyle blokó ile jest periodów
        """
        self.__on_add_log: Callable[[int, str, str, str], None] = on_add_log
        self.teams: list[TeamsResultsContainer] = []

    def init_struct(self, number_team: int, number_players_in_period: int, number_periods: int, number_lane: int) -> bool:
        self.teams = [TeamsResultsContainer(number_players_in_period * number_periods, number_lane) for _ in range(number_team)]
        return True

    def end_period(self) -> None:
        pass

    def update_result(self, who: tuple[int, int, int], type_update: bytes, throw: int, throw_result: int, lane_sum: int,
                      total_sum: int, next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int) -> None:
        if who[2] < 0:
            return
        self.teams[who[0]].players[who[1]].update_result(
            who[2], type_update, throw, throw_result, lane_sum, total_sum, next_arrangements, all_x, time,
            beaten_arrangements, card
        )

    def update_time(self, who: tuple[int, int, int], time: float) -> None:
        self.teams[who[0]].players[who[1]].update_time(who[2], time)

    def init_setup_trial(self, who: tuple[int, int, int], max_throw: int, time: float):
        self.teams[who[0]].players[who[1]].trial.init_setup_trial(max_throw, time)

    def init_setup_game(self, who: tuple[int, int, int], number_p: int, number_z: int, time: float, total_sum: int, all_x: int, card: int):
        self.teams[who[0]].players[who[1]].lanes[who[2]].init_setup(number_p, number_z, time, total_sum, all_x, card)

    def set_player_name_if_not_set(self,who: tuple[int, int, int], name: str):
        self.teams[who[0]].players[who[1]].set_name_if_not_set(name)

class ResultsContainerLeague(ResultsContainer):
    def init_struct(self, number_team: int, number_players_in_period: int, number_periods: int, number_lane: int) -> bool:
        if number_team != 2:
            self.__on_add_log(10, "RCR_L_INIT_ERROR_TEAM", "", f"Liczba zespołów powinna być równa 2, a jest {number_team}")
            return False
        if number_periods <= 0:
            self.__on_add_log(10, "RCR_L_INIT_ERROR_PERIODS", "", f"Liczba okresów musi być większa niż 0, a jest {number_periods}")
            return False
        return super().init_struct(number_team, number_players_in_period, number_periods, number_lane)

    def update_result(self, who: tuple[int, int, int], type_update: bytes, throw: int, throw_result: int, lane_sum: int,
                        total_sum: int, next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int) -> None:
        super().update_result(who, type_update, throw, throw_result, lane_sum, total_sum, next_arrangements, all_x, time,beaten_arrangements, card)
        self.__calculate_league_points(who)

    def __calculate_league_points(self, who: tuple[int, int, int]) -> None:
        rival_team_sum = [t.get_sum() for t in self.teams]
        rival_player_total_sum = [t.players[who[1]].get_sum() for t in self.teams]
        rival_player_lane_sum = [t.players[who[1]].lanes[who[2]].get_sum() for t in self.teams]
        for i, t in enumerate(self.teams):
            t.calculate_league_points(who[1], who[2], rival_team_sum[1-i], rival_player_total_sum[1-i], rival_player_lane_sum[1-i])


class TeamsResultsContainer:
    def __init__(self, number_players: int, number_lane: int):
        self.name: str = ""
        self.pm: float = 0
        self.ps: float = 0
        self.players: list[PlayerResultsContainer] = [PlayerResultsContainer(number_lane) for _ in range(number_players)]

    def calculate_league_points(self, player: int, lane: int, rival_team_sum: int, rival_player_total_sum: int, rival_player_lane_sum: int) -> None:
        self.players[player].calculate_league_points(lane, rival_player_total_sum, rival_player_lane_sum)
        self.ps = sum([p.ps for p in self.players])
        self.pm = sum([p.pm for p in self.players])
        t_s = self.get_sum()
        self.pm += 2.0 if t_s > rival_team_sum else 1.0 if t_s == rival_team_sum else 0.0

    def get_sum(self) -> int:
        return sum([p.get_sum() for p in self.players])


class PlayerResultsContainer:
    def __init__(self, number_lane: int):
        self.list_name: list[tuple[str, int]] = [("", 0)]
        self.team_name: str = ""
        self.pm: float = 0
        self.ps: float = 0
        self.trial: LaneTrialContainer = LaneTrialContainer()
        self.lanes: list[LaneResultsContainer] = [LaneResultsContainer() for _ in range(number_lane)]

    def calculate_league_points(self, lane: int, rival_player_total_sum: int, rival_player_lane_sum: int) -> None:
        self.lanes[lane].calculate_league_points(rival_player_lane_sum)
        t_s = self.get_sum()
        self.ps = sum([l.ps for l in self.lanes])
        if self.ps == lane / 2:
            self.pm = 1.0 if t_s > rival_player_total_sum else 0.5 if t_s == rival_player_total_sum else 0.0
        else :
            self.pm = 1.0 if self.ps > lane/2 else 0.0

    def get_sum(self) -> int:
        return sum([l.get_sum() for l in self.lanes])

    def update_result(self, lane: int, type_update: bytes, throw: int, throw_result: int, lane_sum: int, total_sum: int,
                      next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int) -> None:
        x = self.trial if lane == -1 else self.lanes[lane]
        x.update_result(type_update, throw, throw_result, lane_sum, total_sum, next_arrangements, all_x, time, beaten_arrangements, card)

    def update_time(self, lane: int, time: float) -> None:
        x = self.trial if lane == -1 else self.lanes[lane]
        x.update_time(time)

    def set_name_if_not_set(self, name: str) -> None:
        if len(self.list_name) == 1 and self.list_name[0][0] == "":
            self.set_name(name)

    def set_name(self, name: str) -> None:
        self.list_name[0] = (name, 0)


class LaneContainer:
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
        self.time: float = 0
        self.list_results: list[int | None] = []
        self.list_arrangements: list[tuple[int, int] | None] = []
        self.card: int = 0
        self.list_cards: list[tuple[int, int]] = []

    def update_result(self, type_update: bytes, throw: int, throw_result: int, lane_sum: int, total_sum: int,
                      next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int) -> None:
        """
        Method to add new result

        :param type_update: <bytes> "g" was yellow card, "h" was red card, "f" was empty throw, "k" result was edit, "w"  was not special result
        :param throw: <int> number of throw on lane
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
        self.number_of_throw = throw_result
        self.card = card
        self.all_x = all_x
        self.time = time

        if type_update == b"g":
            self.list_cards.append((throw, 1))
        elif type_update == b"h":
            self.list_cards.append((throw, 2))

        if throw <= self._number_p:
            self.sums = [lane_sum, lane_sum, total_sum]
        else:
            self.sums = [self.sums[0], lane_sum, total_sum]

        if type_update != b"f" or beaten_arrangements == 0:
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


class LaneResultsContainer(LaneContainer):
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
        if t_s > 0 or rival_player_lane_sum > 0:
            self.ps = 1.0 if t_s > rival_player_lane_sum else 0.5 if t_s == rival_player_lane_sum else 0.0


class LaneTrialContainer(LaneContainer):
    def init_setup_trial(self, max_number_throw: int, time: float) -> None:
        """
        This method sets the trial time and initializes the result lists

        :param max_number_throw: <int> throw limit (number of throw when will be end trial)
        :param time: <float> time limit
        :return: None
        """
        super().init_setup(max_number_throw, 0, time, 0, 0, 0)
