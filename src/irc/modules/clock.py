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

import datetime
import re
import urllib.parse

import requests


class Module():
    def __init__(self):
        self.commands = ["time"]
        self.manual = {
            "desc": "Get time information about a country, a city, or a state",
            "bot_commands": {
                "time": {"usage": lambda x: (
                    f"{x}time <country/city/state | utc[+-offset]>")}
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


def get_utc_time(query):
    '''
    Get the time for "utc", "gmt" or "z", optionally with an offset such as
    "utc+2", "UTC -5" or "gmt+5:30". Returns False if 'query' is not one.
    '''
    m = re.fullmatch(r"(utc|gmt|z)\s*(?:([+-])\s*(\d{1,2})(?::?(\d{2}))?)?",
                     query.strip(), re.IGNORECASE)
    if not m:
        return False
    name, sign, hours, minutes = m.groups()
    name = name.upper()
    offset = datetime.timedelta(hours=int(hours or 0),
                                minutes=int(minutes or 0))
    if offset > datetime.timedelta(hours=14):
        return f'Time: "{query}" is not a valid UTC offset'
    if sign == "-":
        offset = -offset

    time = datetime.datetime.now(datetime.timezone.utc) + offset
    time = time.strftime("%Y-%m-%d %H:%M")
    if sign:
        hm = f"{hours}:{minutes}" if minutes else hours
        name = f"{name}{sign}{hm}"
    gmtOffset = offset.total_seconds() / 3600
    gmtOffset = int(gmtOffset) if gmtOffset.is_integer() else gmtOffset
    return f"Time in {name}: {time} GMT {gmtOffset}"


def main(i, irc):
    utc = get_utc_time(i.msg_nocmd)
    if utc:
        return irc.privmsg(i.channel, utc)
    query = urllib.parse.quote_plus(i.msg_nocmd)
    irc.privmsg(i.channel, get_timezone_from_name(query))
