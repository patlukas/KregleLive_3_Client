import socket
from socket_manager import SocketManager
import threading


def test_connect():
    x = SocketManager(0.2, lambda a, b, c, d: print(a, b, c, d))
    x = SocketManager(0.2, lambda a, b, c, d: print(a, b, c))

    assert x.connect("", 10)[0] == -5
    assert x.connect("100.1.1.1", 10)[0] == -5


    assert x.connect("101.0.0.1", -1)[0] == -4
    assert x.connect("101.0.0.1", 65536)[0] == -4

    assert x.connect("1011.0.0.1", 10)[0] == -3
    assert x.connect("localhostt", 10)[0] == -3

    assert x.connect(1, 10)[0] == -2
    assert x.connect("101.0.0.1", lambda a: a)[0] == -2
    assert x.connect("101.0.0.1", "1")[0] == -2

    assert x.connect("localhost", 10)[0] == -1

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 3000))
    server.listen(5)
    server.settimeout(1)

    assert x.connect("localhost", 3001)[0] == -1
    assert x.connect("localhost", 3000)[0] == 1
    assert x.connect("localhost", 3001)[0] == -6
    assert x.connect("localhost", 3000)[0] == -6

def test_disconnect():
    x = SocketManager(0.2, lambda a, b, c, d: print(a, b, c, d))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 3000))
    server.listen(5)
    server.settimeout(1)

    assert x.disconnect() == False

    assert x.connect("localhost", 3001)[0] == -1
    assert x.disconnect() == False

    assert x.connect(1, 3001)[0] == -2
    assert x.disconnect() == False

    assert x.connect("localhostt", 3001)[0] == -3
    assert x.disconnect() == False

    assert x.connect("localhost", -1)[0] == -4
    assert x.disconnect() == False

    assert x.connect("localhost", 3000)[0] == 1
    assert x.connect("localhost", 3000)[0] == -6
    assert x.disconnect() == True
    assert x.disconnect() == False

    assert x.connect("localhost", 3000)[0] == 1
    assert x.connect("localhost", 3000)[0] == -6
    assert x.disconnect() == True
    assert x.disconnect() == False

def test_get_connection_status():
    x = SocketManager(0.2, lambda a, b, c, d: print(a, b, c, d))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 3000))
    server.listen(5)
    server.settimeout(1)

    assert x.get_connection_status() == -1

    x.connect("localhost", -1)
    assert x.get_connection_status() == -1

    x.connect("localhost", 3000)
    assert x.get_connection_status() == 1
    assert x.get_connection_status() == 1

    conn, _ = server.accept()
    assert x.get_connection_status() == 1

    conn.close()
    assert x.get_connection_status() == 1

    x.recv()
    assert x.get_connection_status() == 0

    x.disconnect()
    assert x.get_connection_status() == -1

    x.connect("localhost", 3000)
    conn, _ = server.accept()
    assert x.get_connection_status() == 1

    conn.close()
    assert x.get_connection_status() == 1

    x.disconnect()
    assert x.get_connection_status() == -1

    x.connect("localhost", 3000)
    conn, _ = server.accept()
    assert x.get_connection_status() == 1

    conn.close()
    assert x.get_connection_status() == 1

    x.recv()
    assert x.get_connection_status() == 0

    x.reconnect()
    assert x.get_connection_status() == 1

def test_reconnect():
    x = SocketManager(0.2, lambda a, b, c, d: print(a, b, c, d))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 3000))
    server.listen(5)
    server.settimeout(1)

    assert x.reconnect() == -6

    x.connect("localhost", 3000)
    assert x.reconnect() == -7

    x.recv()
    assert x.reconnect() == -7

    conn, _ = server.accept()
    conn.close()
    x.recv()
    assert x.reconnect() == 1

    x.connect("localhost", 3000)
    conn, _ = server.accept()
    x.disconnect()
    assert x.reconnect() == -6

def c():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 12345))
    server.listen(5)
    server.settimeout(1)
    conn, address = server.accept()
    conn.send(b"Hej\r")
    server.close()

def test_recv():
    x = SocketManager(0.1, lambda a, b, c, d: print(a, b, c, d))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 3000))
    server.listen(5)
    server.settimeout(1)

    assert x.recv()[0] == -3

    x.connect("localhost", 3000)
    assert x.recv()[0] == 0
    x.disconnect()
    assert x.recv()[0] == -3

    d = threading.Thread(target=c)
    d.start()
    assert x.connect("localhost", 12345)[0] == 1
    assert x.recv() == (1, b"Hej\r")
    assert x.recv()[0] == -1

    d = threading.Thread(target=c)
    d.start()
    assert x.connect("localhost", 12345)[0] == 1
    assert x.recv() == (1, b"Hej\r")
    assert x.disconnect() == True
    assert x.recv()[0] == -3

