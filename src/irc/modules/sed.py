#!/usr/bin/env python3
# coding=utf-8

# Sed Module for Drastikbot
#
# Replace text using sed.
#
# This module keeps a buffer of the last posted messages
# and when the substitution command is issued it calls sed
# and sends the result.
#
# Depends:
#   - sed :: default unix program, should be in the repos

'''
Copyright (C) 2018 drastik.org

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

import subprocess
import re
from dbot_tools import p_truncate


class Module:
    def __init__(self):
        self.auto = True
        self.manual = {
            "desc": (
                "Usage: s/regexp/replacement/flags"
                " | Try to match a 'regexp' with one of the previous"
                " messages posted and replace it with 'replacement'."
                " For flags and a detailed explanation see:"
                " https://www.gnu.org/software/sed/manual/html_node/"
                "The-_0022s_0022-Command.html"
                " | Extensions: \"s///-n\" n is the number of matches to skip"
                " If the 'number' flag is used -n should be used after it.")
        }


def write(varget, varset, channel, msg):
    msgdict = varget('msgdict', defval={channel: [msg]})

    try:
        msgdict[channel].append(msg)
    except KeyError:
        msgdict.update({channel: [msg]})

    if len(msgdict[channel]) > 50:
        del msgdict[channel][0]

    varset('msgdict', msgdict)


def read(varget, channel):
    return varget('msgdict')[channel]


def call_sed(msg, sed_args):
    echo = ['echo', msg]
    p = subprocess.run(echo, stdout=subprocess.PIPE)
    echo_outs = p.stdout
    sed = ['sed', '-r', '--sandbox',
           f's/{sed_args[1]}/{sed_args[2]}/{sed_args[3]}']
    p = subprocess.run(sed, stdout=subprocess.PIPE, input=echo_outs)
    return p.stdout.decode('utf-8')


def main(i, irc):
    sed_parse = re.compile('(?<!\\\\)/')
    sed_cmd = re.compile('^s/.*/.*')
    sed_out = ''

    if not sed_cmd.match(i.msg):
        write(i.varget, i.varset, i.channel, i.msg)
        return

    sed_args = sed_parse.split(i.msg)

    if len(sed_args) < 4:
        # check if the last / is missed etc.
        return

    msglist = read(i.varget, i.channel)

    # Extension to allow the user match previous messages.
    # It uses the special syntax: "s///-n" where n is the
    # number of matches to skip.
    # Sideffect: because it matches upto two decimals after -,
    #            sed string positioning (or other commands
    #            with decimals in them) should be issued
    #            before the - command or two characters after
    #            the - .
    # The following code is for parsing the command. It
    # edits the "goback" variable which will be used in the
    # loop below.
    # We use two decimals because the queue save upto 50
    # messages.
    goback = False
    if '-' in sed_args[3]:
        s = sed_args[3]
        idx = s.index('-')
        if len(s[idx:]) > 2 and s[idx + 2].isdecimal():
            goback = int(f'{s[idx + 1]}{s[idx + 2]}')
            sed_args[3] = f'{s[:idx]}{s[idx + 3:]}'
        elif len(s[idx:]) > 1 and s[idx + 1].isdecimal():
            goback = int(s[idx + 1])
            sed_args[3] = f'{s[:idx]}{s[idx + 2:]}'

    n = 1
    while n <= 50:
        if 'i' in sed_args[3]:
            db_search = re.search(sed_args[1], msglist[-n], re.I)
        else:
            db_search = re.search(sed_args[1], msglist[-n])
        if db_search:
            if goback:
                # Check if the goback command was issued.
                goback -= 1
                n = n + 1
                continue
            a = n
            break
        else:
            a = False
        n = n + 1

    if a:
        if '\x01ACTION' in msglist[-a][:7]:
            msg_len = irc.var.msg_len - 9 - len(i.channel) - 10 - 2
            sed_out = call_sed(msglist[-a][7:], sed_args)
            sed_out = sed_out.rstrip('\n').replace('\x01', "").replace('\ca', "")
            sed_out = p_truncate(sed_out, msg_len, 98, True)
            irc.privmsg(i.channel, f'\x01ACTION {sed_out}')
        else:
            msg_len = irc.var.msg_len - 9 - len(i.channel) - 2
            sed_out = call_sed(msglist[-a], sed_args).strip()
            sed_out = sed_out.rstrip('\n').replace('\x01', "").replace('\ca', "")
            sed_out = p_truncate(sed_out, msg_len, 98, True)
            irc.privmsg(i.channel, sed_out)

    if sed_out:
        # We try to limit the string saved in the queue to avoid:
        # OSError: [Errno 7] Argument list too long: 'echo'
        # when calling 'echo' in @call_sed .
        # 512 chars are more than enough, since the bot will
        # never be able to send a message with that many.
        write(i.varget, i.varset, i.channel, sed_out)
    # write(dbc, i.channel, i.msg) # save commands
