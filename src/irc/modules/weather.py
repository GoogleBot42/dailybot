#!/usr/bin/env python3
# coding=utf-8

# Weather Module for Drastikbot
#
# Provides weather information from http://wttr.in
#
# Depends:
#   - requests      :: $ pip3 install requests

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

import urllib.parse
import requests
from user_auth import user_auth


class Module:
    def __init__(self):
        self.commands = ['weather', 'weather_set', 'weather_auth']
        self.manual = {
            "desc": "Show weather information from http://wttr.in",
            "bot_commands": {
                "weather": {
                    "usage": lambda x: (
                        f"{x}weather <location / airport code / @domain"
                        " / IP address / area code / GPS coordinates>"
                    ),
                    "info": "Get weather information."
                },
                "weather_set": {
                    "usage": lambda x: (
                        f"{x}weather_set <location / airport code / @domain"
                        " / IP address / area code / GPS coordinates>"
                    ),
                    "info": (
                        "Set your default location. If a location has been"
                        " set, calling the weather command without arguments"
                        " will return the weather for that location, otherwise"
                        " you will be asked to provide a location. To unset"
                        " your location use .weather_set without any"
                        " arguements."
                    )
                },
                "weather_auth": {
                    "usage": lambda x: f"{x}weather_auth",
                    "info": "Toggle NickServ authentication for weather_set"
                }
            }
        }


# Helper functions:

def unit_swap(unit):
    """Change the unit string from °C to °F or from km/h to mph and opposite"""
    unit_d = {
        "°C": "°F",
        "°F": "°C",
        "km/h": "mph",
        "mph": "km/h"
        }
    return unit_d.get(unit)


# Temperature

def temperature_color(temperature, unit_in, unit_out):
    """Colorize and convert the temperature."""
    tempcolor_d = {  # celsius: color
        -12: "02", -9: "12", -6: "11", 2: "10",
        10: "03", 19: "09", 28: "08", 37: "07"
    }
    if "°C" == unit_in:
        celsius = int(temperature.split("(")[0])
        fahrenheit = celsius * 1.8 + 32
        fahrenheit = int(round(fahrenheit, 0))
    elif "°F" == unit_in:
        fahrenheit = int(temperature.split("(")[0])
        celsius = (fahrenheit - 32) / 1.8
        celsius = int(round(celsius, 0))
    else:
        return "invalid input unit"

    for temp, color in tempcolor_d.items():
        if celsius <= temp:
            if "°C" == unit_out:
                return f"\x03{color} {celsius}\x0F"
            elif "°F" == unit_out:
                return f"\x03{color} {fahrenheit}\x0F"

    # Fallback for when the temperature is too high.
    if "°C" == unit_out:
        return f"\x0304 {celsius}\x0F"
    elif "°F" == unit_out:
        return f"\x0304 {fahrenheit}\x0F"


def temp_format_range(temp_list, unit, unit_s):
    ret = "Temp:"
    ret += f"{temperature_color(temp_list[0], unit, unit)} -"
    ret += f"{temperature_color(temp_list[1], unit, unit)} {unit} /"
    ret += f"{temperature_color(temp_list[0], unit, unit_s)} -"
    ret += f"{temperature_color(temp_list[1], unit, unit_s)} {unit_s}"
    return ret


def temp_format(txt):
    temperature_list = txt.split()  # ['25..27', '°C']
    temperature = temperature_list[0]
    # dashes = temperature.count('-')
    unit = temperature_list[1]
    unit_s = unit_swap(unit)
    ret = "Temp:"

    if '..' in temperature:
        temp_list = temperature.split('..')
        ret = temp_format_range(temp_list, unit, unit_s)
    else:
        ret += f"{temperature_color(temperature, unit, unit)} {unit} /"
        ret += f"{temperature_color(temperature, unit, unit_s)} {unit_s}"

    return ret


# Wind

def wind_color(wind, unit_in, unit_out):
    windcolor_d = {  # km/h: color
        4: "03", 10: "09", 20: "08", 32: "07"
    }
    if "km/h" == unit_in:
        kmh = int(wind)
        mph = kmh * 0.6213711922
        mph = int(round(mph, 0))
    elif "mph" == unit_in:
        mph = int(wind)
        kmh = mph * 1.609344
        kmh = int(round(kmh, 0))
    # elif "m/s" == unit_in:
    #     ms = int(wind)
    #     kmh = ms * 3.6

    for k, color in windcolor_d.items():
        if kmh < k:
            if "km/h" == unit_out:
                return f"\x03{color} {kmh}\x0F"
            elif "mph" == unit_out:
                return f"\x03{color} {mph}\x0F"

    # Fallback for when the wind speed is too high.
    if "km/h" == unit_out:
        return f"\x0304 {kmh}\x0F"
    elif "mph" == unit_out:
        return f"\x0304 {mph}\x0F"


def wind_format(txt):
    def range_hdl(t, tempstr):
        for idx, i in enumerate(t):
            coltemp = wind_color(i, unit)
            tempstr += f'{coltemp}'
            if idx == 0:
                tempstr += ' -'
        return tempstr

    wind_list = txt.split()  # ['↑', '23', 'km/h']
    icon = wind_list[0]
    wind = wind_list[1]
    unit = wind_list[2]
    unit_s = unit_swap(unit)
    dashes = wind.count('-')
    ret = f'Wind: {icon}'

    if 1 == dashes:
        # NEEDLESS?
        wind_list = wind.split('-')
        ret += f"{wind_color(wind_list[0], unit, unit)} -"
        ret += f"{wind_color(wind_list[1], unit, unit)} {unit} /"
        ret += f"{wind_color(wind_list[0], unit, unit_s)} -"
        ret += f"{wind_color(wind_list[1], unit, unit_s)} {unit_s}"
    else:  # 17 km/h
        ret += f"{wind_color(wind, unit, unit)} {unit} /"
        ret += f"{wind_color(wind, unit, unit_s)} {unit_s}"

    return f'{ret}'


def handler(txt):
    if ('°C' in txt) or ('°F' in txt):
        return temp_format(txt)
    elif ('km/h' in txt) or ('mph' in txt) or ('m/s' in txt):
        return wind_format(txt)
    elif ('km' in txt) or ('mi' in txt):
        return f'Visibility: {txt}'
    elif ('mm' in txt) or ('in' in txt):
        return f'Rainfall: {txt}'
    elif '%' in txt:
        return f'Rain Prob: {txt}'
    else:
        return txt


# Ascii art set from:
# https://github.com/schachmat/wego/blob/master/frontends/ascii-art-table.go
art = (
    '             ',
    '    .-.      ',
    '     __)     ',
    '    (        ',
    '     `-᾿     ',
    '      •      ',
    '     .--.    ',
    '  .-(    ).  ',
    ' (___.__)__) ',
    '  _ - _ - _  ',
    ' _ - _ - _ - ',
    '    (   ).   ',
    '   (___(__)  ',
    '  ‚ʻ‚ʻ‚ʻ‚ʻ   ',
    ' _`/"".-.    ',
    '  ,\\_(   ).  ',
    '   /(___(__) ',
    '   ‚ʻ‚ʻ‚ʻ‚ʻ  ',
    '   ‚’‚’‚’‚’  ',
    '   ‚‘‚‘‚‘‚‘  ',
    '     .-.     ',
    '   * * * *   ',
    '  * * * *    ',
    '    * * * *  ',
    '    ʻ ʻ ʻ ʻ  ',
    '   ʻ ʻ ʻ ʻ   ',
    '     ʻ ʻ ʻ ʻ ',
    '    ‘ ‘ ‘ ‘  ',
    '    ʻ * ʻ *  ',
    '   * ʻ * ʻ   ',
    '     ʻ * ʻ * ',
    '    * ʻ * ʻ  ',
    '   *  *  *   ',
    '     *  *  * ',
    '    *  *  *  ',
    '   \\  /      ',
    ' _ /"".-.    ',
    '   \\_(   ).  ',
    '    \\   /    ',
    '  ‒ (   ) ‒  ',
    '    /   \\    ',
    '  ‚ʻ⚡ʻ‚⚡‚ʻ   ',
    '  ‚ʻ‚ʻ⚡ʻ‚ʻ   ',
    '    ⚡ʻ ʻ⚡ʻ ʻ ',
    '     *⚡ *⚡ * ',
    '  ― (   ) ―  ',
    '     `-’     ',
    '   ⚡‘‘⚡‘‘  '
)


def wttr(irc, channel, location):
    if location.lower() == 'moon' or 'moon@' in location.lower():
        irc.privmsg(channel, 'This is not supported yet '
                    '(add ,+US or ,+France for these cities)')
        return

    location = urllib.parse.quote_plus(location)
    url = f'http://wttr.in/{location}?0Tm'
    r = requests.get(url, timeout=10).text.splitlines()
    text = ''
    for line in r:
        for i in art:
            line = line.replace(i, '')
        if line:
            line = handler(line)
            text += f'{line} | '

    text = " ".join(text.split())  # Remove additional spaces.
    text = text.lstrip("Rainfall: ")  # Remove 'Rainfall: ' from the front.
    if "ERROR: Unknown location:" in text:
        text = f'\x0304wttr.in: Location "{location}" could not be found.'
    elif "API key has reached calls per day allowed limit." in text\
         or ("Sorry, we are running out of queries to the weather service at "
             "the moment.") in text:
        text = "\x0304wttr.in: API call limit reached. Try again tomorrow."

    irc.privmsg(channel, text)


# Authentication

def set_auth(i, irc, dbc):
    if not user_auth(i, irc, i.nickname):
        return f"{i.nickname}: You are not logged in with NickServ."

    dbc.execute('SELECT auth FROM weather WHERE nickname=?;',
                (i.nickname,))
    fetch = dbc.fetchone()

    try:
        auth = fetch[0]
    except TypeError:  # 'NoneType' object is not subscriptable
        auth = 0

    if auth == 0:
        auth = 1
        msg = f'{i.nickname}: weather: Enabled NickServ authentication.'
    elif auth == 1:
        auth = 0
        msg = f'{i.nickname}: weather: Disabled NickServ authentication.'

    dbc.execute(
        "INSERT OR IGNORE INTO weather (nickname, auth) VALUES (?, ?);",
        (i.nickname, auth))
    dbc.execute("UPDATE weather SET auth=? WHERE nickname=?;",
                (auth, i.nickname))
    return msg


def get_auth(i, irc, dbc):
    dbc.execute('SELECT auth FROM weather WHERE nickname=?;', (i.nickname,))
    fetch = dbc.fetchone()
    try:
        auth = fetch[0]
    except TypeError:  # 'NoneType' object is not subscriptable
        auth = 0

    if auth == 0:
        return True
    elif auth == 1 and user_auth(i, irc, i.nickname):
        return True
    else:
        return False


def set_location(i, irc, dbc, location):
    if not get_auth(i, irc, dbc):
        return f"{i.nickname}: weather: NickServ authentication is required."
    dbc.execute(
        '''INSERT OR IGNORE INTO weather (nickname, location)
        VALUES (?, ?);''', (i.nickname, location))
    dbc.execute('''UPDATE weather SET location=? WHERE nickname=?;''',
                (location, i.nickname))
    return f'{i.nickname}: weather: Your location was set to "{location}"'


def get_location(dbc, nickname):
    try:
        dbc.execute(
            'SELECT location FROM weather WHERE nickname=?;', (nickname,))
        return dbc.fetchone()[0]
    except Exception:
        return False


def main(i, irc):
    dbc = i.db[1].cursor()

    try:
        dbc.execute(
            '''CREATE TABLE IF NOT EXISTS weather (nickname TEXT COLLATE NOCASE
            PRIMARY KEY, location TEXT, auth INTEGER DEFAULT 0);''')
    except Exception:
        # sqlite3.OperationalError: cannot commit - no transaction is active
        pass

    if "weather" == i.cmd:

        if not i.msg_nocmd:
            location = get_location(dbc, i.nickname)
            if location:
                wttr(irc, i.channel, location)
            else:
                msg = (f'Usage: {i.cmd_prefix}{i.cmd} '
                       '<Location / Airport code / @domain / '
                       'IP address / Area code / GPS coordinates>')
                irc.privmsg(i.channel, msg)
        else:
            wttr(irc, i.channel, i.msg_nocmd)

    elif "weather_set" == i.cmd:
        ret = set_location(i, irc, dbc, i.msg_nocmd)
        i.db[1].commit()
        irc.privmsg(i.channel, ret)
    elif "weather_auth" == i.cmd:
        ret = set_auth(i, irc, dbc)
        i.db[1].commit()
        irc.privmsg(i.channel, ret)
