#!/usr/bin/env python3
# coding=utf-8

# Lainstream for Drastikbot
#
# Update and get information about lainchan radio and video streams.
#
# Depends:
#   - requests      :: $ pip3 install requests

# © 2018-2021 All Rights Reserved olagood (drastik) <derezzed@protonmail.com>

import pickle
import xml.etree.ElementTree as ET
# from bs4 import BeautifulSoup
import requests


lainchan_org_logo = "\x0304Lainstream\x0F"
lainchan_org_logo_rtmp = "\x0304Lainstream\x0F RTMP"
lainchan_org_logo_ogv = "\x0304Lainstream\x0F OGV"

lain_la_logo = "lain.la"


class Module:
    def __init__(self):
        self.commands = ["stream",
                         "radio",
                         # lainchan.org
                         "streamset", "streamset-rtmp", "streamset-ogv",
                         "streamerset", "streamerset-rtmp", "streamerset-ogv",
                         "streamunset", "streamunset-rtmp", "streamunset-ogv",
                         "streamurls",
                         # lain.la
                         "streamset-la", "streamerset-la", "streamunset-la"]
        self.manual = {
            "desc": "Stream and radio information for lainchan.org.",
            "bot_commands": {
                "stream": {"usage": lambda x: f"{x}stream",
                           "info": "Display the currently active streams."},
                "radio": {"usage": lambda x: f"{x}radio",
                          "info": "Station information for lainchan radio."},
                "streamset": {
                    "usage": lambda x: f"{x}streamset [title]",
                    "info": ("Set the stream title for lainchan's RTMP"
                             " stream. The streamer is also set to the"
                             " nickname of the caller. If no title is"
                             " provided, it unsets the stream."),
                    "alias": ["streamset-rtmp"]},
                "streamset-rtmp": {
                    "usage": lambda x: f"{x}streamset-rtmp [title]",
                    "info": ("Set the stream title for lainchan's RTMP"
                             " stream. The streamer is also set to the"
                             " nickname of the caller. If no title is"
                             " provided, it unsets the stream."),
                    "alias": ["streamset"]},
                "streamset-ogv": {
                    "usage": lambda x: f"{x}streamset-ogv [title]",
                    "info": ("Set the stream title for lainchan's OGV"
                             " stream. The streamer is also set to the"
                             " nickname of the caller. If no title is"
                             " provided, it unsets the stream.")},
                "streamerset": {
                    "usage": lambda x: f"{x}streamerset <name>",
                    "info": "Set the streamer for lainchan's RTMP stream",
                    "alias": ["streamerset-rtmp"]},
                "streamerset-rtmp": {
                    "usage": lambda x: f"{x}streamerset-rtmp <name>",
                    "info": "Set the streamer for lainchan's RTMP stream",
                    "alias": ["streamerset"]},
                "streamerset-ogv": {
                    "usage": lambda x: f"{x}streamerset-ogv <name>",
                    "info": "Set the streamer for lainchan's OGV stream"},
                "streamunset": {
                    "usage": lambda x: f"{x}streamunset",
                    "info": ("Unset the title and the streamer for lainchan's"
                             " RTMP stream."),
                    "alias": ["streamunset-rtmp"]},
                "streamunset-rtmp": {
                    "usage": lambda x: f"{x}streamunset-rtmp",
                    "info": ("Unset the title and the streamer for lainchan's"
                             " RTMP stream."),
                    "alias": ["streamunset"]},
                "streamunset-ogv": {
                    "usage": lambda x: f"{x}streamunset-ogv",
                    "info": ("Unset the title and the streamer for lainchan's"
                             " OGV stream.")},
                "streamurls": {
                    "usage": lambda x: f"{x}streamurls",
                    "info": "Show lainchan's RTMP, HLS and OGV stream urls."},
                "streamset-la": {
                    "usage": lambda x: f"{x}streamset-la [title]",
                    "info": ("Set the stream title for the lain.la"
                             " stream. The streamer is also set to the"
                             " nickname of the caller. If no title is"
                             " provided, it unsets the stream.")},
                "streamerset-la": {
                    "usage": lambda x: f"{x}streamerset <name>",
                    "info": "Set the streamer for lain.la's stream"},
                "streamunset-la": {
                    "usage": lambda x: f"{x}streamunset-la",
                    "info": ("Unset the title and the streamer for lain.la's"
                             " stream.")}
            }
        }


# ====================================================================
# IRC: Arisu bot control
# ====================================================================

def arisu_streamerset_rtmp(irc, streamer):
    irc.privmsg("Arisu", f"!streamerset {streamer}")


def arisu_streamset_rtmp(irc, title, streamer):
    irc.privmsg("Arisu", f"!streamset {title}")
    irc.privmsg("Arisu", f"!streamerset {streamer}")


def arisu_streamunset_rtmp(irc):
    irc.privmsg("Arisu", "!streamunset")
    irc.privmsg("Arisu", "!streamerunset")


def arisu_streamerset_ogv(irc, streamer):
    irc.privmsg("Arisu", f"!streamerset --ogv {streamer}")


def arisu_streamset_ogv(irc, title, streamer):
    irc.privmsg("Arisu", f"!streamset --ogv {title}")
    irc.privmsg("Arisu", f"!streamerset --ogv {streamer}")


def arisu_streamunset_ogv(irc):
    irc.privmsg("Arisu", "!streamunset --ogv")
    irc.privmsg("Arisu", "!streamerunset --ogv")


# ====================================================================
# Radio: lainon.life
# ====================================================================

# IRC callbacks

def radio(state, i, irc):
    m = "\x0306Lainchan Radio\x0F: "
    urls = ("https://lainon.life/playlist/cyberia.json",
            "https://lainon.life/playlist/cafe.json",
            "https://lainon.life/playlist/everything.json",
            "https://lainon.life/playlist/swing.json")
    for url in urls:
        channel = url.rsplit("/")[-1][:-5]
        r = requests.get(url, timeout=10)
        j = r.json()
        # live = j['stream_data']['live']
        c_artist = j['current']['artist']
        c_title = j['current']['title']
        listeners = j['listeners']['current']
        m += (f"\x0305{channel} {listeners}\x0F:"
              f" \x0302{c_artist} - {c_title}\x0F | https://lainon.life/")
    irc.privmsg(i.channel, m)


# ====================================================================
# Video: lainchan.org
# ====================================================================

# State functions

def lainchan_org_rtmp_viewers():
    url = "https://lainchan.org:8080/stat"
    r = requests.get(url, timeout=10)
    xml_root = ET.fromstring(r.text)
    viewers = 0
    count = 0
    for i in xml_root.iter("live"):
        nclients = i.find("nclients")
        viewers += int(nclients.text)
        if viewers >= 2 and count == 0:
            viewers -= 2
        count += 1
    return viewers


def lainchan_org_rtmp_status(state):
    title = state["lainchan.org"]["rtmp"]["title"]
    if not title:
        return ""
    viewers = lainchan_org_rtmp_viewers()
    streamer = state["lainchan.org"]["rtmp"]["streamer"]
    url = state["lainchan.org"]["url"]
    rtmp_url = state["lainchan.org"]["rtmp"]["url"]
    return (f"{lainchan_org_logo_rtmp}:"
            f" \x0311{title}\x0F by \x0302{streamer}\x0F"
            f" | Viewers: {viewers} | Watch at: {url} | RTMP: {rtmp_url}")


def lainchan_org_ogv_status(state):
    title = state["lainchan.org"]["ogv"]["title"]
    if not title:
        return ""
    streamer = state["lainchan.org"]["ogv"]["streamer"]
    url = state["lainchan.org"]["url"]
    ogv_url = state["lainchan.org"]["ogv"]["url"]
    return (f"{lainchan_org_logo_ogv}:"
            f" \x0311{title}\x0F by \x0302{streamer}\x0F"
            f" | Watch at: {url} | OGV: {ogv_url}")


def lainchan_org_rtmp_set(state, title, streamer):
    state["lainchan.org"]["rtmp"]["title"] = title
    state["lainchan.org"]["rtmp"]["streamer"] = streamer
    return state


def lainchan_org_ogv_set(state, title, streamer):
    state["lainchan.org"]["ogv"]["title"] = title
    state["lainchan.org"]["ogv"]["streamer"] = streamer
    return state


# IRC callbacks

def lainchan_org_stream_unset_rtmp(state, i, irc):
    state = lainchan_org_rtmp_set(state, "", "")
    m = f"{lainchan_org_logo_rtmp}: Stream information was unset!"
    irc.privmsg(i.channel, m)
    arisu_streamunset_rtmp(irc)
    return state


def lainchan_org_stream_set_rtmp(state, i, irc):
    streamer = i.nickname
    title = i.msg_nocmd

    if not title:
        return lainchan_org_stream_unset_rtmp(state, i, irc)

    state = lainchan_org_rtmp_set(state, title, streamer)
    m = f"{lainchan_org_logo_rtmp}: Stream information updated!"
    irc.privmsg(i.channel, m)
    arisu_streamset_rtmp(irc, title, streamer)
    return state


def lainchan_org_streamer_set_rtmp(state, i, irc):
    streamer = i.msg_nocmd
    title = state["lainchan.org"]["rtmp"]["title"]

    if not streamer:
        m = (f"{lainchan_org_logo_rtmp}: Usage: "
             f"{i.cmd_prefix}{i.cmd} <streamer>")
        irc.privmsg(i.channel, m)
        return

    if not title:
        m = (f"{lainchan_org_logo_rtmp}: Set a title using "
             f"`{i.cmd_prefix}{i.cmd}' first.")
        irc.privmsg(i.channel, m)
        return

    state = lainchan_org_rtmp_set(state, title, streamer)
    m = f"{lainchan_org_logo_rtmp}: Streamer updated!"
    irc.privmsg(i.channel, m)
    arisu_streamerset_rtmp(irc, streamer)
    return state


def lainchan_org_stream_unset_ogv(state, i, irc):
    state = lainchan_org_ogv_set(state, "", "")
    m = f"{lainchan_org_logo_ogv}: Stream information was unset!"
    irc.privmsg(i.channel, m)
    arisu_streamunset_ogv(irc)
    return state


def lainchan_org_stream_set_ogv(state, i, irc):
    streamer = i.nickname
    title = i.msg_nocmd

    if not title:
        return lainchan_org_stream_unset_ogv(state, i, irc)

    state = lainchan_org_ogv_set(state, title, streamer)
    m = f"{lainchan_org_logo_ogv}: Stream information updated!"
    irc.privmsg(i.channel, m)
    arisu_streamset_ogv(irc, title, streamer)
    return state


def lainchan_org_streamer_set_ogv(state, i, irc):
    streamer = i.msg_nocmd
    title = state["lainchan.org"]["ogv"]["title"]

    if not streamer:
        m = (f"{lainchan_org_logo_ogv}: Usage: "
             f"{i.cmd_prefix}{i.cmd} <streamer>")
        irc.privmsg(i.channel, m)
        return

    if not title:
        m = (f"{lainchan_org_logo_ogv}: Set a title using "
             f"`{i.cmd_prefix}{i.cmd}' first.")
        irc.privmsg(i.channel, m)
        return

    state = lainchan_org_ogv_set(state, title, streamer)
    m = f"{lainchan_org_logo_ogv}: Streamer updated!"
    irc.privmsg(i.channel, m)
    arisu_streamerset_ogv(irc, streamer)
    return state


def lainchan_org_stream_urls(state, i, irc):
    rtmp = state["lainchan.org"]["rtmp"]["url"]
    hls = state["lainchan.org"]["rtmp"]["url-hls"]
    ogv = state["lainchan.org"]["ogv"]["url"]
    m = (f"{lainchan_org_logo_rtmp}: {rtmp} / {hls}"
         f" | {lainchan_org_logo_ogv}: {ogv}")
    irc.privmsg(i.channel, m)


# ====================================================================
# Video: lain.la
# ====================================================================

# State functions

def lain_la_status(state):
    title = state["lain.la"]["title"]
    if not title:
        return ""
    streamer = state["lain.la"]["streamer"]
    url = state["lain.la"]["url"]
    rtmp_url = state["lain.la"]["url-rtmp"]
    return (f"{lain_la_logo}:"
            f" \x0311{title}\x0F by \x0302{streamer}\x0F"
            f" | Watch at: {url} | RTMP: {rtmp_url}")


def lain_la_set(state, title, streamer):
    state["lain.la"]["title"] = title
    state["lain.la"]["streamer"] = streamer
    return state


# IRC callbacks

def lain_la_stream_unset(state, i, irc):
    state = lain_la_set(state, "", "")
    m = f"{lain_la_logo}: Stream information was unset!"
    irc.privmsg(i.channel, m)
    return state


def lain_la_stream_set(state, i, irc):
    streamer = i.nickname
    title = i.msg_nocmd

    if not title:
        return lain_la_stream_unset(state, i, irc)

    state = lain_la_set(state, title, streamer)
    m = f"{lain_la_logo}: Stream information updated!"
    irc.privmsg(i.channel, m)
    return state


def lain_la_streamer_set(state, i, irc):
    streamer = i.msg_nocmd
    title = state["lain.la"]["title"]

    if not streamer:
        m = (f"{lain_la_logo}: Usage: "
             f"{i.cmd_prefix}{i.cmd} <streamer>")
        irc.privmsg(i.channel, m)
        return

    if not title:
        m = (f"{lain_la_logo}: Set a title using "
             f"`{i.cmd_prefix}{i.cmd}' first.")
        irc.privmsg(i.channel, m)
        return

    state = lain_la_set(state, title, streamer)
    m = f"{lain_la_logo}: Streamer updated!"
    irc.privmsg(i.channel, m)
    return state


# ====================================================================
# IRC: Generic callbacks
# ====================================================================

def stream(state, i, irc):
    stream_status_list = [
        lainchan_org_rtmp_status(state),
        lainchan_org_ogv_status(state),
        lain_la_status(state)
    ]

    if all([not i for i in stream_status_list]):
        m = (f"{lainchan_org_logo}: Nothing is streaming right now."
             " Learn how you can stream at: "
             "https://lainchan.org/stream.html ")
        irc.privmsg(i.channel, m)

        return

    for s in stream_status_list:
        if s:
            irc.privmsg(i.channel, s)


def stream_how(state, i, irc):
    pass


# ====================================================================
# Main
# ====================================================================

callbacks = {
    "stream": stream,
    # lainon.life / lainchan radio
    "radio": radio,
    # lainchan.org
    "streamset": lainchan_org_stream_set_rtmp,
    "streamset-rtmp": lainchan_org_stream_set_rtmp,
    "streamset-ogv": lainchan_org_stream_set_ogv,
    "streamerset": lainchan_org_streamer_set_rtmp,
    "streamerset-rtmp": lainchan_org_streamer_set_rtmp,
    "streamerset-ogv": lainchan_org_streamer_set_ogv,
    "streamunset": lainchan_org_stream_unset_rtmp,
    "streamunset-rtmp": lainchan_org_stream_unset_rtmp,
    "streamunset-ogv": lainchan_org_stream_unset_ogv,
    "streamurls": lainchan_org_stream_urls,
    # lain.la
    "streamset-la": lain_la_stream_set,
    "streamerset-la": lain_la_streamer_set,
    "streamunset-la": lain_la_stream_unset
}


def main(i, irc):
    state = {
        "lainchan.org": {
            "url": "https://lainchan.org/stream.html",
            "ogv": {
                "url": "https://lainchan.org/icecast/lainstream.ogg",
                "title": "",
                "streamer": ""
            },
            "rtmp": {
                "url": "rtmp://lainchan.org/show/stream",
                "url-hls": "https://lainchan.org:8080/hls/stream.m3u8",
                "title": "",
                "streamer": ""
            }
        },
        "lain.la": {
            "url": "https://stream.lain.la",
            "url-rtmp": "rtmp://lain.la",
            "title": "",
            "streamer": ""
        }
    }

    db = i.db[1]
    dbc = db.cursor()
    try:
        dbc.execute('''SELECT value FROM stream;''')
        fetch = dbc.fetchone()
        state = pickle.loads(fetch[0])
    except Exception:
        dbc.execute('''CREATE TABLE IF NOT EXISTS stream (value BLOB);''')

    callbacks[i.cmd](state, i, irc)

    v = pickle.dumps(state)
    try:
        dbc.execute('''INSERT INTO stream (value) VALUES (?);''', (v,))
    except Exception:
        pass
    dbc.execute('''UPDATE stream SET value = ?''', (v,))
    db.commit()
