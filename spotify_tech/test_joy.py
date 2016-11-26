import spotipy
name="Kanye West"
spotify = spotipy.Spotify()
results = spotify.search(q='artist:' + name, type='artist')
print (results)