#!/usr/bin/env python3
# coding=utf-8

# Seen Module for Drastikbot
#
# It logs the last activity of every user posting and returns it upon request.
# It logs time, post, nickname, channel.
#
# user = The one used the bot (or posted a random line)
# nick = The nickname requested by the user

'''
Seen module for drastikbot.
Copyright (C) 2018, 2021 drastik.org

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


class Module:
    def __init__(self):
        self.auto = True
        self.commands = ["seen"]
        self.manual = {
            "desc": ("See when a user was last seen posting in a channel the"
                     " bot has joined. If the user posted in channel other"
                     " than the one the command was given from, then the bot"
                     " will show that channel. Private messages with the bot"
                     " are NOT saved."),
            "bot_commands": {
                "seen": {"usage": lambda x: f"{x}seen <nickname>"},
                "info": ("Example: <Alice>: .seen Bob / <Bot>:"
                         " Bob was last seen 0:21:09 ago"
                         " [2018-06-25 13:36:42 UTC], saying .help seen")
            }
        }


def update(channel, nick, msg, time, dbc):
    try:
        dbc.execute(
            '''CREATE TABLE IF NOT EXISTS seen (nick TEXT COLLATE NOCASE
            PRIMARY KEY, msg TEXT, time TEXT, channel TEXT);''')
    except Exception:
        # sqlite3.OperationalError: cannot commit - no transaction is active
        pass
    dbc.execute(
        '''INSERT OR IGNORE INTO seen (nick, msg, time, channel)
        VALUES (?, ?, ?, ?);''', (nick, msg, str(time), channel))
    dbc.execute('''UPDATE seen SET msg=?, time=?, channel=? WHERE nick=?;''',
                (msg, str(time), channel, nick))


def fetch(nick, dbc):
    try:
        dbc.execute('SELECT nick, msg, time, channel '
                    'FROM seen WHERE nick=?;''', (nick,))
        fetch = dbc.fetchone()
        nickFnd = fetch[0]
        msgFnd = fetch[1]
        timeFnd = datetime.datetime.strptime(fetch[2], "%Y-%m-%d %H:%M:%S")
        channelFnd = fetch[3]
        return (msgFnd, timeFnd, channelFnd, nickFnd)
    except Exception:
        return False


def main(i, irc):
    dbc = i.db[1].cursor()
    timestamp = datetime.datetime.utcnow().replace(microsecond=0)
    args = i.msg_nocmd.split()

    if not i.cmd and not i.channel == i.nickname:
        # Avoid saving privmsges with the bot.
        update(i.channel, i.nickname, i.msg, timestamp, dbc)
        i.db[1].commit()
        return

    if i.cmd == 'seen' and ((len(args) == 1 and len(i.msg) <= 30)
                            or i.msg_nocmd == ''):

        if not i.msg_nocmd:
            # If no nickname is given set the args[0] to the user's nickname
            args = [i.nickname]

        get = fetch(args[0], dbc)
        if get:
            ago = timestamp - get[1]
            if '\x01ACTION' in get[0][:10]:
                toSend = (f'\x0312{get[3]}\x0F was last seen '
                          f'\x0312{ago} ago\x0F [{get[1]} UTC], '
                          f'doing \x0312{i.msg_nocmd} {get[0][8:]}\x0F')
            else:
                toSend = (f'\x0312{get[3]}\x0F was last seen '
                          f'\x0312{ago} ago\x0F [{get[1]} UTC], '
                          f'saying \x0312{get[0]}\x0F')
            if args[0].lower() == i.nickname.lower():
                # Check if the requested nickname is the user's nickname
                toSend = (f'\x0312You\x0F were last seen \x0312{ago} ago\x0F'
                          f' [{get[1]} UTC], saying \x0312{get[0]}\x0F')
        else:
            toSend = f"Sorry, I haven't seen \x0312{args[0]}\x0F around"
        if args[0] == irc.var.nickname:
            # Check if the requested nickname is the bot's nickname
            toSend = "\x0304Who?\x0F"
            self_nick = True
        else:
            self_nick = False
        try:
            # If 'get' check the channel the user was last seen and send a
            # privmsg
            if get[2] == i.channel or self_nick:
                irc.privmsg(i.channel, toSend)
            else:
                toSend = f'{toSend} in \x0312{get[2]}\x0F'
                irc.privmsg(i.channel, toSend)
        except TypeError:
            # if not 'get' just send a privmsg
            irc.privmsg(i.channel, toSend)
    # Update the database
    if not i.channel == i.nickname:  # Avoid saving privmsges with the bot.
        update(i.channel, i.nickname, i.msg, timestamp, dbc)
        i.db[1].commit()
