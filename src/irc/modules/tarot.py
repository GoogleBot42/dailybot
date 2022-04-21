#!/usr/bin/env python3
# coding=utf-8

# Tarot Module for drastikbot
#
# Draws three cards from the tarot deck.
# Usage: .tarot

'''
Copyright (C) 2018 Newt Vodyanoy

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

import random


class Module():
    def __init__(self):
        self.commands = ['tarot']
        self.manual = {
            "desc": "Draws three cards from the tarot deck.",
            "bot_commands": {"tarot": {"usage": lambda x: f"{x}tarot"}}
        }


major_arcana = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World"
]
suits = ["Swords", "Wands", "Coins", "Cups"]
suit_cards = [
    "Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
    "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"
]
minor_arcana = list()
for card in ((x, y) for x in suit_cards for y in suits):
    minor_arcana.append("The %s of %s" % card)
deck = major_arcana + minor_arcana


def main(i, irc):
    cards = random.sample(deck, 3)
    if 'tarot' == i.cmd:
        irc.privmsg(i.channel, f'{cards[0]}, {cards[1]}, {cards[2]}')
