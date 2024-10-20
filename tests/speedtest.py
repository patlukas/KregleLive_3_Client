import time

t = "63|q|q|q|name_now|"

who = (1,2,3)
who_str = ("1","2","3")

def a1():
    name_split = t.replace("T", str(who[0])).replace("P", str(who[1])).replace("L", str(who[2])).split("|")
    if len(name_split) != 6:
        return

def a2():
    name_split = t.replace("T", who_str[0]).replace("P", who_str[1]).replace("L", who_str[2]).split("|")
    if len(name_split) != 6:
        return

def a3():
    name_split = t.split("|")
    if len(name_split) != 6:
        return
    if name_split[1] == "T":
        name_split[1] = who_str[0]
    if name_split[2] == "P":
        name_split[2] = who_str[1]
    if name_split[3] == "L":
        name_split[3] = who_str[2]

def b1():
    a = "33"
    b = "63"
    c = 4
    d = 0
    if (int(a) & c) != c:
        d += 1
    if int(b) & c != c:
        d += 1

def b2():
    a = "33"
    b = ""
    c = 4
    d = 0
    if a != "" and (int(a) & c) != c:
        d += 1
    if b != "" and int(b) & c != c:
        d += 1

def c1():
    d = {"a": 1, "b": 2}
    a = d.get("a", "")
    b = d.get("b", "")
    c = d.get("c", "")

def c2():
    d = {"a": 1, "b": 2}
    a = d.get("a")
    b = d.get("b")

def c3():
    d = {"a": 1, "b": 2}
    a = d["a"] if "a" in d else ""
    b = d["b"] if "b" in d else ""
    c = d["c"] if "c" in d else ""


def speedtest(loops, function, name):
    start = time.time()
    for _ in range(loops):
        function()
    end = time.time()
    print(name, end - start)

for i in range(3):
    # speedtest(1000000, a1, "a1")
    # speedtest(1000000, a2, "a2")
    # speedtest(1000000, a3, "a3")
    # speedtest(1000000, b1, "b1")
    speedtest(10000000, c1, "c1")
    speedtest(10000000, c2, "c3")
    speedtest(10000000, c3, "c3")

