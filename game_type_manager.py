"""This module read game types from game_types.json"""
#TODO Add comments
#TODO: przekaż ścieżkę do pliku config w argumencie, ścieżkę przechowuje w settings
import json
import os
from typing import Literal


class GameTypesManagerError(Exception):
    """
        List code:
            13-000 - FileNotFoundError - if game_types.json does not exist
            13-001 - ValueError - if config.json format is not correct
            13-002 - KeyError - if config doesn't have required fields
            13-003 - TypeError - parameter has wrong type
            13-004 - ConditionError - parameter doesn't meet the condition
            13-005 - TransitionError - transition is incorrect

    """
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__()


class GameTypesManager:
    def __init__(self):
        self.__game_types: dict[str: GameType] = {}
        self.game_type: GameType | None = None
        loaded_game_types: dict = self.__get_game_types()
        self.__dict_with_transitions = {}
        self.__check_correctness_data(loaded_game_types)
        self.__check_transitions(loaded_game_types)

    def get_list_game_type_name(self) -> list[str]:
        return list(self.__game_types.keys())

    def select_game_type(self, game_type_name: str):
        if game_type_name in self.__game_types:
            self.game_type = self.__game_types[game_type_name]
            return True
        return False

    @staticmethod
    def __get_game_types() -> dict:
        try:
            file = open("settings/game_types.json")
        except FileNotFoundError:
            raise GameTypesManagerError("13-000", "Nie znaleziono pliku {}".format(os.path.abspath("settings/game_types.json")))
        try:
            data = json.load(file)
        except ValueError:
            raise GameTypesManagerError("13-001", "Niewłaściwy format danych w pliku {}".format(os.path.abspath("settings/game_types.json")))
        return data

    def __check_correctness_data(self, loaded_game_types: dict):
        for k, v in loaded_game_types.items():
            self.__check_value(k, v, "type", str, '{v} in ["classic", "league"]')
            self.__check_value(k, v, "lanes", list, 'all(x in [0, 1] for x in {v})')
            if v["type"] == "league":
                self.__check_value(k, v, "number_of_changes", int, '{v} >= 0')
                self.__check_value(k, v, "number_periods", int, '{v} > 0')
                self.__check_value(k, v, "transitions", dict, 'list({v}.keys()) == [""]')
                self.__check_value_not_exists(k, v, "default_transitions")
            elif v["type"] == "classic":
                self.__check_value(k, v, "transitions", dict, 'len(list({v}.keys())) > 0')
                self.__check_value(k, v, "default_transitions", str, '{v}')
                self.__check_value_not_exists(k, v, "number_periods")
                self.__check_value_not_exists(k, v, "number_of_changes")

                if v["default_transitions"] not in list(v["transitions"].keys()):
                    raise GameTypesManagerError("13-005",f"In {k} the parametr 'default_transitions' ma nazwę której nie ma w 'transations'")

    @staticmethod
    def __check_value(name: str, parameters: dict, parameter_name: str, parameter_type: type, condition: str):
        if parameter_name not in parameters:
            raise GameTypesManagerError("13-002",f"In '{name}' there is no '{parameter_name}'")
        v = parameters[parameter_name]
        if not isinstance(parameters[parameter_name], parameter_type):
            raise GameTypesManagerError("13-003", f"In '{name}' the parameter '{parameter_name}' has the wrong type, it is '{type(v).__name__}' but should be '{parameter_type.__name__}'")
        c = condition.format(v=repr(v))
        if not eval(c):
            raise GameTypesManagerError("13-004", f"In '{name}' the parameter '{parameter_name}' does not satisfy the condition '{c}'")

    @staticmethod
    def __check_value_not_exists(name: str, parameters: dict, parameter_name: str):
        if parameter_name in parameters:
            raise GameTypesManagerError("13-006", f"In '{name}' is a parameter '{parameter_name}' it shoudn't be there")

    def __check_transitions(self, loaded_game_types: dict):
        for game_type_name, raw_game_type in loaded_game_types.items():
            lanes = raw_game_type["lanes"]
            transitions = {}
            number_team = 1 if raw_game_type["type"] == "classic" else 2 if raw_game_type["type"] == "league" else 0
            number_player_in_team: int | None = None
            for transition_name, transition in raw_game_type["transitions"].items():
                c = f"In '{game_type_name}' in '{transition_name}'"
                data = {}
                number_lane: int | None = None
                for round_transition in transition:
                    for lane, lane_transition in enumerate(round_transition):
                        if lane_transition == -1 and lanes[lane] == 1:
                            raise GameTypesManagerError("13-005",f"{c} jest instrukcja dotycząca nieużywanego toru numer {lane+1} w rundzie {round_transition+1}")
                        if lane_transition != -1 and lanes[lane] == 0:
                            raise GameTypesManagerError("13-005",f"{c} jest nie ma instrukcji dotyczącej używanego toru numer {lane + 1} w rundzie {round_transition + 1}")
                        if lane_transition == -1:
                            continue
                        if len(lane_transition) != 3:
                            raise GameTypesManagerError("13-005",f"{c} jest instrukcja, która nie ma 3 argumentów '{lane_transition}' na torze numer {lane + 1} w rundzie {round_transition + 1}")
                        if type(lane_transition[0]) != int or type(lane_transition[1]) != int or type(lane_transition[2]) != int:
                            raise GameTypesManagerError("13-005",f"{c} w instrukcji nie ma 3 intów '{lane_transition}' na torze numer {lane + 1} w rundzie {round_transition + 1}")
                        team, player, lane = lane_transition
                        if team not in data:
                            data[team] = {}
                        if player not in data[team]:
                            if lane == 0:
                                data[team][player] = 1
                            else:
                                raise GameTypesManagerError("13-005",f"{c} gracz nr {player} musi zaczynać torem 0, a nie {lane}")
                        else:
                            if data[team][player] == lane:
                                data[team][player] += 1
                            else:
                                raise GameTypesManagerError("13-005",f"{c} gracz nr {player} po torze {data[team][player]-1} ma {lane}")

                if number_team != len(list(data.keys())):
                    raise GameTypesManagerError("13-005", f"{c} jest '{len(list(data.keys()))}' drużyn a powinno być {number_team}")
                for team in data.values():
                    team__number_player = len(list(team.keys()))
                    if number_player_in_team is None:
                        number_player_in_team = team__number_player
                    elif number_player_in_team != team__number_player:
                        raise GameTypesManagerError("13-005", f"In '{game_type_name}' in '{transition_name}' jest '{team__number_player}' graczy, a w każdym schamacie musi być tyle samo graczy")
                    for player in team.values():
                        if number_lane is None:
                            number_lane = player
                        elif number_lane != player:
                            raise GameTypesManagerError("13-005", f"In '{game_type_name}' in '{transition_name}' każdy gracz musi grać tyle samo torów")

                transitions[transition_name] = Transition(transition_name, transition, number_lane)
            self.__game_types[game_type_name] = GameType(game_type_name, raw_game_type["type"], raw_game_type["lanes"],
                                                         raw_game_type.get("number_of_changes", None),
                                                         raw_game_type.get("number_periods", None), number_team,
                                                         number_player_in_team, transitions, raw_game_type.get("default_transitions", None))

class Transition:
    def __init__(self, name: str, schema: list[list[list[int, int, int] | int]], number_lane: int):
        self.name = name
        self.schema = schema
        self.number_lane = number_lane

class GameType:
    def __init__(self, name: str, game_type: Literal["classic", "league"], lanes: list[Literal[0, 1]],
                 number_of_changes: int | None, number_periods: int | None, number_team: int,
                 number_player_in_team: int, transitions: dict[str: Transition], default_transitions: str | None):
        self.name: str = name
        self.type: Literal["classic", "league"] = game_type
        self.lanes: list[Literal[0, 1]] = lanes
        self.number_of_changes: int = number_of_changes
        self.number_periods: int = number_periods
        self.number_team: int = number_team
        self.number_player_in_team: int = number_player_in_team
        self.transitions: dict[str: Transition] = transitions
        self.default_transitions: str = default_transitions

    def get_list_transitions_name(self) -> list[str]:
        return list(self.transitions.keys())


# try:
#     GameTypesManager()
# except GameTypesManagerError as e:
#     print(e.code, e.message)
