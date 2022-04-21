#!/usr/bin/env python3
# coding=utf-8

# Quote Module for Drastikbot
#
# Save user quotes and send them to a channel upon request.

'''
Copyright (C) 2019-2021 drastik.org

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

import random
import sqlite3

import requests

from admin import is_allowed

logo = "\x02quote\x0F"


class Module:
    def __init__(self):
        self.commands = ['quote', 'findquote', 'addquote', 'delquote',
                         'listquotes']
        self.manual = {
            "desc": "Saves user quotes and posts them when requested.",
            "bot_commands": {
                "quote": {
                    "usage": lambda x: (
                        f"[channels]: {x}quote [nickname/id/text]"
                        f" | [queries]: {x}quote <#channel> [nickname/id/text]"
                    ),
                    "info": ("Without any arguments, a random quote will be"
                             " posted. If arguments are given the will try to"
                             " first match a nickname, then an ID and then"
                             " the text of a quote.")
                },
                "findquote": {
                    "usage": lambda x: (
                        f"[channels]: {x}findquote <text>"
                        f" | [queries]: {x}findquote <#channel> <text>"
                    ),
                    "info": ("Try to match the given text to a quote."
                             " If a quote is found, it is posted.")
                },
                "addquote": {
                    "usage": lambda x: f"{x}addquote <nickname> <quote>",
                    "info": "Add a quote to the database."
                },
                "delquote": {
                    "usage": lambda x: f"{x}delquote <id>",
                    "info": "Delete a quote using its ID"
                },
                "listquotes": {
                    "usage": lambda x: f"{x}listquotes <#channel>",
                    "info": ("List all the quotes in which the the caller is"
                             " mentioned in. The list is sent in a query.")
                }
            }
        }


def add(channel, quote, made_by, added_by, dbc):
    try:
        dbc.execute("INSERT INTO quote(channel, quote, made_by, added_by) "
                    "VALUES (?, ?, ?, ?)", (channel, quote, made_by, added_by))
        return f"{logo}: #{dbc.lastrowid} Added!"
    except sqlite3.IntegrityError:
        return f"{logo}: This quote has already been added."


def delete(quote_id, dbc):
    try:
        dbc.execute('''DELETE FROM quote WHERE num=?;''', (quote_id,))
        return f"{logo}: #{quote_id} deleted."
    except Exception:
        pass


def find(channel, query, dbc, export_all=False):
    try:
        dbc.execute(
            '''SELECT num FROM quote_index
            WHERE quote_index MATCH ? AND channel=?;''',
            (f"quote:{query}", channel))
        f = dbc.fetchall()
        num = random.choice(f)[0]
        dbc.execute('''SELECT * FROM quote WHERE num=?''', (num,))
        if export_all:
            return dbc.fetchall()
        f = dbc.fetchone()
        return f"{logo}: #{f[0]} | {f[2]} \x02-\x0F {f[3]} | Added by {f[4]}"
    except Exception:
        if export_all:
            return False
        return f"{logo}: No results."


def _search_by_nick(channel, text, dbc, export_all=False):
    try:
        if not text:
            dbc.execute('SELECT * FROM quote WHERE channel=?', (channel,))
        else:
            dbc.execute('SELECT * FROM quote WHERE made_by=? AND channel=?;',
                        (text, channel))
        f = dbc.fetchall()
        if export_all:
            return f
        f = random.choice(f)
        return f"{logo}: #{f[0]} | {f[2]} \x02-\x0F {f[3]} | Added by {f[4]}"
    except Exception:
        return False


def _search_by_id(channel, text, dbc):
    if not text.isdigit():
        return False

    try:
        dbc.execute('SELECT * FROM quote WHERE num=? AND channel=?;', (text, channel))
        f = dbc.fetchone()
        return f"{logo}: #{f[0]} | {f[2]} \x02-\x0F {f[3]} | Added by {f[4]}"
    except Exception:
        return False


def listquotes(channel, nickname, dbc, irc):
    data = ""

    sbn = _search_by_nick(channel, nickname, dbc, export_all=True)
    if sbn:
        for f in sbn:
            m = f"#{f[0]} | {f[2]} - {f[3]} | Added by {f[4]}\n\n"
            data += m

    rest = find(channel, nickname, dbc, export_all=True)
    if rest:
        for f in rest:
            m = f"#{f[0]} | {f[2]} - {f[3]} | Added by {f[4]}\n\n"
            data += m

    if not rest and not sbn:
        irc.notice(nickname, f"{logo}: No results.")
    else:
        pomf_url = listquotes_pomf(data)
        m = f"{logo}: Your quotes can be found here: {pomf_url}"
        irc.notice(nickname, m)


def listquotes_pomf(data):
    url = "https://pomf.lain.la/upload.php"
    files = {"files[]": ("quotes.txt", data, "text/plain")}
    r = requests.post(url, files=files)
    return r.json()["files"][0]["url"]



def quote(channel, text, dbc):
    sbn = _search_by_nick(channel, text, dbc)
    if sbn:
        return sbn
    sbi = _search_by_id(channel, text, dbc)
    if sbi:
        return sbi

    return find(channel, text, dbc)


def main(i, irc):
    dbc = i.db[1].cursor()
    dbc.execute(
        '''
        CREATE TABLE IF NOT EXISTS quote
        (num     INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        channel  TEXT,
        quote    TEXT COLLATE NOCASE UNIQUE,
        made_by  TEXT COLLATE NOCASE,
        added_by TEXT COLLATE NOCASE);''')
    dbc.execute(
        '''
        CREATE VIRTUAL TABLE IF NOT EXISTS quote_index
        USING fts5(num, quote, channel, tokenize=porter);''')
    dbc.execute(
        '''
        CREATE TRIGGER IF NOT EXISTS quote_after_insert AFTER INSERT ON quote
        BEGIN
        INSERT INTO quote_index (num, quote, channel)
        VALUES (new.num, new.quote, new.channel);
        END;''')
    dbc.execute(
        '''
        CREATE TRIGGER IF NOT EXISTS quote_after_delete AFTER DELETE ON quote
        BEGIN
        DELETE FROM quote_index WHERE num = old.num;
        END;''')
    i.db[1].commit()

    if 'quote' == i.cmd:
        if i.is_pm:
            if not i.msg_nocmd:
                m = (f"{logo}: Usage: {i.cmd_prefix}{i.cmd} "
                     f"<#channel> <Nickname / ID / Query>")
                irc.privmsg(i.channel, m)
                return
            channel = i.msg_nocmd.split()[0]
            if not channel[:1] == '#':
                m = (f"{logo}: Usage: {i.cmd_prefix}{i.cmd} "
                     f"<#channel> <Nickname / ID / Query>")
                irc.privmsg(i.channel, m)
                return
            if channel not in irc.var.namesdict:
                m = f"{logo}: The bot has not joined the channel: {channel}"
                irc.privmsg(i.channel, m)
                return
            query = " ".join(i.msg_nocmd.split()[1:])
            irc.privmsg(i.channel, quote(channel, query, dbc))
        else:
            irc.privmsg(i.channel, quote(i.channel, i.msg_nocmd, dbc))

    elif 'findquote' == i.cmd:
        if i.is_pm:
            if not i.msg_nocmd or len(i.msg_nocmd.split()) < 2:
                m = f"{logo}: Usage: {i.cmd_prefix}{i.cmd} <#channel> <Query>"
                irc.privmsg(i.channel, m)
                return
            channel = i.msg_nocmd.split()[0]
            if not channel[:1] == '#':
                m = f"{logo}: Usage: {i.cmd_prefix}{i.cmd} <#channel> <Query>"
                irc.privmsg(i.channel, m)
                return
            if channel not in irc.var.namesdict:
                m = f"{logo}: The bot has not joined the channel: {channel}"
                irc.privmsg(i.channel, m)
                return
            query = " ".join(i.msg_nocmd.split()[1:])
            irc.privmsg(i.channel, find(channel, query, dbc))
        else:
            if not i.msg_nocmd:
                m = f"{logo}: Usage: {i.cmd_prefix}{i.cmd} <Query>"
                irc.privmsg(i.channel, m)
                return
            irc.privmsg(i.channel, find(i.channel, i.msg_nocmd, dbc))

    elif 'delquote' == i.cmd:
        if i.is_pm:
            m = f"{logo}: This command can only be used within a channel."
            irc.privmsg(i.channel, m)
            return
        if not i.msg_nocmd or not i.msg_nocmd.isdigit():
            m = f"{logo}: Usage: {i.cmd_prefix}{i.cmd} <ID>"
            irc.privmsg(i.channel, m)
            return
        if is_allowed(i, irc, i.nickname, i.channel):
            irc.privmsg(i.channel, delete(i.msg_nocmd, dbc))
        else:
            m = f"{logo}: Only Channel Operators are allowed to delete quotes."
            irc.privmsg(i.channel, m)

    elif 'addquote' == i.cmd:
        if i.is_pm:
            m = (f"{logo}: Please, submit the quote in the channel it was"
                 " posted in.")
            irc.privmsg(i.channel, m)
        else:
            if not i.msg_nocmd or len(i.msg_nocmd.split()) < 2:
                m = f"{logo}: Usage: {i.cmd_prefix}{i.cmd} <Nickname> <Quote>"
                irc.privmsg(i.channel, m)
                return
            made_by = i.msg_nocmd.split()[0]
            quote_text = " ".join(i.msg_nocmd.split()[1:])
            irc.privmsg(i.channel,
                        add(i.channel, quote_text, made_by, i.nickname, dbc))

    elif 'listquotes' == i.cmd:
        if not i.msg_nocmd or len(i.msg_nocmd.split()) != 1:
            m = f"{logo}: Usage: {i.cmd_prefix}{i.cmd} <#channel>"
            irc.privmsg(i.channel, m)
            return
        channel = i.msg_nocmd.split()[0]
        if not channel[:1] == '#':
            m = f"{logo}: Usage: {i.cmd_prefix}{i.cmd} <#channel>"
            irc.privmsg(i.channel, m)
            return
        if channel not in irc.var.namesdict:
            m = f"{logo}: The bot has not joined the channel: {channel}"
            irc.privmsg(i.channel, m)
            return
        listquotes(channel, i.nickname, dbc, irc)
    i.db[1].commit()
