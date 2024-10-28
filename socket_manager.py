import time
from socket import socket
import socket
from typing import Callable


class SocketManager:
    """
        Logs:
            SKT_RECV_ERROR - 10 - Unexpected error while receiving data
            SKT_RCV_LSRVR - 10 - Lost connection to server, probably the server disconnected (Lost SeRVeR)
            SKT_RCNCT_WTYPE - 9 - Wrong data type when trying to reconnect (Wrong TYPE)
            SKT_RCNCT_WADDR - 9 - Wrong IP address when trying to reconnect (Wrong ADDRess)
            SKT_RCNCT_WPORT - 9 - Wrong IP address when trying to reconnect (Wrong PORT)
            SKT_INIT_EXIST - 7 - Connection already existed (connection EXISTs)
            SKT_INIT_WTYPE - 7 - Wrong data type (Wrong TYPE)
            SKT_INIT_ECRTE - 7 - Error creating socket (Error CReaTE socket)
            SKT_RCNCT_EXIST - 7 - Connection already existed when trying to reconnect (connection EXISTs)
            SKT_RCNCT_NSADDR - 7 - Server address and port are not set when trying to reconnect (Not Set ADDRess and port)
            SKT_RCNCT_ECRTE - 7 - Error creating socket when trying to reconnect (Error CReaTE socket)
            SKT_DSCNT_NCNCT - 7 - There was no connection to the server (Not CoNeCTed)
            SKT_RECV_NCNCT - 7 - There is no connection to the server (Not CoNeCTed)
            SKT_RCNCT_OK - 6 - Reconnection successfully was created
            SKT_INIT_OK - 5 - Connection successfully was created
            SKT_INIT_TOUT - 5 - Timeout while trying to connect (TimeOUT)
            SKT_INIT_WADDR - 5 - Wrong IP address (Wrong ADDRess)
            SKT_INIT_WPORT - 5 - Wrong IP address (Wrong PORT)
            SKT_RCNCT_TOUT - 5 - Timeout while trying to connect when trying to reconnect (TimeOUT)
            SKT_DSCNT_OK - 5 - Successfully disconnected from server
            SKT_RECV_OK - 4 - Data received
            SKT_CNCT_START - 2 - Connection attempt started
            SKT_RECV_EMPTY - 1 - Nothing was received

    """
    def __init__(self, socket_timeout: float, on_add_log: Callable[[int,str,str,str], None]):
        """
        :param socket_timeout: <float> number of seconds waiting for recv data and connection
        :param on_add_log: <Callable[[int,str,str,str], None]> function to add logs

        self.__socket_timeout - same like :param socket_timeout:
        self._on_add_log - same like :param on_add_log:
        self.__ip_address - <str> server ip address or "" if not set
        self.__port - <int> server port number or -1 if not set
        self.__socket - <None | socket.socket> an instance of the socket object, or None if there is no connection
        """
        self.__socket_timeout: float = socket_timeout
        self.__on_add_log: Callable[[int,str,str,str], None] = on_add_log
        self.__ip_address: str = ""
        self.__port: int = -1
        self.__socket: None | socket.socket = None
        self.__time_last_msg: float = 0

    def connect(self, ip_address: str, port: int) -> tuple[int, str]:
        """
        The function is used to establish the first connection to the server

        :param ip_address: <str> server ip address
        :param port: <int> server port number
        :return: <int, str> int - code (look below), str - message
                            -6 - Connection already existed
                            -5 - Error creating socket
                            -4 - Wrong port number
                            -3 - Wrong IP address
                            -2 - Wrong data type
                            -1 - Timeout while trying to connect
                            1 - Connection successfully was created
        :logs: SKT_INIT_EXIST (7), SKT_INIT_WTYPE (7), SKT_INIT_ECRTE (7), SKT_INIT_OK (5), SKT_INIT_TOUT (5),
                    SKT_INIT_WADDR (5), SKT_INIT_WPORT (5)
        """
        if self.__socket is not None:
            self.__on_add_log(7, "SKT_INIT_EXIST", "", "Połączenie jest nawiązane, więc nie można nawiązać nowego")
            return -6, "Połączenie jest już nawiązane"
        if not isinstance(port, int):
            try:
                port = int(port)
            except ValueError:
                return -2, "Niepoprawny typ danych"
        self.__ip_address, self.__port = ip_address, port
        result_connect = self.__connect()
        if result_connect == 1:
            self.__on_add_log(5, "SKT_INIT_OK", "", f"Nawiązano połączenie z IP: {ip_address}, port: {port}")
            return 1, ""
        self.__ip_address, self.__port = "", -1
        match result_connect:
            case -1:
                self.__on_add_log(5, "SKT_INIT_TOUT", "", "Nie udało się połączyć z powodu timeoutut.")
                return -1, "Nie udało się nawiązać połączenia."
            case -2:
                self.__on_add_log(7, "SKT_INIT_WTYPE", "", f"Błędny typ danych ip ({ip_address}) ma być str jest {type(ip_address)}, port ({port}) ma być int jest {type(port)}")
                return -2, "Niepoprawny typ danych"
            case -3:
                self.__on_add_log(5, "SKT_INIT_WADDR", "", f"Błędny adres IP ({ip_address})")
                return -3, "Niepoprawny adres IP"
            case -4:
                self.__on_add_log(5, "SKT_INIT_WPORT", "", f"Błędny numer portu, musi być z zakresu 0-65535, a jest {port}")
                return -4, "Niepoprawny numer portu"
            case -5:
                self.__on_add_log(7, "SKT_INIT_ECRTE", "", f"Błąd podczas tworzenia soketa")
                return -5, "Błąd podczas tworzenia soketa"

    def reconnect(self) -> int:
        """
        This function is used to reconnect to the server.

        :return: <int>
                    -7 - Connection already existed
                    -6 - Server address and port are not set
                    -5 - Error creating socket
                    -4 - Wrong port number
                    -3 - Wrong IP address
                    -2 - Wrong data type
                    -1 - Timeout while trying to connect
                    1 - Reconnection was successfully created
        :logs: SKT_RCNCT_WTYPE (9), SKT_RCNCT_WADDR (9), SKT_RCNCT_WPORT (9), SKT_RCNCT_EXIST (7), SKT_RCNCT_NSADDR (7),
                SKT_RCNCT_ECRTE (7), SKT_RCNCT_OK (6), SKT_RCNCT_TOUT (5)
        """
        if self.__socket is not None:
            self.__on_add_log(7, "SKT_RCNCT_EXIST", "", "Połączenie jest nawiązane, więc nie można nawiązać nowego")
            return -7
        if self.__port == -1 or self.__ip_address == "":
            self.__on_add_log(7, "SKT_RCNCT_NSADDR", "", "Nie ma ustawionego adresu serwer, więc nie można się połączyć")
            return -6
        result_connect = self.__connect()
        if result_connect in [-2, -3, -4]:
            self.__ip_address, self.__port = "", -1
        match result_connect:
            case 1:
                self.__on_add_log(6, "SKT_RCNCT_OK", "", "Ponownie połączono się z serwerem")
            case -1:
                self.__on_add_log(5, "SKT_RCNCT_TOUT", "", "Nie udało się połączyć z powodu timeoutut.")
            case -2:
                self.__on_add_log(9, "SKT_RCNCT_WTYPE", "", f"Błędny typ danych ip ({self.__ip_address}) ma być str jest {type(self.__ip_address)}, port ({self.__port}) ma być int jest {type(self.__port)}")
            case -3:
                self.__on_add_log(9, "SKT_RCNCT_WADDR", "", f"Błędny adres IP ({self.__ip_address})")
            case -4:
                self.__on_add_log(9, "SKT_RCNCT_WPORT", "", f"Błędny numer portu, musi być z zakresu 0-65535, a jest {self.__port}")
            case -5:
                self.__on_add_log(7, "SKT_RCNCT_ECRTE", "", f"Błąd podczas tworzenia soketa")
        return result_connect

    def __connect(self) -> int:
        """
        The function is used to establish a tcp connection to the server

        :return: <int>
                    -5 - Problem while create socket
                    -4 - Wrong port number
                    -3 - Invalid ip address
                    -2 - Invalid data type
                    -1 - Timeout while trying to connect
                    1 - New connection successful
        :logs: SKT_CNCT_START (2)
        """
        self.__on_add_log(2, "SKT_CNCT_START", "", f"Próba stworzenia soketu")
        try:
            socket_el = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_el.settimeout(self.__socket_timeout)
            socket_el.connect((self.__ip_address, self.__port))
        except TimeoutError:
            return -1
        except TypeError:
            return -2
        except socket.gaierror:
            return -3
        except OverflowError:
            return -4
        except OSError as e:
            return -5
        self.__socket = socket_el
        return 1

    def disconnect(self) -> bool:
        """
        This function is used to disconnect a connection.

        :return: <bool> True - successfully disconnected, False - there was no connection
        :logs:  SKT_DSCNT_NCNCT (7), SKT_DSCNT_OK (5)
        """
        if self.__socket is None and self.__ip_address == "" and self.__port == -1:
            self.__on_add_log(7, "SKT_DSCNT_NCNCT", "", "Nie istniało połączenie, więc nie rozłączono")
            return False
        else:
            self.__on_add_log(5, "SKT_DSCNT_OK", "", f"Rozłączono się z IP: {self.__ip_address} port: {self.__port}")
            if self.__socket is not None:
                self.__socket.close()
                self.__socket = None
            self.__ip_address = ""
            self.__port = -1
            return True

    def get_connection_status(self) -> int:
        """
        This method returns information whether the connection is active or not, or whether the server address is set

        :return: <int>
                1 - is connection
                0 - is set address and port, but not connected
                -1 - is not set address and port and is not connection
        """
        if self.__socket is not None:
            return 1
        if self.__port != -1 and self.__ip_address != "":
            return 0
        return -1

    def recv(self) -> tuple[int, bytes]:
        """
        This method is used to receive data from the server

        :return: <int, bytes> int - code (look below), bytes - message
                            1 - data received
                            0 - nothing was received
                            -1 - lost connection to server
                            -2 - unexpected error while receiving data
                            -3 - there is no connection to the server
        :logs: SKT_RECV_ERROR (10), SKT_RCV_LSRVR (10), SKT_RECV_NCNCT (7), SKT_RECV_OK (4), SKT_RECV_EMPTY (1)
        """
        self.__time_last_msg = time.time()
        if self.__socket is None:
            self.__on_add_log(7, "SKT_RECV_NCNCT", "", f"Nie można odebrać danych bo nie ma połaczenia")
            return -3, b""
        try:
            msg = self.__socket.recv(1024)
        except socket.timeout:
            self.__on_add_log(1, "SKT_RECV_EMPTY", "", f"Nic nie odebrano")
            return 0, b""
        except socket.error as e:
            self.__on_add_log(10, "SKT_RCV_ERROR", "", f"Nieoczekiwany błąd podczas odbierania | {e}")
            self.__socket = None
            return -2, b""
        if len(msg) == 0:
            self.__on_add_log(10, "SKT_RCV_LSRVR", "", f"Utracono połączenie z serwerem!")
            self.__socket = None
            return -1, b""
        self.__on_add_log(4, "SKT_RCV_OK", "", f"{msg}")
        return 1, msg

    def ping(self, interval: float) -> bool:
        """
            TODO: Add comment
        """
        if self.__socket is None:
            self.__on_add_log(7, "SKT_PING_NCNCT", "", f"Nie można odebrać danych bo nie ma połaczenia")
            return False
        if self.__time_last_msg + interval > time.time():
            return True
        self.__time_last_msg = time.time()
        try:
            msg = self.__socket.send(b"\r")
        except socket.error as e:
            self.__on_add_log(10, "SKT_PING_ERROR", "", f"Nieoczekiwany błąd podczas odbierania | {e}")
            self.__socket = None
            return False
        self.__on_add_log(0, "SKT_PING_OK", "", f"{msg}")
        return True
