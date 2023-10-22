from datetime import datetime, timedelta
import requests
from flask import Flask, redirect, request, jsonify, session
import os
from dotenv import load_dotenv
import urllib.parse

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
    scope = 'user-read-private user-read-email'

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

        return redirect('/get_songs')
    
""" @app.route('/playlists')
def get_playlists():
    #check for missing token
    if 'access_token' not in session:
        return redirect('/login')
    
    #check for expiration
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"        
    }

    response = requests.get(api_base_url + 'me/playlists', headers=headers)
    playlists = response.json()

    return jsonify(playlists) """

@app.route('/get_songs')
def get_songs(): #param = valence
    #check for missing token
    if 'access_token' not in session:
        return redirect('/login')
    
    #check for expiration
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"        
    }
    
    #TEMP
    miraya_values = 0.7
   
    query = f"?limit=100&seed_genres=classical&target_valence={miraya_values}"
    query_url = api_base_url + 'recommendations' + query

    response = requests.get(query_url, headers=headers)
    
    session['songs'] = response['tracks']

    return redirect('/make_playlist')

@app.route('/make_playlist')
def make_playlist(): #params = name of book
    testName = "slayidk"
    req_body = {
        "name": testName,
        "description": f"The perfect soundtrack for reading {testName}, courtesy of Orpheus."
    }


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