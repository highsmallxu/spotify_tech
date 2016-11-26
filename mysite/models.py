from __future__ import unicode_literals

#from django.db import models
import spotipy
import spotipy.util as util
import json
import numpy as np

#Environment variables to use for authorizing user requests
# export SPOTIPY_CLIENT_ID='85c7a80b0ee84941a3325c9cf0195a29'
# export SPOTIPY_CLIENT_SECRET='ee5c526f74574b2588c7fd5e340ddd2f'
# export SPOTIPY_REDIRECT_URI='http://localhost:8080/callback'

username = '1160377113'
relevant_features = ['tempo']

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
    scope = 'playlist-read-private'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.user_playlist_tracks(username, playlist_id)
        tracks = results['items']
        return tracks
    else:
        print ("Can't get token for", username)

def getTrackFeatures(track_id):
    scope = 'playlist-read-private'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        features = sp.audio_features([track_id])
        return features[0]
    else:
        print ("Can't get token for", username)

# The preferences chosen by the user for the new playlist
#def userPlaylistPreferences():


#def playListLength():

#def mergePlaylists():

# Create a new tracklist with a track
def sortTrackList(tracks):
    #print(tracks)
    track_ids = []
    track_tempo =[]

    for track in tracks:
        features = getTrackFeatures(track['track']['id'])
        track_ids.append(features['id'])
        track_tempo.append(features['tempo'])
        #json_tracks.append({'id': id, 'tempo': tempo})
    indices = np.argsort(track_tempo)
    return [np.asarray(track_ids)[indices], np.asarray(track_tempo)[indices]] #newTrackList = json.loads(newTracks).sort(key='tempo', reverse=True) #True is descending


# playlists = getPlaylists(username)
#
# for playlist in playlists['items']:
#     if playlist['owner']['id'] == username:
#         print("Getting tracks")
#         tracks = getTracks(playlist['id'])
# #        for track in tracks:
# #          print (track['track']['name'])
#         print("Sorting tracks")
#         newTracks_ids, newTracks_tempos = sortTrackList(tracks)
#         print ("SORTED")
#         print (len(newTracks_ids))
#         #print (newTracks_ids, newTracks_tempos)