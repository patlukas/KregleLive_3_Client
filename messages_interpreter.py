from typing import Callable


class MessagesInterpreter:
    """
        Logs:

    """
    def __init__(self, on_add_log: Callable[[int, str, str, str], None]):
        self.__on_add_log: Callable[[int, str, str, str], None] = on_add_log
        self.__messages = b""

    def add_messages(self, messages: bytes) -> None:
        self.__on_add_log(4, "INT_ADD_MSG", "", f"Add new message to interpreter: {messages}")
        self.__messages += messages

    def interpret_messages(self):
        while b"\r" in self.__messages:
            index_separator = self.__messages.index(b"\r")
            message = self.__messages[:index_separator]
            self.__messages = self.__messages[index_separator + 1:]
            self.__interpret_message(message)

    def __interpret_message(self, message: bytes):
        if len(message) < 6:
            self.__on_add_log(6, "INT_MINT_SHORT", "", f"Message is too short: {message}")
            return
        if not self.__checksum_checker(message):
            self.__on_add_log(6, "INT_MINT_CHECKSUM", "", f"Message has invalid checksum: {message}")
            return
        recipient, sender, content = message[:2], message[2:4], message[4:-2]
        recipient_int, recipient_name = self.__interpret_lane(recipient)
        sender_int, sender_name = self.__interpret_lane(sender)
        if recipient_int == -1 or sender_int == -1 or (recipient_int == 8 and sender_int == 8):
            self.__on_add_log(6, "INT_MINT_IROS", "", f"Message has invalid recipient or sender: {message}")
            return
        if recipient_int == 8 :
            self.__interpret_message_from_lane(sender_int, sender_name, content)
        else:
            self.__interpret_message_to_lane(recipient_int, recipient_name, content)

    def __interpret_message_from_lane(self, sender_int: int, sender_name: str, content: bytes) -> None:
        length = len(content)
        if length == 0:
            self.__on_add_log(9, "INT_LANE_UNKNOWN", "", f"Unknown message from {sender_name} with content: {content}")
            return
        x = content[0:1]
        if length == 28 and x in [b"w", b"g", b"h", b"k", b"f"]:
            self.__interpretation_of_lane_result(sender_int, content)
        elif length == 3 and ((b"0" <= x <= b"9") or (b"A" <= x <= b"F")):
            self.__set_lane_time(sender_int, content[0:3])
        elif length == 2:
            if x == b"i":
                status = 4 if content[1:2] == b"1" else 5
                self.__set_lane_status(sender_int, status)
            elif x == b"p":
                status = 1 if content[1:2] == b"1" else 2
                self.__set_lane_status(sender_int, status)
            else:
                self.__on_add_log(9, "INT_LANE_UNKNOWN", "", f"Unknown message from {sender_name} with content: {content}")
        elif length == 9 and x == "s":
            s = "on" if content[1:2] == b"1" else "off"
            self.__on_add_log(3, "INT_LANE_IGNORE", f"IS_{s.upper()}", f"Lane {sender_name} is {s}")
        else:
            self.__on_add_log(9, "INT_LANE_UNKNOWN", "", f"Unknown message from {sender_name} with content: {content}")

    def __interpret_message_to_lane(self, recipient_int: int, recipient_str: str, content: bytes) -> None:
        length = len(content)
        if length == 0:
            self.__on_add_log(3, "INT_TOLANE_IGNORE", "HEARTBEAT", f"In lane {recipient_str} heartbeat sent")
            return
        x = content[0:1]
        if length == 1:
            if x == b"S":
                self.__on_add_log(3, "INT_TOLANE_IGNORE", "IS_ON?", f"In lane {recipient_str} was a question whether is on or off")
            else:
                self.__on_add_log(9, "INT_TOLANE_UNKNOWN", "", f"Unknown message to {recipient_str} with content: {content}")
            return
        y = content[1:2]
        if length == 21 and x == b"I" and y == b"G":
            self.__set_lane_status(recipient_int, 3)
            self.__interpretation_of_game_run(recipient_int, content[2:])
        elif length == 8 and x == b"P":
            self.__set_lane_status(recipient_int, 0)
            self.__interpretation_of_trail_run(recipient_int, content[1:])
        elif length == 2 and x == b"E":
            s = "enable" if y == b"1" else "disable"
            self.__on_add_log(3, "INT_TOLANE_IGNORE", s.upper(), f"In lane {recipient_str} communications {s}")
        elif x == b"M":
            if y == b"S":
                self.__on_add_log(3, "INT_TOLANE_IGNORE", "PRINT_SURNAME", f"In lane {recipient_str} was set data to print: name={content}")
            elif y == b"D":
                self.__on_add_log(3, "INT_TOLANE_IGNORE", "PRINT_DATE", f"In lane {recipient_str} was set data to print: date={content}")
            else:
                self.__on_add_log(9, "INT_TOLANE_UNKNOWN", "", f"Unknown message to {recipient_str} with content: {content}")
        else:
            self.__on_add_log(9, "INT_TOLANE_UNKNOWN", "", f"Unknown message to {recipient_str} with content: {content}")

    def __set_lane_status(self, lane: int, status: int):
        pass

    def __set_lane_time(self, lane: int, time_bytes: bytes):
        pass

    def __interpretation_of_trail_run(self, lane: int, trial_setup: bytes):
        pass

    def __interpretation_of_game_run(self, lane: int, game_setup: bytes):
        pass

    def __interpretation_of_lane_result(self, lane: int, result: bytes):
        pass

    @staticmethod
    def __interpret_lane(lane: bytes) -> (int, str):
        """

        :param lane:
        :return:
        """
        interpreter = {b"30": [0, "1"], b"31": [1, "2"], b"32": [2, "3"], b"33": [3, "4"], b"34": [4, "5"], b"35": [5, "6"], b"38": [8, "Server"]}
        if lane in interpreter:
            return interpreter[lane]
        return -1, ""

    @staticmethod
    def __checksum_checker(message: bytes) -> bool:
        """

        :param message:
        :return:
        """
        message_head, message_tail = message[:-2], message[-2:]
        sum_ascii = 0
        for x in message_head:
            sum_ascii += x
        checksum = bytes(hex(sum_ascii).split("x")[-1].upper()[-2:], 'utf-8')
        if message_tail == checksum:
            return True
        return False
