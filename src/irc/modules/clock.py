#!/usr/bin/env python3
# coding=utf-8

# Location module for drastikbot.
#
# It uses the geonames.org API to get time information about a
# country/city/etc.
#
# Issues: geonames.org is slow and not very reliable, consider
#         rewriting it to use another API or an offline method.
#
# You may need to provide your own geonames.org username if the one
# provided doesn't work.

'''
Copyright (C) 2018 drastik (https://github.com/olagood)

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

import urllib.parse

import requests


class Module():
    def __init__(self):
        self.commands = ["time"]
        self.manual = {
            "desc": "Get time information about a country, a city, or a state",
            "bot_commands": {
                "time": {"usage": lambda x: f"{x}time <country/city/state>"}
            }
        }


username = "bugmenotuser"


def location_info_from_name(query):
    api_url = ("http://api.geonames.org/searchJSON?"
               f"q={query}&maxRows=1&username={username}")
    r = requests.get(api_url, timeout=30)
    try:
        return r.json()["geonames"][0]
    except IndexError:
        return False


def get_timezone_from_name(query):
    j = location_info_from_name(query)
    if not j:
        return f'Time: "{query}" is not a valid location'

    lng = j['lng']
    lat = j['lat']
    name = j['name']

    api_url = ("http://api.geonames.org/timezoneJSON?"
               f"lat={lat}&lng={lng}&username={username}")
    r = requests.get(api_url, timeout=30)
    j = r.json()

    try:
        gmtOffset = j['gmtOffset']
        countryName = j['countryName']
        time = j['time']
    except KeyError:
        return f'Time: "{query}" is not a valid location'

    ret = f"Time in {name}, {countryName}: {time} GMT {gmtOffset}"
    return ret


def main(i, irc):
    query = urllib.parse.quote_plus(i.msg_nocmd)
    irc.privmsg(i.channel, get_timezone_from_name(query))
