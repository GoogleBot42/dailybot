import requests
import random
import re
import time

host = "https://collectionapi.metmuseum.org/public/collection/v1/"
# How long to keep the list of artwork before fetching it again (seconds)
objects_ttl = 24 * 60 * 60

def getObjects(i):
  # The list of artwork is ~3.5MB, so keep it in the bot's memory instead of
  # fetching it on every command. Module globals are reset when the bot
  # reloads its modules, which happens on every message, so use varset.
  cache = i.varget('objects', defval=(0, None))
  fetched, objects = cache
  if objects is None or time.time() - fetched > objects_ttl:
    r = requests.get(host + 'objects', timeout=30)
    objects = r.json()['objectIDs']
    i.varset('objects', (time.time(), objects))
  return objects

def getArt(i, term):
  # get the list of artwork
  objects = getObjects(i)

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
    msg = getArt(i, "")
    if msg is None:
      msg = "No result"
    else:
      msg = '"' + msg['title'] + '" ' + msg['objectDate'] + ' ' + msg['primaryImage']
    irc.privmsg(i.channel, msg)
