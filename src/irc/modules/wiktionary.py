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
# Wikimedia rejects requests without a descriptive user agent:
# https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
user_agent = "drastikbot/2.1 (https://git.neet.dev/zuckerberg/dailybot)"
# ---------------------------- #


# Part of speech headings to post definitions for.
pos_headings = ("Noun", "Verb", "Adjective", "Adverb", "Interjection",
                "Particle", "Preposition", "Pronoun", "Conjunction",
                "Proper noun", "Numeral", "Determiner", "Article", "Prefix",
                "Suffix", "Phrase", "Prepositional phrase", "Proverb",
                "Contraction", "Abbreviation", "Initialism", "Acronym",
                "Symbol", "Letter")


def heading_level(tag):
    '''
    Return the level of a section heading or 0 if 'tag' is not a heading.
    Headings look like: <div class="mw-heading mw-heading3"><h3>...</h3></div>
    '''
    if getattr(tag, "name", None) != "div":
        return 0
    for c in tag.get("class", []):
        if c.startswith("mw-heading") and c[10:].isdigit():
            return int(c[10:])
    return 0


def language_section(soup):
    '''
    Return the elements of the English section of the page, or of the first
    language on the page if there is no English section.
    '''
    h2 = soup.find("h2", id="English")
    if h2 is None:
        for h in soup.find_all("h2"):
            if heading_level(h.parent) == 2:
                h2 = h
                break
        else:
            return []

    section = []
    for tag in h2.parent.find_next_siblings():
        if heading_level(tag) == 2:
            break
        section.append(tag)
    return section


def section_text(tags, i, name):
    '''
    Get the text of the first 'name' element (e.g "p" or "ol") that follows
    the heading at tags[i], before the next heading.
    '''
    for tag in tags[i + 1:]:
        if heading_level(tag):
            return False
        if tag.name == name:
            # Remove quotations so that they are not in the definitions.
            for q in tag.find_all(["ul", "dl"]):
                q.decompose()
            for q in tag.find_all("span", class_="defdate"):
                q.decompose()
            for q in tag.find_all("sup", class_="reference"):
                q.decompose()  # Footnote links like [1]
            if name == "ol":
                # Number the definitions to keep them on one line.
                items = [" ".join(li.text.split())
                         for li in tag.find_all("li", recursive=False)]
                text = " ".join(f"{n}. {t}"
                                for n, t in enumerate(filter(None, items), 1))
            else:
                text = " ".join(tag.text.split())
            return text or False
    return False


def wiktionary(url, res):
    r = requests.get(url, timeout=r_timeout,
                     headers={"user-agent": user_agent})
    soup = bs4.BeautifulSoup(r.text, bs4_parser)
    tags = language_section(soup)

    result = {}
    current = "Etymology"  # Used for words without an etymology section.
    count = 0
    for i, tag in enumerate(tags):
        if not heading_level(tag):
            continue
        h = tag.find(["h3", "h4", "h5", "h6"])
        if h is None:
            continue
        title = h.get_text().strip()
        if title.startswith("Etymology"):
            count += 1
            current = "Etymology" if title == "Etymology" \
                else f"Etymology_{count}"
            result.setdefault(current, {})
            txt = section_text(tags, i, "p")
            if txt:
                result[current]["Etymology"] = txt
        elif title in pos_headings:
            txt = section_text(tags, i, "ol")
            if txt and title not in result.get(current, {}):
                result.setdefault(current, {})[title] = txt

    # Etymologies without definitions are not useful.
    return {k: v for k, v in result.items()
            if any(p in v for p in pos_headings)}


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

    result = list(result.values())[res - 1]

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
