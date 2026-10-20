import requests
import random
import re
import time

host = "https://collectionapi.metmuseum.org/public/collection/v1/"
search_host = "https://collectionapi.metmuseum.org/public/collection/v1.1/"
search_window = 10000  # /v1.1/search returns nothing past this offset
search_page = 20  # Search results to pick from
tries = 10  # Objects to try before giving up on finding one with an image
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

def searchObjects(term):
  # /v1.1/search is paginated and only serves the first 10000 results, so
  # count the matches, then fetch one random page of them.
  query = {'q': term, 'hasImages': 'true', 'limit': 1}
  r = requests.get(search_host + 'search', params=query, timeout=30)
  total = min(r.json()['total'], search_window)
  if total == 0:
    return []
  query['limit'] = search_page
  query['offset'] = random.randrange(0, max(total - search_page, 0) + 1)
  r = requests.get(search_host + 'search', params=query, timeout=30)
  return r.json()['objectIDs'] or []

def getArt(i, term):
  if term:
    objects = searchObjects(term)
  else:
    objects = getObjects(i)

  if not objects:
    return None

  # Not every object has an image we are allowed to post, try a few.
  for objectID in random.sample(objects, min(len(objects), tries)):
    r = requests.get(host + 'objects/' + str(objectID), timeout=30)
    j = r.json()
    if j.get('primaryImage'):
      return j
  return None

class Module:
    def __init__(self):
        self.commands = ['art']
        self.manual = {
            "desc": ("Post random art from metmuseum's api"),
            "bot_commands": {"art": {
                "usage": lambda x: f"{x}art [search term]",
                "info": "Without a search term, any artwork can be posted."
            }}
        }

def main(i, irc):
    term = i.msg_nocmd.strip()
    try:
      msg = getArt(i, term)
    except (requests.RequestException, ValueError, KeyError) as e:
      # The API answers with an html error page when it blocks a request.
      print(f"art: {e}")
      return irc.privmsg(i.channel, "The Met's collection API is not "
                         "responding right now, try again later.")
    if msg is None:
      msg = f'No result for "{term}"' if term else "No result"
    else:
      # Some titles contain html, e.g. "Arrowhead (<i>Yanone</i>)"
      title = re.sub(r'<[^>]+>', '', msg['title'])
      msg = '"' + title + '" ' + msg['objectDate'] + ' ' + msg['primaryImage']
    irc.privmsg(i.channel, msg)
