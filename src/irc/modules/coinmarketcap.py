#!/usr/bin/env python3
# coding=utf-8

# Cryptocurrency price fetcher for Drastikbot that uses
# https://coinmarketcap.com/api/

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


class Module:
    def __init__(self):
        self.commands = ['coin', 'cmc']
        self.helpmsg = [
            "Usage: .coin <COIN> [-p, --pair <FIAT/COIN>]",
            " ",
            "Get cryptocurrency prices from https://coinmarketcap.com",
            "The --pair option allows you to also get a Fiat price of the",
            "specified cryptocurrency.",
            "Examples: .coin BTC",
            "          .cmc LTC",
            "          .coin ETH -p EUR"]


def fiat2usd_fetch(fiat):
    f = fiat.upper()
    u = f"https://api.fixer.io/latest?base={f}&symbols=USD"
    r = requests.get(u, timeout=5)
    try:
        j = r.json()["rates"]["USD"]
    except KeyError:
        return False
    return j


def cmc_fetch(c, p):
    '''
    Use coinmarketcap.com API to get the required values.

    Returns:
        1     : Cryptocurrency requested not found.
        2     : Fiat requested not found.
        Tuple : Tuple with the needed values.
    '''
    coin = c.upper()
    url = f"https://api.coinmarketcap.com/v1/ticker/?convert={p}&limit=0"
    r = requests.get(url, timeout=5)
    for i in r.json():
        if not (coin == i["symbol"] or coin == i["name"].upper()):
            continue
        name = i["name"]
        sym = i["symbol"]
        try:
            fiat = i[f'price_{p.lower()}']
        except KeyError:
            return 2
        btc = i["price_btc"]
        c24 = i["percent_change_24h"]
        if "-" in c24:
            c24 = f"\x0304{c24} %\x0F"
        else:
            c24 = f"\x0303{c24} %\x0F"
        c7d = i["percent_change_7d"]
        if "-" in c7d:
            c7d = f"\x0304{c7d} %\x0F"
        else:
            c7d = f"\x0303{c7d} %\x0F"
        cap = "{:,}".format(float(i[f"market_cap_{p.lower()}"]))
        cap = f"{cap} {p.upper()}"
        t_sup = i["total_supply"]
        p_usd = i["price_usd"]
        return (name, sym, fiat, btc, cap, c24, c7d, t_sup, p_usd)
    else:
        return 1


def query(args):
    # Get the args list and the commands
    # Join the list to a string and return
    _args = args[:]
    cmds_args = ['--pair', '-p']
    if '--pair' in args or '-p' in args:
        try:
            idx = args.index('--pair')
        except ValueError:
            idx = args.index('-p')
        f = args[idx + 1]
    else:
        f = 'usd'
    for i in cmds_args:
        try:
            idx = _args.index(i)
            del _args[idx]
            del _args[idx]
        except ValueError:
            pass
    _args = ' '.join(_args)
    return (_args, f)


def main(i, irc):
    args = i.msg_nocmd.split()
    q = query(args)
    coin_ls = q[0].split()
    if len(coin_ls) != 1:
        # If no coin is given, send a help message.
        return irc.privmsg(i.channel,
                           f"Usage: {i.cmd_prefix}{i.cmd} <COIN> "
                           "[-p, --pair <FIAT/COIN>]"
                           f"  |  e.g. {i.cmd_prefix}{i.cmd} BTC")
    coin = coin_ls[0]
    pair = q[1]
    res = cmc_fetch(coin, pair)
    # Invalid input error handling.
    if res == 1:
        return irc.privmsg(i.channel, f"\x0311{coin}\x0F is not an available "
                           "cryptocurrency.")
    elif res == 2:
        return irc.privmsg(i.channel, f"Pair \x0311{pair}\x0F not found. "
                           "Available Pairs: [All cryptocurrencies] + AUD, "
                           "BRL, CAD, CHF, CLP, CNY, CZK, DKK, EUR, GBP, HKD, "
                           "HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, "
                           "PHP, PKR, PLN, RUB, SEK, SGD, THB, TRY, TWD, ZAR")
    if pair.lower() != 'usd':
        f2u = fiat2usd_fetch(pair)
        if not f2u:
            f2u = cmc_fetch(pair, 'usd')[2]
        rel_p = "{:,}".format(float(f2u) * float(res[2]))
        rel_p = f"\x02Relative price to USD:\x0F \x0311${rel_p} USD\x0F | "
    else:
        rel_p = ""
    # Main flow.
    p1po = "{:,}".format(float(res[7]) * 0.01 * float(res[8]))
    p1po = f"\x02Price of 1% ownership:\x0F \x0311${p1po} USD\x0F | "
    price = "{:,}".format(float(res[2]))
    irc.privmsg(i.channel, f"\x0311{res[0]} ({res[1]})\x0F: "
                f"\x02Price\x0F: \x0311{price} {pair.upper()}\x0F"
                f" , \x0311{res[3]} BTC\x0F"
                f" | {rel_p} {p1po}"
                f"\x02Market Cap\x0F: \x0311${res[4]}\x0F"
                f" | \x02Change (24h)\x0F: {res[5]}"
                f" | \x02Change (7d)\x0F: {res[6]}")
