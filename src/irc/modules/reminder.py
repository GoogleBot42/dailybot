#!/usr/bin/env python3
# coding=utf-8

# Reminder Module for Drastikbot
#
# Ask the bot to remind you of something after some time.
# .in 35m check laundry | .in <DURATION> <MESSAGE>
#
# The duration works like the unix sleep command: one or more numbers with
# an optional s, m, h or d suffix that are added together, e.g. "90",
# "1.5h" or "1h 30m". Reminders are saved in the bot's database, so they
# survive restarts. Reminders that became due while the bot was offline are
# sent as soon as it is back.

'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import datetime
import re
import threading
import time
import traceback


class Module:
    def __init__(self):
        self.commands = ['in']
        self.auto = True
        self.startup = True
        # JOIN is used to get the new irc object after a reconnection.
        self.msgtypes = ['PRIVMSG', 'JOIN']
        self.manual = {
            "desc": (
                "Set a reminder. The bot will mention you with your message"
                " in the same channel after the given time."
            ),
            "bot_commands": {
                "in": {
                    "usage": lambda x: f"{x}in <duration> <message>",
                    "info": ("The duration is one or more numbers with an"
                             " optional s, m, h or d suffix, like the unix"
                             " sleep command. Example: .in 1h 30m check"
                             " laundry")
                }
            }
        }


# ----- Constants ----- #
units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
unit_words = {
    "sec": "s", "secs": "s", "second": "s", "seconds": "s",
    "min": "m", "mins": "m", "minute": "m", "minutes": "m",
    "hr": "h", "hrs": "h", "hour": "h", "hours": "h",
    "day": "d", "days": "d"
}
max_duration = 365 * 86400
max_reminders = 25  # Pending reminders per nickname
poll_interval = 1  # Seconds between checks for due reminders
# --------------------- #


def parse_duration(args):
    '''
    Parse a duration from the start of 'args' (a list of words).
    Returns (seconds, remaining words). 'seconds' is 0 if 'args' does not
    start with a duration.
    '''
    number = r'(\d+(?:\.\d*)?|\.\d+)'
    total = 0
    idx = 0
    while idx < len(args):
        word = args[idx].lower()
        parts = re.findall(number + r'([a-z]*)', word)
        if not parts or ''.join(n + u for n, u in parts) != word:
            break
        # Allow a unit as a separate word: ".in 5 minutes ..."
        if len(parts) == 1 and not parts[0][1] and idx + 1 < len(args) \
           and args[idx + 1].lower() in unit_words:
            idx += 1
            parts = [(parts[0][0], args[idx].lower())]
        seconds = 0
        for n, u in parts:
            u = unit_words.get(u, u) or "s"
            if u not in units:
                return total, args[idx:]
            seconds += float(n) * units[u]
        total += seconds
        idx += 1
    return total, args[idx:]


def format_duration(seconds):
    seconds = int(round(seconds))
    out = []
    for name, size in (("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        n, seconds = divmod(seconds, size)
        if n:
            out.append(f"{n}{name}")
    return " ".join(out) or "0s"


def db_init(dbc):
    dbc.execute("CREATE TABLE IF NOT EXISTS reminder "
                "(id INTEGER PRIMARY KEY, nickname TEXT COLLATE NOCASE, "
                "channel TEXT, msg TEXT, created INTEGER, due INTEGER);")


def add(nickname, channel, msg, seconds, db):
    dbc = db.cursor()
    db_init(dbc)
    dbc.execute("SELECT COUNT(*) FROM reminder WHERE nickname=?;",
                (nickname,))
    if dbc.fetchone()[0] >= max_reminders:
        return False
    now = int(time.time())
    dbc.execute("INSERT INTO reminder (nickname, channel, msg, created, due) "
                "VALUES (?, ?, ?, ?, ?);",
                (nickname, channel, msg, now, now + int(round(seconds))))
    db.commit()
    return True


def send_due(irc, db):
    dbc = db.cursor()
    db_init(dbc)
    now = int(time.time())
    dbc.execute("SELECT id, nickname, channel, msg, created FROM reminder "
                "WHERE due <= ? ORDER BY due;", (now,))
    for rid, nickname, channel, msg, created in dbc.fetchall():
        # Delete before sending, so a failed delete can't send it twice.
        dbc.execute("DELETE FROM reminder WHERE id=?;", (rid,))
        db.commit()
        ago = format_duration(now - created)
        irc.privmsg(channel, f"{nickname}: Reminder: {msg} (set {ago} ago)")


def reminder_loop(varget, db):
    '''
    Send reminders when they become due. This runs in its own thread for as
    long as the bot is running.
    '''
    while True:
        time.sleep(poll_interval)
        try:
            # The irc object is replaced when the bot reconnects, so always
            # use the most recent one.
            irc = varget("irc")
            if irc.var.sigint:
                return
            if irc.var.conn_state != 2:
                continue  # Not connected, keep the reminders for later.
            send_due(irc, db)
        except Exception:
            print(f"reminder.py: {traceback.format_exc()}")


def main(i, irc):
    i.varset("irc", irc)
    if i.msgtype == "STARTUP":
        t = threading.Thread(target=reminder_loop, args=(i.varget, i.db[1]),
                             daemon=True)
        t.start()
        return
    if i.cmd != "in":
        return

    usage = f"Usage: {i.cmd_prefix}in <duration> <message> (e.g. 35m, 1h 30m)"
    seconds, msg = parse_duration(i.msg_nocmd.split())
    msg = " ".join(msg)
    if not seconds or not msg:
        return irc.privmsg(i.channel, usage)
    if seconds > max_duration:
        return irc.privmsg(i.channel, f"{i.nickname}: That is too far away. "
                           f"The maximum is {format_duration(max_duration)}.")

    if not add(i.nickname, i.channel, msg, seconds, i.db[1]):
        return irc.privmsg(i.channel,
                           f"{i.nickname}: You already have {max_reminders} "
                           "reminders pending.")
    due = datetime.datetime.now(datetime.timezone.utc) \
        + datetime.timedelta(seconds=seconds)
    irc.privmsg(i.channel,
                f"{i.nickname}: I will remind you in "
                f"{format_duration(seconds)} "
                f"({due.strftime('%Y-%m-%d %H:%M:%S')} UTC).")
