import json
import urllib2
import urllib
import sys
from categorizers import *

details = {}
def read_details(filename):
  f = open(filename, 'r')
  global details
  details = json.load(f)

read_details('details')

weka = False

if weka:
  categorizer = WekaCategorizer(EverythingLabeler(), details)
else:
  categorizer = SVMCategorizer(EverythingLabeler(), details)
  
def get_content(line):
  line = line.split(':', 1)[-1]
  line = line.strip()
  return line

def get_song_details(artist, title):
  url = 'http://developer.echonest.com/api/v4/song/search?api_key=G7A8JR9MHLSHZ9CBW&format=json&results=1&bucket=audio_summary&'
  data = {}
  data['artist'] = artist
  data['title'] = title
  url_values = urllib.urlencode(data)
  url += url_values
  response = urllib2.urlopen(url)
  data = json.load(response)
  try:
    data = data['response']['songs'][0]['audio_summary']
    global details
    details[artist + ' ' + title] = data
  except:
    print artist, title
    return '1'

filename = sys.argv[1]

print filename
f = open(filename, 'r')

emotions = []
newsong = True
verse = ''
songnum = 0
for line in f:
    line = line.strip()
    if line.startswith('emotions:'):
        line = line.replace('emotions:', '')
        line = line.replace(' ', '')
        if newsong:
            song_emotions = line.split(',')
            emotions = []
            if weka:
              song = artist + ' ' + title
              categorizer.categorize(song, song_emotions)
        else:
            emotions = line.split(',')
    elif line.find('song:') >= 0:
        newsong = True
        emotions = []
        songnum += 1
        title = get_content(line)
        title.replace("\'", "")
    elif line.startswith('singer:') or line.startswith('band:'):
        artist = get_content(line)
    elif line == '' and verse: 
        if weka: continue
        emot = emotions or song_emotions
        is_test = (songnum % 10) == int(sys.argv[2])
        song = artist + ' ' + title
        categorizer.categorize(song, emot, verse, is_test)
        verse = ''
        emotions = []
    elif line:
        newsong = False
        verse += line.strip() + ' '

def save_details():
  details_file = open('details', 'a')
  json.dump(details, details_file)
  details_file.close()

#save_details()
