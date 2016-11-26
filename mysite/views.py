from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
import sys
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2

scope = 'user-read-private user-top-read'
client_id = "85c7a80b0ee84941a3325c9cf0195a29"
client_secret = "ee5c526f74574b2588c7fd5e340ddd2f"
redirect_uri = "http://localhost:8080/callback"

# if len(sys.argv) > 1:
# else:
#     print "Usage: %s username" % (sys.argv[0],)
#     sys.exit()



token=""
auth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, state=None, scope=scope, cache_path=None)

def home(request):
    # Create links and OpenID form to the Login handler.
    if token=="":
        return HttpResponse('<a href=%s>Login</a>.<br />' % auth.get_authorize_url())
    else:
        sp = spotipy.Spotify(auth=token, requests_session=True)
        results = sp.current_user_top_tracks(limit=50)
        a = ""
        for item in results['items']:
            track = item['name']
            a += (track + " \n ")
        return HttpResponse(a)

def callback(request, code):
    # return HttpResponse(auth.client_id)
    global token
    token = auth.get_access_token(request.GET["code"])["access_token"]
    # return HttpResponse(token)
    return redirect('index')

    # if token:
    #     sp = spotipy.Spotify(auth=token, requests_session=True)
    #     results = sp.current_user_top_tracks(limit=50)
    #     a=""
    #     for item in results['items']:
    #         track = item['name']
    #         a += (track+" \n " )
    #     return HttpResponse(a)
    # else:
    #     print("Can't get token for", username)

# example/simple/views.py
