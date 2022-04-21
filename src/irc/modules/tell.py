#!/usr/bin/env python3
# coding=utf-8

# Tell Module for Drastikbot
#
# It works "like" memoserv.
# A user tells the bot to tell a message to a nick when that nick is seen.
# .tell drastik drastikbot is down | .tell <NICKNAME> <MESSAGE>

'''
Copyright (C) 2017 drastik.org

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
from ignore import is_ignored


class Module:
    def __init__(self):
        self.commands = ['tell']
        self.auto = True
        self.manual = {
            "desc": (
                "Send a message to a user through the bot. This is used to"
                " send messages to users that are AFK or not connected to "
                "the server. The bot will message the receiver as soon as "
                "they post to a channel that the bot has joined."
            ),
            "bot_commands": {
                "tell": {"usage": lambda x: f"{x}tell <receiver> <message>"}
            }
        }


def add(receiver, msg, sender, dbc):
    timestamp = datetime.datetime.utcnow().replace(microsecond=0)
    dbc.execute("CREATE TABLE IF NOT EXISTS tell "
                "(receiver TEXT COLLATE NOCASE, msg TEXT, sender TEXT, "
                "timestamp TEXT, date INTEGER);")
    dbc.execute("INSERT INTO tell VALUES (?, ?, ?, ?, strftime('%s', 'now'));",
                # These are wrong but handled correctly. Fix it someday.
                (receiver, msg, str(timestamp), sender))


def find(nick, irc, dbc):
    try:
        dbc.execute('SELECT sender, msg, timestamp FROM tell '
                    'WHERE receiver=?;', (nick,))
        fetch = dbc.fetchall()
        for i in fetch:
            irc.privmsg(nick, f'\x0302{i[2]} [{i[0]} UTC]:\x0F')
            irc.privmsg(nick, i[1])
        dbc.execute('''DELETE FROM tell WHERE receiver=?;''', (nick,))
        # Delete messages older than 3600 * 24 * 30 * 3 seconds.
        dbc.execute('''DELETE FROM tell WHERE
                    (strftime('%s', 'now') - date) > (3600 * 24 * 30 * 3);''')
    except Exception:
        # Nothing in the db yet, ignore errors.
        pass


def main(i, irc):
    dbc = i.db[1].cursor()
    if 'tell' == i.cmd:
        try:
            arg_list = i.msg_nocmd.split(' ', 1)
            receiver = arg_list[0]
            msg = arg_list[1]
        except IndexError:
            help_msg = f"Usage: {i.cmd_prefix}{i.cmd} <Receiver> <Message>"
            return irc.privmsg(i.channel, help_msg)
        if i.nickname.lower() == receiver.lower():
            return irc.privmsg(i.channel, 'You can tell yourself that.')
        if irc.var.curr_nickname.lower() == receiver.lower():
            return irc.privmsg(i.channel,
                               f'{i.nickname}: I am here now, tell me.')
        if is_ignored(i, irc, receiver, i.nickname):
            return  # say nothing
        add(receiver, msg, i.nickname, dbc)
        irc.privmsg(i.channel,
                    f'{i.nickname}: I will tell {receiver} '
                    'when they are around.')

    find(i.nickname, irc, dbc)
    i.db[1].commit()
