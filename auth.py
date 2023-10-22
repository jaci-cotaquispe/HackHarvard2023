from datetime import datetime, timedelta
import json
import requests
from flask import Flask, redirect, request, jsonify, session
import os
from dotenv import load_dotenv
import urllib.parse
from hackHarvardJJM import*

app = Flask(__name__)
app.secret_key = "random stuff?"

client_id = "172864bf1c9c486fa39955b6dafc90c0"
client_secret = "1966d7082df54d74a5e7cbafca56b805"
redirect_uri = "http://localhost:5000/callback"

auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
api_base_url = "https://api.spotify.com/v1/"

@app.route('/')
def index():
    return "Welcome to my Spotify app <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        'show_dialog': True #delete later!!!
    }
    
    auth_url = "https://accounts.spotify.com/authorize"
    auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(token_url, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/get-userID')

@app.route('/get-userID')
def get_userID():

    headers = {
        'Authorization': f"Bearer {session['access_token']}"        
    }
    response = requests.get(api_base_url + "me", headers=headers)

    user = response.json()
    session['userID'] = user['id']

    return redirect('/make_playlist')

@app.route('/make_playlist')
def make_playlist(): 
    headers = {
        'Authorization': f"Bearer {session['access_token']}",
        'Content-Type': 'application/json'       
    }
    testName = session['book']
    req_body = {
        "name": testName,
        "description": f"The perfect soundtrack for reading {testName}, courtesy of Orpheus.",
        "public": False
    }

    playlistURL = api_base_url + "users/" + session['userID'] + "/playlists"

    response = requests.post(playlistURL, headers=headers, data=json.dumps(req_body))
    playlist = response.json()
    session['playlistID'] = playlist['id']

    return redirect('/get_songs')

@app.route('/get_songs')
def get_songs(): 
    
    session['book'] = "romeo_and_juliet" #TEMP
    miraya_values = get_energy_positivity_score(session['book'])

    #check for missing token
    if 'access_token' not in session:
        return redirect('/login')
    
    #check for expiration
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"        
    }
   
    query = f"?limit=100&seed_genres=classical&target_valence={miraya_values}"
    query_url = api_base_url + 'recommendations' + query

    response = requests.get(query_url, headers=headers)
    result = response.json()

    tracklist = []
    for track in result['tracks']:
        tracklist.append(track['uri'])
    session['songs'] = tracklist
    
    return redirect('/add_songs')

@app.route('/add_songs')
def add_songs():
    headers = {
        'Authorization': f"Bearer {session['access_token']}",
        'Content-Type': 'application/json'       
    }
    req_body = {
        "uris": session['songs'],
        "position": 0
    }
    addURL = api_base_url + "playlists/" + session['playlistID'] + "/tracks"
    response = requests.post(addURL, headers=headers, data=json.dumps(req_body))
    result = response.json()

    return jsonify(result)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    #making sure refresh is necessary
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(token_url, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    
        return redirect('/playlists')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)