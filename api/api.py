from flask import Flask,jsonify,url_for,request,render_template,session
from logging import FileHandler,WARNING


app = Flask(__name__)
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
from Strava import Strava
from Spotify import Spotify
from analyzeData import analyzeData

Strava = Strava()
Spotify = Spotify()
analyzeData = analyzeData()

@app.route('/stravaAuthenticate', methods = ['GET'])
def stravaAuthentication():
    if request.method == "GET":
        code = request.args.get('code', None)
        if code is not None:
            Strava.setAuthCode(code)
            return "Please return to original page"
        else:
            code = Strava.getAuthCode()
            if code is not None:
                return {"success": True, "code": code}
            Strava.getAuthCodeRoute()
            return {"success": False}

@app.route('/stravaWorkout', methods = ['GET'])
def stravaWorkout():
    code = request.args.get('code', None) #expecting strava auth code to be passed
    if code is not None:
        return Strava.getLatestWorkout(code)

@app.route('/spotifyAuthenticate', methods = ['GET'])
def spotifyAuthentication():
    if request.method == "GET":
        code = request.args.get('code', None)
        if code is not None:
            Spotify.setAuthCode(code)
            return "Please return to original page"
        else:
            code = Spotify.getAuthCode()
            if code is not None:
                return {"success": True, "code": code}
            Spotify.getAuthCodeRoute()
            return {"success": False}

@app.route('/spotifyRankedSongs', methods = ['GET'])
def getRankedSongs():
    # return { "success": True,
    #     "songs": [{'Ranking': 1, 'Name': 'Waves', 'Artist': 'Kanye West', 'Image': 'https://i.scdn.co/image/ab67616d0000b2732a7db835b912dc5014bd37f4'},
    # {'Ranking': 1, 'Name': 'Waves', 'Artist': 'Kanye West', 'Image': 'https://i.scdn.co/image/ab67616d0000b2732a7db835b912dc5014bd37f4'}]}
    if request.method == "GET":
        code = request.args.get('code', None)
        if code is not None:
            songs = Spotify.getLatestMusic(code)
            songs = analyzeData.getSongs(songs)
            splits = Strava.getSavedWorkout()
            if splits is None:
                return {"success":False}
            splits = analyzeData.getSplits(splits)
            songsScores = analyzeData.getSongScores(songs, splits)
            rankedSongs = analyzeData.calculateSongRankings(songsScores)
            rankedSongs = analyzeData.enrichRankedSongs(rankedSongs, songs)
            analyzeData.setRankedSongs(rankedSongs)
            htmlRankedSongs = analyzeData.formatRankedSongsForHTML(rankedSongs)
            return htmlRankedSongs


@app.route('/getRecommendedPlaylist', methods = ['GET'])
def getRecommendedPlaylist():
    rankedSongs = analyzeData.getRankedSongs()
    if rankedSongs is not None:
        access_token = Spotify.getAuthToken()
        return analyzeData.generateRecommendedPlaylist(rankedSongs, access_token)
    return {"success":False, "errorMessage": "Can't find rankedSongs"}