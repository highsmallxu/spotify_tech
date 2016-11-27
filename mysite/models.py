from __future__ import unicode_literals

#from django.db import models
import spotipy
import spotipy.util as util
import json
import numpy as np
from sklearn.cluster import KMeans


#Environment variables to use for authorizing user requests
# export SPOTIPY_CLIENT_ID='85c7a80b0ee84941a3325c9cf0195a29'
# export SPOTIPY_CLIENT_SECRET='ee5c526f74574b2588c7fd5e340ddd2f'
# export SPOTIPY_REDIRECT_URI='http://localhost:8080/callback'


username = 'julhien'
relevant_features = ['tempo']

# Get all playlists of a user to show as choices for the user
def getPlaylists(username):
    scope = 'playlist-read-private'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        username = sp.me()["id"]
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
        #if track_id is None:
        #    print (track_id)
        features = sp.audio_features([track_id])
        if features == None:
            print(track_id)
        #if features[0]:
        #    print (features[0])
        return features[0]
    else:
        print ("Can't get token for", username)
# The preferences chosen by the user for the new playlist
#def userPlaylistPreferences():


#def playListLength():

#def mergePlaylists():


def getRecommendedTrack(tracks, tempo_min, tempo_max):
    scope = 'user-library-read'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)

    recommendation = sp.recommendations(seed_tracks=tracks, limit=1, min_tempo=tempo_min, max_tempo = tempo_max)
    return recommendation[0]

##TODO: HANDLE SCALE LIMITS AND GAPS IMPOSSIBLE TO FILL
def extendTrackList(sorted_ids, sorted_tempos, add_limit):
    #Takes tracks ids and the distance
    added_time = 0
    while added_time<add_limit:
        derivatives = [sorted_tempos[k+1]-sorted_tempos[k] for k in range(sorted_tempos-1)]
        indices = np.argsort(derivatives)
        recommendation = getRecommendedTrack(sorted_ids[range(min(0,indices[0]-2),max(len(sorted_ids),indices[0]+3))], sorted_tempos[indices[0]],sorted_tempos[indices[0]+1])
        sorted_ids.insert(indices[0]+1,recommendation['id'])
        sorted_tempos.insert(indices[0] + 1, recommendation['id'])
        added_time += recommendation['duration_ms']

    return sorted_ids

# def cutList(sorted_ids, sorted_tempos, add_limit, min_tempo_scale, max_tempo_scale):
#     added_time = 0
#     while added_time > add_limit:
#         derivatives = [sorted_tempos[k + 1] - sorted_tempos[k] for k in range(sorted_tempos - 1)]
#         indices = np.argsort(derivatives)
#         recommendation = getRecommendedTrack(
#             sorted_ids[range(min(0, indices[0] - 2), max(len(sorted_ids), indices[0] + 3))], sorted_tempos[indices[0]],
#             sorted_tempos[indices[0] + 1])
#         sorted_ids.insert(indices[0] + 1, recommendation['id'])
#         sorted_tempos.insert(indices[0] + 1, recommendation['id'])
#         added_time += recommendation['duration_ms']
#
#     return sorted_ids


def clusterSortTrackList(tracks):
    # print(tracks)
    track_ids = []
    track_tempo = []
    track_features = []
    for track in tracks:
        features = getTrackFeatures(track['track']['id'])
        track_ids.append(features['id'])
        track_tempo.append(features['tempo'])
        track_features.append([160*features['danceability'], 160*features['energy']])
        # json_tracks.append({'id': id, 'tempo': tempo})
    indices = np.argsort(track_features)
    track_tempo = np.asarray(track_features)
    kmeans = KMeans(n_clusters=4, random_state=0).fit(track_features)

    print(kmeans.cluster_centers_)
    print(kmeans.labels_)

    return [np.asarray(track_ids)[indices], np.asarray(track_tempo)[
        indices]]  # newTrackList = json.loads(newTracks).sort(key='tempo', reverse=True) #True is descending




def sortTrackList(tracks):
    #print(tracks)
    track_ids = []
    track_tempo =[]

    for track in tracks:
        # print(track['track']['name'])
        features = getTrackFeatures(track['track']['id'])
        #print (features)
        track_ids.append(features['id'])
        track_tempo.append(features['tempo'])
        #json_tracks.append({'id': id, 'tempo': tempo})
    indices = np.argsort(track_tempo)
    return [np.asarray(track_ids)[indices], np.asarray(track_tempo)[indices]] #newTrackList = json.loads(newTracks).sort(key='tempo', reverse=True) #True is descending


playlists = getPlaylists(username)

for playlist in playlists['items']:
    if playlist['owner']['id'] == username:
        print("Getting tracks")
        tracks = getTracks(playlist['id'])
#        for track in tracks:
#          print (track['track']['name'])
        print("Sorting tracks")
        newTracks_ids, newTracks_tempos = sortTrackList(tracks)
        # clusterSortTrackList(tracks)
        print ("SORTED")
        # print (len(newTracks_ids))
        #print (newTracks_ids, newTracks_tempos)