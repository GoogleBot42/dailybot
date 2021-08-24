import re

class Module:
    def __init__(self):
        self.commands = ["karma"]
        self.auto = True
        self.manual = {
            "desc": "Count a user's karma.",
            "bot_commands": {
                "karma": lambda x: f"{x}karma",
                "info": "Show your total amount of karma."
            }
        }

def set_karma(dbc, nickname, points):
    dbc.execute("CREATE TABLE IF NOT EXISTS karma "
                "(nickname TEXT COLLATE NOCASE, points INTEGER);")
    dbc.execute("INSERT OR IGNORE INTO karma VALUES (?, ?);",
                (nickname, points))
    dbc.execute("UPDATE karma SET points=? WHERE nickname=?;",
                (points, nickname))

def get_karma(dbc, nickname):
    try:
        dbc.execute("SELECT points FROM karma WHERE nickname=?;",
                    (nickname,))
        return dbc.fetchone()[0]
    except Exception:
        return 0

def main(i, irc):
    dbc = i.db[1].cursor()

    if i.cmd == "karma":
        k = get_karma(dbc, i.nickname)
        irc.privmsg(i.channel, f"Karma for {i.nickname}: {k}")

    if i.channel == i.nickname:
        return

    if re.match("^[a-z_\\-\\[\\]\\\\^{}|`][a-z0-9_\\-\\[\\]\\\\^{}|`]*\\+\\+$", i.msg):
        set_karma(dbc, i.nickname, get_karma(dbc, i.nickname) + 1)
    elif re.match("^[a-z_\\-\\[\\]\\\\^{}|`][a-z0-9_\\-\\[\\]\\\\^{}|`]*\\-\\-$", i.msg):
        set_karma(dbc, i.nickname, get_karma(dbc, i.nickname) - 1)