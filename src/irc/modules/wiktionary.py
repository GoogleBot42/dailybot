#!/usr/bin/env python3
# coding=utf-8

# Wiktionary Module for Drastikbot
#
# Depends:
#   - requests       :: $ pip3 install requests
#   - beautifulsoup4 :: $ pip3 install beautifulsoup4

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

import requests
import bs4
import re
from dbot_tools import p_truncate


class Module:
    def __init__(self):
        self.commands = ['wiktionary', 'wt']

        usage = lambda x, y: f"{x}{y} <word> [-e <num>]"
        info = ("The -e option allows you to choose other defintions."
                " The number of definitions is listed in parenthesis in the"
                " result. In a query, the bot will post the full definitions"
                " without truncating the text.")
        self.manual = {
            "desc": "Search https://en.wiktionary.org/ for word definitions.",
            "bot_commands": {
                "wiktionary": {"usage": lambda x: usage(x, "wiktionary"),
                               "info": info,
                               "alias": ["wt"]},
                "wt": {"usage": lambda x: usage(x, "wt"),
                       "info": info,
                       "alias": ["wiktionary"]}
            }
        }


# ----- Global Constants ----- #
r_timeout = 10
bs4_parser = 'html.parser'
# ---------------------------- #


def get_text(html, etymology):
    soup = bs4.BeautifulSoup(html, bs4_parser)

    result = {}
    result[etymology] = {}

    s_et = soup.find('span', id=etymology)
    result[etymology]["Etymology"] = s_et.find_next('p').text

    ids = ("Noun", "Verb", "Adjective", "Adverb",
           "Interjection", "Particle", "Preposition")
    for i in ids:
        s = s_et.find_next('span', string=i)
        try:
            txt = s.find_next('ol').text
            result[etymology][i] = txt
        except Exception as e:
            pass

    return result


def extract_etymologies(html):
    result = {}
    count = 1
    while(True):
        if 'id="Etymology"' in html:
            result.update(get_text(html, "Etymology"))
            break
        elif f'id="Etymology_{count}"' in html:
            result.update(get_text(html, f"Etymology_{count}"))
            count += 1
        else:
            break

    return result


def wiktionary(url, res):
    r = requests.get(url, timeout=r_timeout)

    # Extract the html of a single language section.
    section_end = '<hr'
    html = ""
    for t in r.text.splitlines():
        html += t
        if section_end in t:
            break

    # Remove quotations so that beautifulsoup doesn't catch them.
    html = re.compile(r'(?ims)<ul>.*?</ul>').sub('', html)
    html = re.compile(r'(?ims)<dl>.*?</dl>').sub('', html)
    html = re.compile(r'(?ims)<span class="defdate">.*?</span>').sub('', html)
    return extract_etymologies(html)


def query(args):
    # Get the args list and the commands
    # Join the list to a string and return
    _args = args[:]
    try:
        idx = _args.index('-e')
        del _args[idx]
        del _args[idx]
    except ValueError:
        pass
    return ' '.join(_args)


def main(i, irc):
    if not i.msg_nocmd:
        msg = (f'Usage: {i.cmd_prefix}{i.cmd} <Word> [-e <NUM>]')
        return irc.privmsg(i.channel, msg)

    args = i.msg_nocmd.split()

    if '-e' in args:
        idx = args.index('-e')
        res = int(args[idx + 1])
    else:
        res = 1

    q = query(args)
    q_web = q.replace(" ", "_")
    url = f"https://en.wiktionary.org/wiki/{q_web}"
    result = wiktionary(url, res)
    result_length = len(result)

    if res not in range(1, result_length + 1):
        msg = f'Wiktionary: No definition was found for "{q}" | {url}'
        return irc.privmsg(i.channel, msg)

    if res == 1:
        try:
            result = result["Etymology"]
        except KeyError:
            result = result["Etymology_1"]
    else:
        result = result[f"Etymology_{res}"]

    msg_len = (irc.var.msg_len - 9 - 8 - len(str(result_length))
               - (len(result) * 5) - len(url))
    p_tr_percent = 100 / len(result)

    txt = ""
    for part, cont in result.items():
        rslt = f"{part}: {cont}"
        if not i.nickname == i.channel:
            rslt = p_truncate(rslt, msg_len, p_tr_percent, True)
        txt += f"{rslt} | "

    rpl = f"{q} | {txt}({result_length}) | {url}"
    irc.privmsg(i.channel, rpl)
