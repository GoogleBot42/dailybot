import requests

host = "http://localhost:5000/"
radioUrl = "https://radio.neet.space/stream.mp3"

class Module:
    def __init__(self):
        self.commands = ["dailyradio",
                         "play",
                         "current",
                         "skip",
                         "queue",
                         "listeners"]
        self.manual = {
            "desc": "Stream and radio information for dailyradio",
            "bot_commands": {
                "dailyradio": {"usage": lambda x: f"{x}dailyradio",
                           "info": "Display the dailyradio stream url."},
                "play": {"usage": lambda x: f"{x}play URL",
                          "info": "plays the url on the radio."},
                "current": {"usage": lambda x: f"{x}current",
                          "info": "Gets what's currently playing on the radio."},
                "skip": {"usage": lambda x: f"{x}skip",
                          "info": "Skips what's currently playing on the radio."},
                "queue": {"usage": lambda x: f"{x}queue",
                          "info": "Gets the radio's play queue"},
                "listeners": {"usage": lambda x: f"{x}listeners",
                          "info": "Returns the number of clients listening to the radio"}
            }
        }

def dailyradio(i, irc):
    irc.privmsg(i.channel, radioUrl)

def play(i, irc):
    if not i.msg_nocmd:
        m = f"Usage: {i.cmd_prefix}{i.cmd} URL"
        irc.privmsg(i.channel, m)
        return
    pload = {'url': i.msg_nocmd}
    r = requests.post(host+"play", data = pload)
    irc.privmsg(i.channel, r.text)

def current(i, irc):
    r = requests.get(host+"current")
    irc.privmsg(i.channel, r.text)

def skip(i, irc):
    r = requests.get(host+"skip")
    irc.privmsg(i.channel, r.text)

def queue(i, irc):
    r = requests.get(host+"queue")
    irc.privmsg(i.channel, r.text)

def listeners(i, irc):
    r = requests.get(host+"listeners")
    irc.privmsg(i.channel, r.text)

callbacks = {
    "dailyradio": dailyradio,
    "play": play,
    "current": current,
    "skip": skip,
    "queue": queue,
    "listeners": listeners
}

def main(i, irc):
    callbacks[i.cmd](i, irc)