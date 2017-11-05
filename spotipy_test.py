import spotipy_api
from PyLyrics import *
import spotipy
import numpy as np
import random
import time
from spotipy.oauth2 import SpotifyClientCredentials

genreSet = {('pop',0),('country',1),('rock',2),('rap',3)}

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

artistSet = {}
for genre,k in genreSet:
	query = sp.search(q='genre:' + genre, type='artist',limit=10)
	artistSet[genre] = [x['name'] for x in query['artists']['items']]
print "Artists are:"
print artistSet

def myGetTracks(album):
	url = "http://lyrics.wikia.com/api.php?action=lyrics&artist={0}&fmt=xml".format(album.artist())
	soup = BeautifulSoup(requests.get(url).text,"xml")
	for al in soup.find_all('album'):
		currentAlbum = al
		if al.text.lower().strip() == album.name.strip().lower():
			break
	songs =[Track(song.text,album,album.artist()) for song in currentAlbum.findNext('songs').findAll('item')]
	return songs

for artist in artistSet[genre]:
	print "~~~~~~~~~~~~~~~~~~~~"
	print artist
	print "~~~~~~~~~~~~~~~~~~~~"
	try:
		albums = PyLyrics.getAlbums(artist)
	except UnicodeEncodeError:
		print "Artist has illegal character"
		continue
	except ValueError:
		print "Artist not in wikia lyrics!"
		continue
	for album in albums:
		print "------------"
		print album
		print "------------"
		songs = myGetTracks(album)
		for song in songs:
			print song
			print song.artist, song.name
			print type(song)
			try:
				lyrics = PyLyrics.getLyrics(song.artist,song.name)
			except ValueError:
				print "Song not in wikia lyrics!"
				continue
			#print lyrics