#!/usr/bin/env python3
# coding=utf-8

# YouTube Module for Drastikbot
#
# Search YouTube and return the resulting video.
# When a YouTube url is posted return the video's information.
#
# If you are planning to use the url module or a url bot, consider adding the
# following blacklist: ['youtu.be/', 'youtube.com/watch']
#
# Depends:
#   - requests      :: $ pip3 install requests

'''
Copyright (C) 2018-2020 drastik.org

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
import json
import requests


class Module:
    def __init__(self):
        self.commands = ['yt']
        self.manual = {
            "desc": "Search YouTube and return the resulting video url.",
            "bot_commands": {"yt": {"usage": lambda x: f"{x}yt <video title>"}}
        }


# ----- Constants ----- #
lang = "en-US"
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
              " AppleWebKit/537.36 (KHTML, like Gecko)"
              " Chrome/83.0.4103.116 Safari/537.36")
# --------------------- #


def _text(obj):
    '''Get the text out of a YouTube "simpleText" or "runs" object.'''
    if not obj:
        return False
    if "simpleText" in obj:
        return obj["simpleText"]
    return "".join(r.get("text", "") for r in obj.get("runs", [])) or False


def yt_vid_info(v):
    yt_id = v["videoId"]
    short_url = f"https://youtu.be/{yt_id}"
    name = _text(v.get("title"))
    # Usually youtube's automated music uploads dont have dates.
    date = _text(v.get("publishedTimeText"))
    # Live streams don't have a length.
    duration = _text(v.get("lengthText")) or "LIVE"
    views = _text(v.get("viewCountText")) or "N/A"
    channel = _text(v.get("ownerText") or v.get("longBylineText")) or "N/A"

    return {
        'short_url': short_url, 'name': name, 'date': date, 'views': views,
        'channel': channel, 'duration': duration, 'yt_id': yt_id
    }


def yt_search(query):
    search = (f'https://www.youtube.com/results?search_query={query}'
              '&app=desktop')
    r = requests.get(search, timeout=10,
                     headers={"Accept-Language": lang,
                              "user-agent": user_agent})

    try:
        st = 'var ytInitialData = '
        st_i = r.text.index(st) + len(st)
    except ValueError:
        st = 'window["ytInitialData"] = '
        st_i = r.text.index(st) + len(st)

    j, _ = json.JSONDecoder().raw_decode(r.text[st_i:])

    sections = j["contents"]['twoColumnSearchResultsRenderer'][
        'primaryContents']['sectionListRenderer']['contents']

    for section in sections:
        res = section.get('itemSectionRenderer', {}).get('contents', [])
        for vid in res:
            # Promoted videos, shelves, channels, etc. are skipped.
            if "videoRenderer" in vid:
                return yt_vid_info(vid["videoRenderer"])  # Video information
    return False


def output(i):
    '''Format the output message to be returned.'''
    # logo_yt = "\x0301,00You\x0300,04Tube\x0F"
    logo_yt = "\x0300,04 ► \x0F"

    if i["date"]:
        date = f" | \x02Uploaded:\x0F {i['date']}"
    else:
        date = ""

    return (f"{logo_yt}: {i['short_url']} | "
            f"\x02{i['name']}\x0F ({i['duration']})"
            f" | \x02Views:\x0F {i['views']}"
            f" | \x02Channel\x0F: {i['channel']}"
            f"{date}")


def main(i, irc):
    if i.cmd:
        query = urllib.parse.quote_plus(i.msg_nocmd)
        try:
            res = yt_search(query)
        except Exception as e:
            print(e)
            res = False
        if res:
            out = output(res)
        else:
            out = f"YouTube: No results found for \"{i.msg_nocmd}\""
        irc.privmsg(i.channel, out)
