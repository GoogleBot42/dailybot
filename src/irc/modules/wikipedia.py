#!/usr/bin/env python3
# coding=utf-8

# Wikipedia Module for Drastikbot
#
# NOTE: This module is making use of the MediaWiki API,
# so it should work with other MediaWiki based websites.
#
# Depends:
#   - requests       :: $ pip3 install requests
#   - beautifulsoup4 :: $ pip3 install beautifulsoup4

'''
Copyright (C) 2017 drastik.org

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
import urllib.parse
from dbot_tools import Config, p_truncate


class Module:
    def __init__(self):
        self.commands = ['wikipedia', 'wiki', 'w']

        usage = lambda x, y: (f"{x}{y} <article> [--full] [--search]"
                           " [--sections] [-l <lang>] [--resuult <num>]")
        info = ("--info: Get the full section in a query."
                " / --search: Search and get the results in a query."
                " / --sections: Get all the sections of an article in a query."
                " / -l: Post an article from a specific language"
                " / --result: Select specific result."
                " <num> is the index of the result returned by --search"
                " / Use #section after the article's name to get a specific"
                " section. Example: .w irc#Technical information")
        self.manual = {
            "desc": ("Search wikipedia and post a snippet from the resulting"
                     " article."),
            "bot_commands": {
                "wikipedia": {"usage": lambda x: usage(x, "wikipedia"),
                              "info": info,
                              "alias": ["w", "wiki"]},
                "wiki": {"usage": lambda x: usage(x, "wiki"),
                         "info": info,
                         "alias": ["w", "wikipedia"]},
                "w": {"usage": lambda x: usage(x, "w"),
                      "info": info,
                      "alias": ["wikipedia", "wiki"]}
            }
        }


# ----- Global Constants ----- #
r_timeout = 10
bs4_parser = 'html.parser'
# ---------------------------- #


def language(args, config, channel):
    '''Set the language used to search for wikipedia articles'''
    if '-l' in args:
        # Check if the language command has been used and
        # use the given value instead of the configuration
        index = args.index('-l')
        return args[index + 1]
    else:
        # Try loading from the configuration
        try:
            # Check the configuration file for per channel language settings.
            return config['irc']['modules']['wikipedia']['channels'][channel]
        except KeyError:
            try:
                # Check the configuration file for global language settings
                return config['irc']['modules']['wikipedia']['lang']
            except KeyError:
                # Return English if all above fails
                return 'en'


def mw_opensearch(query, url, max_results=1):
    '''
    Uses the MediaWiki API:Opensearch
    https://en.wikipedia.org/w/api.php?action=help&modules=opensearch

    Search MediaWiki for articles relevant to the search 'query'
    It returns a [query,[titles],[descriptions],[urls]] of relevant
    results to the search query.

    'query' is the string to search for
    'url' is the url of the MediaWiki website
    'max_results' is the maximum amount of results to get
    '''
    u = (f'{url}/w/api.php'
         f'?action=opensearch&format=json&limit={max_results}&search={query}')
    r = requests.get(u, timeout=r_timeout)
    return r.json()


def mw_list_sections(page, url):
    '''
    Uses the MediaWiki API:Parsing_wikitext#parse
    https://www.mediawiki.org/wiki/Special:MyLanguage/API:Parsing_wikitext#parse

    Get a list of all the available sections for a given article.
    Returns a tuple with the title of the article and a
    list [[sections],[indexes]]

    'page' should be the name of the MediaWiki article as returned
    by mw_opensearch()
    'url' is the url of the MediaWiki website
    '''
    u = f'{url}/w/api.php?action=parse&format=json&prop=sections&page={page}'
    r = requests.get(u, timeout=r_timeout)
    parse = r.json()
    title = parse['parse']['title']
    sections_ = parse['parse']['sections']
    section_list = [[], []]
    for i in sections_:
        section_list[0].append(i['line'])
        section_list[1].append(i['index'])
    return (title, section_list)


def text_cleanup(soup):
    try:
        for sup in soup('sup'):
            soup.sup.decompose()
    except AttributeError:
        pass
    try:
        for small in soup('small'):
            soup.small.decompose()
    except AttributeError:
        pass
    return soup


def mw_parse_intro(url, page, limit):
    '''
    Uses the MediaWiki API:Parsing_wikitext#parse
    https://www.mediawiki.org/wiki/Special:MyLanguage/API:Parsing_wikitext#parse

    This function calls the MediaWiki API, which returns a JSON
    document containing the html of the introduction section
    of an article, which is parsed by beautifulsoup4, limited
    to the specified amount of characters and returned.

    'url' is the url of the MediaWiki website
    'page' should be the name of the MediaWiki article as
    returned by mw_opensearch()
    'limit' if True truncate the text
    '''
    u = (f'{url}/w/api.php'
         f'?action=parse&format=json&prop=text&section=0&page={page}')
    r = requests.get(u, timeout=r_timeout)
    html = r.json()['parse']['text']['*']
    soup = bs4.BeautifulSoup(html, bs4_parser)
    soup = text_cleanup(soup)
    text = soup.find('p').text
    if text == 'Redirect to:':
        n_title = soup.find('a').text
        n_text = mw_parse_intro(url, n_title, limit)
        text = f'\x0302[Redirect to: {n_title}]\x0F {n_text}'
    if limit:
        text = p_truncate(text, msg_len, 85, True)
    return text


def mw_parse_section(url, section_list, page, sect, limit):
    '''
    Uses the MediaWiki API:Parsing_wikitext#parse
    https://www.mediawiki.org/wiki/Special:MyLanguage/API:Parsing_wikitext#parse

    This function finds the position of the section ('sect')
    requested in 'section_list' and calls the MediaWiki API,
    which returns a JSON document containing the html of the
    requested section which is parsed by beautifulsoup4,
    limited to the specified amount of characters and returned.

    'url' is the url of the MediaWiki website
    'section_list' is the second item returned by mw_list_sections()
    'page' should be the name of the MediaWiki article as
    returned by mw_opensearch()
    'sect' is the section requested to be viewed
    'limit' if True truncate the text
    '''
    id_index = section_list[0].index(sect)
    u = (f'{url}/w/api.php'
         '?action=parse&format=json&prop=text'
         f'&section={section_list[1][id_index]}&page={page}')
    r = requests.get(u, timeout=r_timeout)
    html = r.json()['parse']['text']['*']
    soup = bs4.BeautifulSoup(html, bs4_parser)
    soup = text_cleanup(soup)
    text = soup.find('span', id=sect)
    text = text.find_next('p').text
    if limit:
        text = p_truncate(text, msg_len, 85, True)
    return text


def str2url(url):
    return urllib.parse.quote_plus(url)


def query(args):
    # Get the args list and the commands
    # Join the list to a string and return
    _args = args[:]
    cmds = ['--search', '--sections', '--full']
    cmds_args = ['--result', '-r', '-l']
    for i in cmds_args:
        try:
            idx = _args.index(i)
            del _args[idx]
            del _args[idx]
        except ValueError:
            pass
    for i in cmds:
        try:
            idx = _args.index(i)
            del _args[idx]
        except ValueError:
            pass
    return ' '.join(_args)


def main(i, irc):
    if not i.msg_nocmd:
        msg = (f'Usage: {i.cmd_prefix}{i.cmd} <Article> '
               '[--full, --search, --sections -l], [--result <NUM>]')
        return irc.privmsg(i.channel, msg)

    channel = i.channel
    args = i.msg_nocmd.split()
    config = Config(irc.cd).read()
    lang = language(args, config, i.channel)
    # Do not put a "/" slash at the end of the url
    mediawiki_url = f'https://{lang}.wikipedia.org'
    logo = '\x0301,00Wikipedia\x0F'
    limit = True
    search_q = query(args)
    global msg_len
    msg_len = irc.var.msg_len - 9 - 22

    if '--search' in args:
        opensearch = mw_opensearch(search_q, mediawiki_url, 10)
        rs_string = ''
        for n in opensearch[1]:
            rs_string += f'[{opensearch[1].index(n) + 1}:{n}] '
        msg = (f'{logo}: \x0302[search results for: '
               f'{search_q}]\x0F: {rs_string}')
        return irc.privmsg(i.nickname, msg)

    if '--full' in args:
        limit = False
        channel = i.nickname

    if '--result' in args or '-r' in args:
        try:
            r_index = args.index('--result')
        except ValueError:
            r_index = args.index('-r')
        os_limit = int(args[r_index + 1])
        opensearch = mw_opensearch(search_q, mediawiki_url, os_limit)
        try:
            title = opensearch[1][os_limit - 1]
        except IndexError:
            msg = f'{logo}: No article was found for \x02{search_q}\x0F'
            return irc.privmsg(channel, msg)
    else:
        opensearch = mw_opensearch(search_q, mediawiki_url)
        try:
            title = opensearch[1][0]
        except IndexError:
            msg = f'{logo}: No article was found for \x02{search_q}\x0F'
            return irc.privmsg(channel, msg)
    wikiurl = f'{mediawiki_url}/wiki/{title.replace(" ", "_")}'

    if '--sections' in args:
        sections_out = mw_list_sections(title, mediawiki_url)
        sec_out_str = ' | '.join(sections_out[1][0])
        msg = (f'{logo}: \x0302 [sections for {sections_out[0]}]\x0F: '
               f'{sec_out_str} [ {wikiurl} ]')
        irc.privmsg(i.nickname, msg)
    elif '#' in search_q:
        ts_list = search_q.split('#')
        sections_out = mw_list_sections(title, mediawiki_url)
        snippet = mw_parse_section(mediawiki_url, sections_out[1],
                                   title, ts_list[1], limit)
        msg = f'{logo}: \x02{title}#{ts_list[1]}\x0F | {snippet} | {wikiurl}'
        irc.privmsg(channel, msg)
    else:
        snippet = mw_parse_intro(mediawiki_url, title, limit)
        msg = f'{logo}: \x02{title}\x0F | {snippet} | {wikiurl}'
        irc.privmsg(channel, msg)
