from __future__ import unicode_literals

#from django.db import models
import spotipy
import spotipy.util as util

''' Environment variables for use to authorize user requests
export SPOTIPY_CLIENT_ID='85c7a80b0ee84941a3325c9cf0195a29'
export SPOTIPY_CLIENT_SECRET='ee5c526f74574b2588c7fd5e340ddd2f'
export SPOTIPY_REDIRECT_URI='http://localhost:8080/callback'
'''

username = '1160377113'

# Get all playlists of a user to show as choices for the user
def getPlaylists(username):
    scope = 'playlist-read-private'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        results_playlists = sp.user_playlists(username)

        for playlist in results_playlists['items']:
            if playlist['owner']['id'] == username:
                print (playlist['name'])
                print
        return results_playlists  # ['name']['id']
    else:
        print ("Can't get token for", username)


# Get all tracks of a playlist for use in creating new playlists
def getTracks(playlist_id): #or playlist['id']
    scope = 'user-library-read'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        tracks = sp.user_playlist_tracks(username, playlist_id)
        return tracks['name']['id']
    else:
        print ("Can't get token for", username)

def getTrackFeatures(track_id):
    sp = spotipy.Spotify()
    features = sp.audio_features(track_id)

    return features

# The preferences chosen by the user for the new playlist
#def userPlaylistPreferences():


#def playListLength():

#def mergePlaylists():

# Create a new tracklist with a
def sortNewTrackList(tracks):
    for track in tracks:
        features = getTrackFeatures(track['id'])
        tracksToSort = features['id']['tempo']


    newTrackList = tracksToSort.sort(key='tempo', reverse=True) #True is descending
    return newTrackList


#username = '1160377113'
playlists = getPlaylists(username)

for playlist in playlists['items']:
    tracks = getTracks(playlist['id'])
    for track in tracks:
        print (track)