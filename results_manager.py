import copy
from typing import Callable
from game_type_manager import GameType, Transition
from results_container import ResultsContainer


class ResultsManager:
    def __init__(self, results_container: ResultsContainer, game_type: GameType, on_add_log: Callable[[int, str, str, str, bool], None]):
        """
        :param results_container: <ResultsContainer> container for storing results
        :param game_type: <GameType> an object with details about the selected game type
        :param on_add_log: <Callable[[int, str, str, str, bool], None]> function to add logs

        self.__results_container: <ResultsContainer> container for storing results
        self.__game_type: <GameType> an object with details about the selected game type
        self.__on_add_log: <Callable[[int, str, str, str, bool], None]> function to add logs
        self.__list_of_blocks: <list[Transition]> every single object is one block
        self.__block_number: <int> the largest block number in which all the lanes are
        self.__max_block_number: <int> the largest block number in which at least one track is
        self.__block_is_running: <bool> whether the block number whose number is in the variable self.__block_number is still active
        self.__round: <int> the round number that is on all lanes min([x for x in self.__status_on_lanes])
        self.__status_on_lanes: list[list[int] | None] list of all rounds on all lanes

        Info:
            1. variables "self.__block_number" and "self.__max_block_number" have equal values almost all the time.
                "self.__block_is_running" is greater than "self.__block_number" by 1 only in
                the time between when a new block starts on some track and when a new block starts on all tracks
            2. you cannot remove blocks whose indexes are less than or equal to "self.__block_is_running"
        # TODO: uproszczenie self.__status_on_lanes z list[int, ....] do list[int, int]
        """
        self.__results_container: ResultsContainer = results_container
        self.__on_add_log: Callable[[int, str, str, str, bool], None] = on_add_log
        self.__game_type: GameType = game_type
        self.__list_of_blocks: list[Transition] = []
        self.__block_number: int = -1
        self.__max_block_number: int = -1
        self.__block_is_running: bool = False
        self.__round: int = -1
        self.__status_on_lanes: list[list[int] | None] = [([] if l == 1 else None) for l in game_type.lanes]
        self.__results_container.init_struct(self.__game_type.number_team, self.__game_type.number_player_in_team_in_period)
        self.__functions_wait_to_new_block: list[Callable] = []
        if self.__game_type.type == "league": # TODO Przenieś to do PlayerSectionLEague
            for _ in range(self.__game_type.number_periods):
                self.add_block("")

    def add_block(self, transitions_name: str) -> bool:
        """
        This method add new block to self.__list_of_block and create new players

        :param transitions_name: <str> name of the added block
        :return: <bool> True - success, False - not exist transitions with this name

        Logs:
            RST_BLOCK_ADD - 3 - Added new block
            RST_BLOCK_EADD - 0 - Successfully added new block
        """
        if transitions_name not in self.__game_type.transitions:
            return False
        block_number = len(self.__list_of_blocks) + 1
        self.__on_add_log(3, "RST_BLOCK_ADD", f"", f"Dodano blok numer {block_number} o nazwie {transitions_name}", False)

        transition: Transition = self.__game_type.transitions[transitions_name]
        self.__list_of_blocks.append(transition)
        self.__results_container.init_block(transition.number_lane)
        self.__on_add_log(0, "RST_BLOCK_EADD", f"", f"Pomślnie dodano blok numer {block_number} o nazwie {transitions_name}", False)
        return True

    def change_lane_status(self, lane: int, status_new: int) -> bool:
        """
        This method change status on lane number 'lane' to 'status_new'

        :param lane: <int> lane number
        :param status_new: <int> new status
        :return: <bool> True - status was changed, False - was problem

        Logs:
            RST_STATUS_EQ - 9 - A message arrived that caused the status to not change
            RST_STATUS_JMP - 9 - A message was received that caused a jumped change in status
            RST_STATUS_OK - 3 - Status has been changed

        Info:
            1. In method is line "if status_old != 3:" because"
                the kegeln program sends messages in the order "set name" then "initialize game", and "set name" is
                optional, so both messages change state to 3, because if only the second one were changed, the name
                would be incorrectly assigned
        """
        if self.__block_number == self.__game_type.number_periods - 1 and not self.__block_is_running:
            return False
        if self.__status_on_lanes[lane] is None:
            return False
        if len(self.__status_on_lanes[lane]) == 0:
            self.__change_lane_status__add_new_round(lane, status_new)
        else:
            status_old = self.__status_on_lanes[lane][-1]
            if status_old + 1 == status_new:
                self.__on_add_log(3, "RST_STATUS_OK", f"{lane + 1}", f"Poprawna zmiana statusu rundy na torze {lane + 1}: poprzedni status {status_old}, nowy {status_new}", False)
                self.__status_on_lanes[lane][-1] = status_new
            elif status_old == status_new:
                if status_old != 3:
                    self.__on_add_log(9, "RST_STATUS_EQ", f"{lane + 1}", f"Status rundy na torze {lane + 1} nie zmienił się: poprzedni status {status_old}, nowy {status_new}", True)
            elif status_old + 1 < status_new or (status_new < 2 and status_old <= 2):
                self.__on_add_log(9, "RST_STATUS_JMP", f"{lane + 1}", f"Zmiana statusu rundy na torze {lane + 1}: poprzedni status {status_old}, nowy {status_new}", True)
                self.__status_on_lanes[lane][-1] = status_new
            else:
                self.__change_lane_status__add_new_round(lane, status_new)
        if status_new == 5:
            self.__check_end_block()
        return True

    def __change_lane_status__add_new_round(self, lane: int, status_new: int) -> None:
        """
        This method add new round on lane, and if conditions is complete then change block

        :param lane: <int> lane number
        :param status_new: <int> new status
        :return: None

        Logs:
            RST_NSTATUS_JMP - 9 - New round starts with bad status
            RST_NSTATUS_OK - 3 - New round starts on lane
            RST_ROUND_CHANGE - 3 - New round starts on all lanes
            RST_BLOCK_NEWO - 3 - A new block has been started on one lane
            RST_BLOCK_NEW - 3 - A new block has been started on all lanes
        """
        if status_new == 0 or status_new == 3:
            self.__on_add_log(3, "RST_STATUS_OK", f"{lane + 1}", f"Nowa runda na torze {lane + 1}. Status: {status_new}", False)
        else:
            self.__on_add_log(9, "RST_STATUS_JMP", f"{lane + 1}", f"Nowa runda na torze {lane + 1}. Status: {status_new}, powinien być 0 lub 3", True)
        self.__status_on_lanes[lane].append(status_new)

        new_round = len(self.__status_on_lanes[lane]) - 1
        for list_status_lane in self.__status_on_lanes:
            if list_status_lane is None:
                continue
            new_round = min(new_round, len(list_status_lane) - 1)

        if len(self.__status_on_lanes[lane]) - 1 >= sum([block.number_lane for block in self.__list_of_blocks[:self.__max_block_number+1]]):
            self.__max_block_number += 1
            self.__on_add_log(3, "RST_BLOCK_NEWO", f"", f"Rozpoczęto blok numer {self.__max_block_number + 1} zainicjował go tor {lane}", False)
            if self.__max_block_number == len(self.__list_of_blocks):
                self.add_block(self.__game_type.default_transitions)

        if new_round != self.__round:
            self.__on_add_log(3, "RST_ROUND_CHANGE", f"", f"Zmiana rundy. Stara: {self.__round}, nowa: {new_round}", False)
            self.__round = new_round
            if self.__round == sum([block.number_lane for block in self.__list_of_blocks[:self.__block_number+1]]):
                self.__block_number += 1
                self.__block_is_running = True
                self.__on_add_log(3, "RST_BLOCK_NEW", f"", f"Rozpoczęto blok numer {self.__block_number + 1} na wszystkich torach", True)
                for f in self.__functions_wait_to_new_block:
                    f()

    def __check_end_block(self) -> bool:
        """
        This method checks if the block has been finished

        :return: <bool> True - block has been finished, False - otherwise
        """
        if self.__block_number == -1:
            return False
        round_to_end_block = sum([block.number_lane for block in self.__list_of_blocks[:self.__block_number + 1]])
        for list_status_lane in self.__status_on_lanes:
            if list_status_lane is not None:
                if list_status_lane[-1] != 5 or len(list_status_lane) < round_to_end_block:
                    return False
        self.__block_is_running = False
        self.__on_add_log(6, "RST_PERIOD_END", f"", f"Zakończono blok: {self.__block_number + 1} na wszystkich torach", True)
        return True

    def change_time_on_lane(self, lane: int, time: float) -> bool:
        """
        This method will update the time on the lane

        :param lane: <int> lane number
        :param time: <float> new time
        :return: <bool> True - time has been updated, False - otherwise
        """
        who = self.__get_player_on_lane_for_results_or_time(lane)
        if not who:
            return False
        self.__results_container.update_time(who, time)
        return True

    def add_result_to_lane(self, lane, type_update: bytes, throw: int, throw_result: int, lane_sum: int, total_sum: int,
                      next_arrangements: int, all_x: int, time: float, beaten_arrangements: int, card: int, raw_message: bytes) -> bool:
        """
        This method updates the player's result on lane

        :param lane: <int> lane number
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
        :return: <bool> True - result has been added, False - otherwise
        """
        who = self.__get_player_on_lane_for_results_or_time(lane)
        if not who:
            return False
        self.__results_container.update_result(who, type_update, throw, throw_result, lane_sum, total_sum,
                      next_arrangements, all_x, time, beaten_arrangements, card, raw_message)
        return True

    def trial_setup_on_lane(self, lane: int, max_throw: int, time: float) -> bool:
        """
        This method initiates a player trial, the player can make "max_throw" throws or play for "time" amount of time

        :param lane: <int> lane number
        :param max_throw: <int> max number of throws a player can play in trial
        :param time: <float> max time a player can play in trial
        :return: <bool> True - trial has been initialised, False - otherwise
        """
        result = self.__get_player_on_lane(lane)
        if not result or result[0] != 0:
            return False
        self.__results_container.init_setup_trial(result[1], max_throw, time)
        return True

    def game_setup_on_lane(self, lane: int, number_p: int, number_z: int, time: float, total_sum: int, all_x: int, card: int) -> bool:
        """
        This method initiates a player's lane

        :param lane: <int> lane number
        :param number_p: <int> number of throws played to full
        :param number_z: <int> number of throws played to clear off
        :param time: <float> max time a player can play in trial
        :param total_sum: <int> number of pins knocked down from previous lanes
        :param all_x: <int> number of empty throws from previous lanes
        :param card: <int> <int> 0 - no card, 1 - yellow card, 3 - red card
        :return: <bool> True - game has been initialised, False - otherwise
        """
        result = self.__get_player_on_lane(lane)
        if not result or result[0] != 3:
            return False
        self.__results_container.init_setup_game(result[1], number_p, number_z, time, total_sum, all_x, card)
        return True

    def set_player_name_if_not_set(self, lane: int, name: str) -> bool:
        """
        This method sets the player name if it is not already set

        :param lane: <int> lane number
        :param name: <str> player name
        :return: None
        """
        result = self.__get_player_on_lane(lane)
        if not result:
            return False
        self.__results_container.set_player_name_if_not_set(result[1], name)
        return True

    def set_player_name(self, team: int, player: int, name: str) -> bool:
        """
        This method sets the player name

        :param team: <int> team number
        :param player: <int> player number
        :param name: <str> player name
        :return: True
        """
        self.__results_container.set_player_name((team, player), name)
        return True

    def set_player_list_name(self, team: int, player: int, list_name: list[tuple[str, int]]) -> bool:
        """
        This method set player name or player's if was playing more than one player

        :param team: <int> team number
        :param player: <int> player number
        :param list_name: <list[tuple[str, int]]> player name and throw number when he started playing
        :return: True
        """
        self.__results_container.set_player_list_name((team, player), list_name)
        return True

    def set_player_previous_sum(self, team: int, player: int, previous_sum: int) -> bool:
        """
        This method sets the player previous sum e.g. the result from the elimination

        :param team: <int> team number
        :param player: <int> player number
        :param previous_sum: <int> e.g. the result from the elimination
        :return: True
        """
        self.__results_container.set_player_previous_sum((team, player), previous_sum)
        return True

    def set_team_name(self, team: int, name: str) -> bool:
        """
        This method sets the team name

        :param team: <int> number_team
        :param name: <str> team name
        :return: None
        """
        self.__results_container.set_team_name(team, name)
        return True

    def __get_player_on_lane(self, lane: int) -> tuple[int, tuple[int, int, int]] | bool:
        """
        This method returns who is playing on the lane

        :param lane: <int> lane number
        :return: False | tuple[int, tuple[int, int, int]] in tuple -> status on lane, and (team_index, player_index, lane_index)
                if lane_index == -1 it means on lane is trial
        """
        if self.__block_number == self.__game_type.number_periods and not self.__block_is_running:
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
        player[1] += block * self.__game_type.number_player_in_team_in_period
        return status, tuple(player)

    def __get_player_on_lane_for_results_or_time(self, lane: int) -> tuple[int, int, int] | bool:
        """
        This method return player only if player now playing trial or game

        :param lane: <int> lane number
        :return: False - no one is playing now, tuple[int, int, int] - player info
        """
        result = self.__get_player_on_lane(lane)
        if not result or result[0] in [0, 2, 3, 5]:
            return False
        return result[1]

    def __get_currently_playing_players(self) -> list[tuple[int, tuple[int, int, int]] | None] | None:
        """
        The method returns who is playing on the lanes and what is their game status

        :return: None - was problem, list - information about players
        """
        if self.__round == -1 or self.__block_number == -1:
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
            player[1] += self.__block_number * self.__game_type.number_player_in_team_in_period
            status = list_status_on_lane[self.__round]
            list_playing_players.append((status, player))
        return list_playing_players

    def __get_block_and_round(self, round_number: int) -> tuple[int, int]:
        """
        This method translate round_number to block number and lane on block

        :param round_number: <int> round number
        :return: tuple[int, int] - first block_number, second lane_on_block
        """
        block_number = 0
        for block in self.__list_of_blocks:
            if round_number >= block.number_lane:
                round_number -= block.number_lane
                block_number += 1
        return block_number, round_number

    def get_scores_of_players_now_playing(self, list_of_result_names: list[str]) -> list[dict | None] | None:
        """
        The method takes a list of keys 'list_of_result_names' and returns a dictionary in which it adds a value to each
        key. It returns such a dictionary to each track where someone is playing

        :param list_of_result_names: <list[str]> - list of statistics names
        :return: None - was problem, list[dict | None] each element is a single lane, None means there is no player on lane, dict - player statistics
        """
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

    def get_scores(self, list_of_result_names: list[str]) -> list[dict]:
        """
        The method takes a list of keys 'list_of_result_names' and returns a dictionary where it adds a value to each key

        :param list_of_result_names: <list[str]> list of statistics names
        :return: dict - team/player/lane statistics
        """
        return [self.__results_container.get_dict_with_results(list_of_result_names, (0, 0, 0), 0)]

    def get_number_of_blocks(self) -> int:
        return len(self.__list_of_blocks)

    def add_function_wait_to_new_block(self, func: Callable):
        self.__functions_wait_to_new_block.append(func)

    def get_player_name_in_relative_block(self, team: int, player: int, relative_block: int) -> str | None:
        """
        :param team: <int> team number
        :param player: <int> relative player number (player in block)
        :param relative_block: <int> 0 - actual block, -1 - previous block, 1 - next block
        :return: str - str - player name, None - the expected block does not exist
        """
        block = self.__block_number + relative_block
        if block < 0 or block >= self.get_number_of_blocks():
            return None
        previous_players = block * self.__game_type.number_player_in_team_in_period
        return self.__results_container.get_player_name((team, player + previous_players))

    def set_player_name_in_relative_block(self, team: int, player: int,  relative_block: int, name: str) -> bool:
        """
        :param team: <int> team number
        :param player: <int> relative player number (player in block)
        :param relative_block: <int> 0 - actual block, -1 - previous block, 1 - next block
        :param name: <str> new player name
        :return: True - player name is set, False - the expected block does not exist
        """
        block = self.__block_number + relative_block
        if block < 0 or block >= self.get_number_of_blocks():
            return False
        previous_players = block * self.__game_type.number_player_in_team_in_period
        self.__results_container.set_player_name((team, player + previous_players), name)
        return True
