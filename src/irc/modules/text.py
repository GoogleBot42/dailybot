#!/usr/bin/env python3
# coding=utf-8

# Text Module for Drastikbot
#
# Transform textual input to various other styles.

'''
Copyright (C) 2019 drastik.org

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


class Module:
    def __init__(self):
        self.commands = [
            "ae", "text-c", "text-nc", "text-s", "text-ns", "flag", "cirrus",
            "strike", "strikethrough"
        ]
        self.manual = {
            "desc": "Text transformation tools",
            "bot_commands": {
                "ae": {"usage": lambda p: f"{p}ae <text>",
                       "info": "Example: Ｈｅｌｌｏ，　Ｗｏｒｌｄ！"},
                "text-c": {"usage": lambda p: f"{p}text-c <text>",
                           "info": "Example: ⒽⒺⓁⓁⓄ, ⓌⓄⓇⓁⒹ!"},
                "text-nc": {"usage": lambda p: f"{p}text-nc <text>",
                            "info": "Example: 🅗🅔🅛🅛🅞, 🅦🅞🅡🅛🅓!"},
                "text-s": {"usage": lambda p: f"{p}text-s <text>",
                           "info": "Example: 🄷🄴🄻🄻🄾, 🅆🄾🅁🄻🄳!"},
                "text-ns": {"usage": lambda p: f"{p}text-ns <text>",
                            "info": "Example: 🅷🅴🅻🅻🅾, 🆆🅾🆁🅻🅳!"},
                "flag": {"usage": lambda p: f"{p}flag <text>",
                         "info": ("Transforms two letter country codes to"
                                  " regional indicator symbols.")},
                "cirrus": {"usage": lambda p: f"{p}cirrus <text>",
                           "info": "Example: Hello, WWorld!"},
                "strike": {"usage": lambda p: f"{p}strike <text>",
                           "info": "Example: H̶e̶l̶l̶o̶,̶ ̶W̶o̶r̶l̶d̶!̶",
                           "alias": ["strikethrough"]},
                "strikethrough": {
                    "usage": lambda p: f"{p}strikethrough <text>",
                    "info": "Example: H̶e̶l̶l̶o̶,̶ ̶W̶o̶r̶l̶d̶!̶",
                    "alias": ["strike"]
                }
            }
        }


# https://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms_(Unicode_block)
FULLWIDTH_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
FULLWIDTH_MAP[0x20] = 0x3000

# https://en.wikipedia.org/wiki/Enclosed_Alphanumerics
_CIRCLED_NUM_MAP = dict((i, (i - 0x31) + 0x2460) for i in range(0x30, 0x3A))
_CIRCLED_NUM_MAP[0x30] = 0x24EA  # Set the actual Circled digit zero character
_CIRCLED_ALP_U_MAP = dict((i, (i - 0x41) + 0x24B6) for i in range(0x41, 0x5B))
_CIRCLED_ALP_L_MAP = dict((i, (i - 0x61) + 0x24B6) for i in range(0x61, 0x7B))
CIRCLED_MAP = {**_CIRCLED_NUM_MAP, **_CIRCLED_ALP_U_MAP, **_CIRCLED_ALP_L_MAP}

# https://en.wikipedia.org/wiki/Enclosed_Alphanumeric_Supplement
_NEGATIVE_CIRCLED_ALP_U_MAP = dict(
    (i, (i - 0x41) + 0x1F150) for i in range(0x41, 0x5B))
_NEGATIVE_CIRCLED_ALP_L_MAP = dict(
    (i, (i - 0x61) + 0x1F150) for i in range(0x61, 0x7B))
NEGATIVE_CIRCLED_MAP = {
    **_NEGATIVE_CIRCLED_ALP_U_MAP,
    **_NEGATIVE_CIRCLED_ALP_L_MAP
}

_SQUARED_ALP_U_MAP = dict((i, (i - 0x41) + 0x1F130) for i in range(0x41, 0x5B))
_SQUARED_ALP_L_MAP = dict((i, (i - 0x61) + 0x1F130) for i in range(0x61, 0x7B))
SQUARED_MAP = {**_SQUARED_ALP_U_MAP, **_SQUARED_ALP_L_MAP}

_NEGATIVE_SQUARED_ALP_U_MAP = dict(
    (i, (i - 0x41) + 0x1F170) for i in range(0x41, 0x5B))
_NEGATIVE_SQUARED_ALP_L_MAP = dict(
    (i, (i - 0x61) + 0x1F170) for i in range(0x61, 0x7B))
NEGATIVE_SQUARED_MAP = {
    **_NEGATIVE_SQUARED_ALP_U_MAP,
    **_NEGATIVE_SQUARED_ALP_L_MAP
}

# https://en.wikipedia.org/wiki/Regional_Indicator_Symbol
_REGIONAL_INDICATOR_SYMBOL_U_MAP = dict(
    (i, (i - 0x41) + 0x1F1E6) for i in range(0x41, 0x5B))
_REGIONAL_INDICATOR_SYMBOL_L_MAP = dict(
    (i, (i - 0x61) + 0x1F1E6) for i in range(0x61, 0x7B))
REGIONAL_INDICATOR_SYMBOL_MAP = {
    **_REGIONAL_INDICATOR_SYMBOL_U_MAP,
    **_REGIONAL_INDICATOR_SYMBOL_L_MAP
}

command_map_d = {
    "ae": FULLWIDTH_MAP,
    "text-c": CIRCLED_MAP,
    "text-nc": NEGATIVE_CIRCLED_MAP,
    "text-s": SQUARED_MAP,
    "text-ns": NEGATIVE_SQUARED_MAP,
    "flag": REGIONAL_INDICATOR_SYMBOL_MAP,
}


def cirrus(text):
    words = text.split()
    wc = len(words)
    cc = 0
    for i in range(wc):
        if random.uniform(0, 1) < 0.38:
            cc += 1
            words[i] = f"{words[i][0]}{words[i]}"

    if cc == 0:
        i = random.randint(0, wc - 1)
        words[i] = f"{words[i][0]}{words[i]}"

    return " ".join(words)


def strikethrough(text):
    return "\u0336".join(text) + '\u0336'


def main(i, irc):
    if not i.msg_nocmd:
        return
    s = i.msg_nocmd

    if i.cmd == "cirrus":
        return irc.privmsg(i.channel, cirrus(s))
    if i.cmd == "strike" or i.cmd == "strikethrough":
        return irc.privmsg(i.channel, strikethrough(s))

    t = s.translate(command_map_d[i.cmd])
    if i.cmd == "ae" and t == s:
        t = s.replace("", " ")[1: -1]

    irc.privmsg(i.channel, t)
