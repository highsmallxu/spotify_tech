from django.http import HttpResponse
import sys
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2

scope = 'user-library-read'
client_id = "85c7a80b0ee84941a3325c9cf0195a29"
client_secret = "ee5c526f74574b2588c7fd5e340ddd2f"
redirect_uri = "http://localhost:8080/callback"

# if len(sys.argv) > 1:
username = "julhien"
# else:
#     print "Usage: %s username" % (sys.argv[0],)
#     sys.exit()

token = util.prompt_for_user_token(username, scope)
auth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, state=None, scope=scope, cache_path=None)

def home(request):
    # Create links and OpenID form to the Login handler.
    return HttpResponse('<a href=%s>Login</a>.<br />' % auth.get_authorize_url())

def callback(request,code):
    auth.get_access_token(request.GET["code"])
    if token:
        sp = spotipy.Spotify(auth=token)

        results = sp.user_playlists(sp.current_user()['id'], limit=50)
        a=""
        for item in results['items']:
            track = item['name']
            a += (track+" \n " )
        return HttpResponse(a)
    else:
        print("Can't get token for", username)

# example/simple/views.py
