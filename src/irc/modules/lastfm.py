#!/usr/bin/env python3
# coding=utf-8

# Last.fm Now Playing Module for Drastikbot
#
# It uses the Last.fm API to get the user's currently playing song.
# You need to provide your own API key to use this.
#
# Depends:
#   - requests      :: $ pip3 install requests

'''
Copyright (C) 2018, 2021 drastik.org

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

import requests
from user_auth import user_auth


class Module():  # Request commands to be used by the module
    def __init__(self):
        self.commands = ['np', 'npset', 'npunset', 'npauth']
        self.manual = {
            "desc": "Display your currently playing song using last.fm.",
            "irc_commands": {
                "np": {"usage": lambda x: f"{x}np [nickname]",
                       "info": "Show the song that is playing right now."},
                "npset": {"usage": lambda x: f"{x}npset <last.fm username>",
                          "info": "Set your last.fm username."},
                "npunset": {"usage": lambda x: f"{x}npunset",
                            "info": "Unset your last.fm username."},
                "npauth": {"usage": lambda x: f"{x}npauth",
                           "info": "Toggle NickServ authentication for npset"},
            }
        }


# ----- Constants ----- #
API_KEY = 'Add you lastfm API here'
# --------------------- #


def set_auth(i, irc, dbc, irc_nick):
    if not user_auth(i, irc, irc_nick):
        return f'{irc_nick}: You are not logged in with NickServ.'

    dbc.execute('SELECT auth FROM lastfm WHERE irc_nick=?;',
                (irc_nick,))
    fetch = dbc.fetchone()

    try:
        auth = fetch[0]
    except TypeError:  # 'NoneType' object is not subscriptable
        auth = 0

    if auth == 0:
        auth = 1
        msg = f'{irc_nick}: lastfm: Enabled NickServ authentication.'
    elif auth == 1:
        auth = 0
        msg = f'{irc_nick}: lastfm: Disabled NickServ authentication.'

    dbc.execute("INSERT OR IGNORE INTO lastfm (irc_nick, auth) VALUES (?, ?);",
                (irc_nick, auth))
    dbc.execute("UPDATE lastfm SET auth=? WHERE irc_nick=?;", (auth, irc_nick))
    return msg


def get_auth(i, irc, dbc, irc_nick):
    dbc.execute('SELECT auth FROM lastfm WHERE irc_nick=?;',
                (irc_nick,))
    fetch = dbc.fetchone()
    try:
        auth = fetch[0]
    except TypeError:  # 'NoneType' object is not subscriptable
        auth = 0

    if auth == 0:
        return True
    elif auth == 1 and user_auth(i, irc, irc_nick):
        return True
    else:
        return False


def set_user(i, irc, dbc, irc_nick, lfm_user):
    if not get_auth(i, irc, dbc, irc_nick):
        return f"{irc_nick}: lastfm: NickServ authentication is required."
    dbc.execute(
        '''INSERT OR IGNORE INTO lastfm (irc_nick, lfm_user)
        VALUES (?, ?);''', (irc_nick, lfm_user))
    dbc.execute('''UPDATE lastfm SET lfm_user=? WHERE irc_nick=?;''',
                (lfm_user, irc_nick))
    return f'{irc_nick}: Your last.fm username was set to "{lfm_user}"'


def unset_user(i, irc, dbc, irc_nick):
    if not get_auth(i, irc, dbc, irc_nick):
        return f"{irc_nick}: lastfm: NickServ authentication is required."
    try:
        dbc.execute('''DELETE FROM lastfm WHERE irc_nick=?;''', (irc_nick,))
    except Exception:
        return f"{irc_nick}: You haven't set a last.fm username."
    return f'{irc_nick}: Your last.fm username was unset.'


def get_user(dbc, irc_nick):
    try:
        dbc.execute('SELECT lfm_user FROM lastfm WHERE irc_nick=?;',
                    (irc_nick,))
        fetch = dbc.fetchone()
        lfm_user = fetch[0]
        return lfm_user
    except Exception:
        return False


def now_playing(dbc, irc_nick, same=False):
    lfm_user = get_user(dbc, irc_nick)
    if not lfm_user:
        return False
    url = ('https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks'
           f'&user={lfm_user}&api_key={API_KEY}&format=json&limit=1')
    try:
        r = requests.get(url, timeout=10)
    except Exception:
        return
    out = r.json()['recenttracks']['track'][0]
    try:
        artist = out['artist']['#text']
        song = out['name']
        album = out['album']['#text']
    except KeyError:
        pass
    try:
        np = out['@attr']['nowplaying']
    except KeyError:
        np = False

    if np == 'true':
        if album:
            ret = (f'\x0304{irc_nick}\x0F is listening to \x0304{song}\x0F by '
                   f'\x0304{artist}\x0F from the album \x0304{album}\x0F.')
        else:
            ret = (f'\x0304{irc_nick}\x0F is listening to \x0304{song}\x0F by '
                   f'\x0304{artist}\x0F.')
    else:
        if same:
            ret = 'You are not playing anything right now.'
        else:
            ret = f'\x0304{irc_nick}\x0F is not playing anything right now.'
    return ret


def main(i, irc):
    dbc = i.db[1].cursor()
    args = i.msg_nocmd.split()

    try:
        dbc.execute(
            '''CREATE TABLE IF NOT EXISTS lastfm (irc_nick TEXT COLLATE NOCASE
            PRIMARY KEY, lfm_user TEXT, auth INTEGER DEFAULT 0);''')
    except Exception:
        # sqlite3.OperationalError: cannot commit - no transaction is active
        pass

    if 'np' == i.cmd:
        if not args:
            np = now_playing(dbc, i.nickname, same=True)
            if not np:
                help_msg = (f"You haven't set your last.fm user yet. Set it "
                            f'with "{i.cmd_prefix}npset <Last.fm Username>".')
                return irc.privmsg(i.channel, help_msg)
            else:
                return irc.privmsg(i.channel, np)
        elif len(args) == 1:
            np = now_playing(dbc, args[0])
            return irc.privmsg(i.channel, np)
        else:
            help_msg = 'Usage: .np [nickname]'
            return irc.privmsg(i.channel, help_msg)
    elif 'npset' == i.cmd:
        if not args or len(args) > 1:
            help_msg = 'Usage: .npset <Last.fm Username>'
            return irc.privmsg(i.channel, help_msg)
        else:
            ret = set_user(i, irc, dbc, i.nickname, args[0])
            i.db[1].commit()
            return irc.privmsg(i.channel, ret)
    elif 'npunset' == i.cmd:
        ret = unset_user(i, irc, dbc, i.nickname)
        i.db[1].commit()
        return irc.privmsg(i.channel, ret)
    elif 'npauth' == i.cmd:
        ret = set_auth(i, irc, dbc, i.nickname)
        i.db[1].commit()
        irc.privmsg(i.channel, ret)
