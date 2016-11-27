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
scope = 'playlist-modify-public playlist-modify-private user-library-read playlist-read-private'



# Get all playlists of a user to show as choices for the user
def getPlaylists(username):
    # scope = 'playlist-read-private'

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
    # scope = 'playlist-read-private'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.user_playlist_tracks(username, playlist_id)
        tracks = results['items']
        return tracks
    else:
        print ("Can't get token for", username)

def getTrackFeatures(track_id):
    #print('Track ID:' + track_id)
    # scope = 'playlist-read-private'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        #if track_id is None:
        #    print (track_id)
        features = sp.audio_features([track_id])
        #if features[0]:
        #    print (features[0])
        return features[0]
    else:
        print ("Can't get token for", username)

# The preferences chosen by the user for the new playlist
#def userPlaylistPreferences():


#def playListLength():

#def mergePlaylists():


def getRecommendedTrack(tracks, tempo_limit_1, tempo_limit_2):
    # scope = 'user-library-read'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)

    recommendation = sp.recommendations(seed_tracks=tracks.tolist(), limit=1, min_tempo=min(tempo_limit_1,tempo_limit_2), max_tempo = max(tempo_limit_1,tempo_limit_2))
    if len(recommendation['tracks'])==0:
        recommendation = sp.recommendations(seed_tracks=tracks.tolist(), limit=1,
                                            min_tempo=min(tempo_limit_1, tempo_limit_2)-5,
                                            max_tempo=max(tempo_limit_1, tempo_limit_2)+5)

    return recommendation['tracks'][0]

##TODO: HANDLE SCALE LIMITS AND GAPS IMPOSSIBLE TO FILL
def extendTrackList(sorted_ids, sorted_tempos, add_limit):
    #Takes tracks ids and the distance
    added_time = 0
    while added_time<add_limit:
        # print(added_time)
        derivatives = [sorted_tempos[k+1]-sorted_tempos[k] for k in range(len(sorted_tempos)-1)]
        print(len(sorted_tempos))
        indices = np.argsort(derivatives)
        recommendation = getRecommendedTrack(sorted_ids[range(min(0,indices[0]-2),max(len(sorted_ids),indices[0]+3))], sorted_tempos[indices[0]],sorted_tempos[indices[0]+1])
        sorted_ids = sorted_ids.tolist()
        sorted_ids.insert(indices[0]+1,recommendation['id'])
        sorted_ids = np.asarray(sorted_ids)
        sorted_tempos = sorted_tempos.tolist()
        sorted_tempos.insert(indices[0] + 1, getTrackFeatures(recommendation['id'])['tempo'])
        sorted_tempos = np.asarray(sorted_tempos)

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
    #Where we store the track features
    track_features = []
    for track in tracks:
        if track['track']['id'] is None:
            continue
        features = getTrackFeatures(track['track']['id'])
        if features["energy"] is None or features["danceability"] is None :
            continue
        track_features.append([features['id'], features['tempo'], 160*features['danceability'], 160*features['energy']])
        # json_tracks.append({'id': id, 'tempo': tempo})

    track_features = np.asarray(track_features)
    print("SIZE BEFORE SORT")
    print(track_features.shape)
    # print(track_features)
    indices = np.argsort(track_features[:,1:2])
    track_tempo = np.asarray(track_features)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(track_features[:,1:3])

    # print(kmeans.cluster_centers_)
    # print(kmeans.labels_)

    labels  = kmeans.labels_
    cluster_centers = np.asarray([[cluster[0], cluster[1], np.sqrt(cluster[0]**2+cluster[1]**2)] for cluster in kmeans.cluster_centers_])
    #sorting the clusters
    # print(cluster_centers.shape)
    # print(kmeans.cluster_centers_.shape)
    cluster_indices = np.argsort(cluster_centers[:, 2])


    #our final ordered list
    final_list=[]
    for label in cluster_indices:
        # print("CLUSTER " + str(label))
        #intremediate sorting in the clusters
        track_features = np.asarray([track_features[i,:] for i in range(len(track_features)) if labels[i] == label])
        if track_features.shape == (0,):
            continue
        sorted_indices = np.argsort(track_features[:,1].astype(float))
        track_features = track_features[sorted_indices]

        final_list.append(track_features)



    final_features = np.concatenate(final_list)
    print("SIZE BEFORE SORT")
    print(final_features.shape)


    # print(final_features)
    # print(final_features[:,1].astype(float))
    # return [final_features[:,0], final_features[:,1].astype(float)]  # newTrackList = json.loads(newTracks).sort(key='tempo', reverse=True) #True is descending




def sortTrackList(tracks):
    #print(tracks)
    track_ids = []
    track_tempo =[]

    for track in tracks:
        #print(track['track']['name'])
        if track['track']['id'] is None:
            continue
        features = getTrackFeatures(track['track']['id'])
        #print (features)
        track_ids.append(features['id'])
        track_tempo.append(features['tempo'])
        #json_tracks.append({'id': id, 'tempo': tempo})
    indices = np.argsort(track_tempo)
    return [np.asarray(track_ids)[indices], np.asarray(track_tempo)[indices]] #newTrackList = json.loads(newTracks).sort(key='tempo', reverse=True) #True is descending

def updatePlaylist(playlist, playlistLen):
    if playlist['owner']['id'] == username:
        tracks = getTracks(playlist['id'])
        #length = playlistLength(tracks)
        newTracks_ids, newTracks_tempos = sortTrackList(tracks)
        # clusterSortTrackList(tracks)
        smoothifiedTrackListIDs = extendTrackList(newTracks_ids, newTracks_tempos, playlistLen)
        #return
        createPlaylist(playlist['name'], smoothifiedTrackListIDs)

def createPlaylist(playlistName, track_ids):
    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        playlistNameNew = 'Smoothified ' + playlistName
        newPlaylist = sp.user_playlist_create(username, playlistNameNew, public=True)
        newTracklist = sp.user_playlist_add_tracks(username, newPlaylist['id'], track_ids)
        return [newPlaylist, newTracklist]
    else:
        print("Can't get token for", username)

def playlistLength(tracks):
    length = 0

    for track in tracks:
        if track['track']['id'] is None:
            continue
        length = length + int (track['track']['duration_ms'])
    return length

playlists = getPlaylists(username)
i=0
for playlist in playlists['items']:
    i += 1
    if i<2:
        continue

    if playlist['owner']['id'] == username:
        updatePlaylist(playlist, 3*10**6)
#         print("Getting tracks")
#         print(playlist)
#         tracks = getTracks(playlist['id'])
# #        for track in tracks:
# #          print (track['track']['name'])
#         print("Sorting tracks")
#         # newTracks_ids, newTracks_tempos = sortTrackList(tracks)
#
#         # newTracks_ids, newTracks_tempos = clusterSortTrackList(tracks)
#         print ("SORTED")
#         print("START EXTENSION")
#         # extended_track_list = extendTrackList(newTracks_ids,newTracks_tempos, 10**7)
#         print("EXTENDED")
#         # print (len(newTracks_ids))
#         #print (newTracks_ids, newTracks_tempos)
        break