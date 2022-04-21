# coding=utf-8

# Point (karma) counting module for Drastikbot
#
# Give points/karma to users for performing certain actions

'''
Copyright (C) 2019 drastik.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


class Module:
    def __init__(self):
        self.commands = ["points"]
        self.auto = True
        self.manual = {
            "desc": "Count a user's GNU/Linux points.",
            "bot_commands": {
                "points": lambda x: f"{x}points",
                "info": "Show your total amount of points."
            }
        }


def set_gnu_linux_points(dbc, nickname, points):
    dbc.execute("CREATE TABLE IF NOT EXISTS points_gnu_linux "
                "(nickname TEXT COLLATE NOCASE, points INTEGER);")
    dbc.execute("INSERT OR IGNORE INTO points_gnu_linux VALUES (?, ?);",
                (nickname, points))
    dbc.execute("UPDATE points_gnu_linux SET points=? WHERE nickname=?;",
                (points, nickname))


def get_gnu_linux_points(dbc, nickname):
    try:
        dbc.execute("SELECT points FROM points_gnu_linux WHERE nickname=?;",
                    (nickname,))
        return dbc.fetchone()[0]
    except Exception:
        return 0


def gnu_linux_points_handler(dbc, nickname, mode=""):
    try:
        p = get_gnu_linux_points(dbc, nickname)
    except Exception:
        p = 0
    if "gnu" == mode:
        p += 1
    elif "linux" == mode:
        p -= 1
    set_gnu_linux_points(dbc, nickname, p)


def main(i, irc):
    dbc = i.db[0].cursor()

    if i.cmd == "points":
        gl_p = get_gnu_linux_points(dbc, i.nickname)
        irc.privmsg(i.channel, f"GNU/Linux Points for {i.nickname}: {gl_p}")

    if i.channel == i.nickname:
        return

    last_nick = i.varget("last_nick", defval=irc.var.nickname)
    if last_nick == i.nickname:
        return
    else:
        i.varset("last_nick", i.nickname)

    if "gnu/linux" in i.msg.lower() or "gnu+linux" in i.msg.lower():
        gnu_linux_points_handler(dbc, i.nickname, mode="gnu")
    elif "linux" in i.msg.lower() and "linux kernel" not in i.msg.lower():
        gnu_linux_points_handler(dbc, i.nickname, mode="linux")
