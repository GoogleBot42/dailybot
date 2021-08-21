import requests
import random
import re

host = "https://collectionapi.metmuseum.org/public/collection/v1/"

# get the list of artwork
r = requests.get(host + 'objects')
objects = r.json()['objectIDs']

def getArt(term):
  searchObjects = objects
  if term:
    query = {'q': term, 'hasImages': 'true'}
    r = requests.get(host + 'search', params=query)
    searchObjects = r.json()['objectIDs']

  if not searchObjects or len(searchObjects) == 0:
    return None

  tries = 10
  while tries > 0:
    r = requests.get(host + 'objects/' + str(random.choice(searchObjects)))
    j = r.json()
    if j['primaryImage']:
      return j
    tries -= 1
  return None

class Module:
    def __init__(self):
        self.commands = ['art']
        self.manual = {
            "desc": ("Post random art from metmuseum's api"),
            "bot_commands": {"art": {"usage": lambda x: f"{x}art"}}
        }

def main(i, irc):
    msg = getArt("")
    if msg is None:
      msg = "No result"
    else:
      msg = '"' + msg['title'] + '" ' + msg['objectDate'] + ' ' + msg['primaryImage']
    irc.privmsg(i.channel, msg)
