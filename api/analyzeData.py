from datetime import datetime
import json
import numpy as np
import pandas as pd
import math
import requests

"""Class for handling analyzing song & workout data.
"""
class analyzeData():
    def __init__(self):
      self.rankedSongs = None

    #from format 'YYYY-MM-DDTHH:MM:SSZ' to float timestamp
    def convertTimeStamp(self, timeStamp):
        # return(datetime.strptime(timeStamp, "%Y-%m-%dT%H:%M:%S.%f%z"))
        return(datetime.fromisoformat(timeStamp).timestamp())
        # ^this is what i originally had and need to figure outtt.

    def getSongs(self, songs):
        """get song data from json and format
        into pandas dataframe
        """
        # data = json.load(open("/Users/sarasyed/code/heartbeats/api/TestRecentMusic.json"))['items']
        data = songs
        songs = pd.DataFrame(columns=['Name', 'ID', 'Start', 'End', 'Score', 'ScoreLength', 'SongLength', 'Artist', 'ArtistId', 'Image'])
        
        songs['Name'] = [d['track']['name'] for d in data]
        songs['Artist'] = [d['track']['artists'][0]['name'] if len(d['track']['artists']) > 0 else "" for d in data]
        songs['Image'] = [d['track']['album']['images'][0]['url'] if (len(d['track']['album']) > 0 and len(d['track']['album']['images']) > 0) else "" for d in data]
        songs['ArtistId'] = [d['track']['artists'][0]['id'] if len(d['track']['artists']) > 0 else "" for d in data]
        songs['ID'] = [d['track']['id'] for d in data]
        songs['Start'] = [d['played_at'] for d in data] #need to convert to do convertTimeStamp
        songs['Start'] = songs['Start'].apply(lambda x : self.convertTimeStamp(x))
        songs['SongLength'] = [d['track']['duration_ms'] for d in data]
        songs['SongLength'] = songs['SongLength'].apply(lambda x : x/1000) #ms -> seconds to bc compatible w epoch time
        songs = songs.sort_values(by='Start', ascending=True)
        songs = songs.reset_index(drop=True)
        songs['temp'] = songs['Start'] #for calculating end.... start of next song
        songs['temp'] = songs['temp'].shift(-1)
        songs['temp'][len(songs.index)-1] = songs['Start'][len(songs.index)-1] + songs['SongLength'][len(songs.index)-1]#listened to whole song for last song
        songs['End'] = songs['Start'] + songs['SongLength']
        songs['End'] = songs[['End', 'temp']].min(axis=1)
        
        return(songs)

    def getSplits(self, data):
        """get splits data from json and format
        into pandas dataframe
        """
        # data = json.load( open( "/Users/sarasyed/code/heartbeats/api/TestRecentActivity.json") )
        # if 'splits_standard' not in data:
        #     return("No splits data for this activity") #think about how want to handle this

        splits = pd.json_normalize(data['splits_standard'])
        starts = []
        ends = []
        start = self.convertTimeStamp(data['start_date'])
        for split in data['splits_standard']:
            starts.append(start)
            ends.append(start + split['elapsed_time'])
            start += split['elapsed_time']
        splits['Start']= starts
        splits['End']=ends
        return(splits)

    def getSongScores(self, songs, splits):
        """calculate scores from song data
        and split data
        """
        #for each song
        for index, song in songs.iterrows():
            # overlappingSplits = select all rows of splits where songEnd > splitStart AND songStart < splitEnd
            overlappingSplits = splits[(splits['Start'] < song['End']) & (splits['End'] > song['Start'])]
            for splitIndex, split in overlappingSplits.iterrows():
                start = max(split['Start'], song['Start'])
                end = min(split['End'], song['End'])
                overlap = end - start
                if not math.isnan(songs['ScoreLength'][index]):
                    songs['Score'][index] = (songs['Score'][index] * songs['ScoreLength'][index] + split['average_grade_adjusted_speed'] * overlap)/ (songs['ScoreLength'][index]+overlap)
                    songs['ScoreLength'][index] = songs['ScoreLength'][index] + overlap

                else:
                    songs['Score'][index] = split['average_grade_adjusted_speed']
                    songs['ScoreLength'][index] = overlap

        return songs

    def calculateSongRankings(self, songs):
        #filtering, remove scores with Nan and songs with ScoreLength / SongLength < 1/2
        bestSongs = songs.where( (songs['Score'] > 0 ) & (songs['ScoreLength'] > (songs['SongLength']/2) ))
        bestSongs = bestSongs.dropna()

        #if listened to same song multiple times in workout, treated as different datapoints
        #now aggregating datapoints to create one score for that song by taking weighted average
        #of score by ScoreLength
        weightedSumMethod = lambda x: np.average(x, weights=bestSongs.loc[x.index, 'ScoreLength'])

        bestSongs = bestSongs.groupby(["Name", "Artist"]).agg(ScoreLength=('ScoreLength', 'sum'),
                        Score=('Score', weightedSumMethod))

        #sort, best to worst songs!
        bestSongs = bestSongs.sort_values(by=['Score', 'ScoreLength', 'Name', 'Artist'], ascending=[False, True, True, True])

        return(bestSongs)

    def enrichRankedSongs(self, rankedSongs, songData):
        rankedSongs = rankedSongs.drop(['ScoreLength', 'Score'], axis=1)
        rankings = rankedSongs.index.values #[(name, artist)]
        names = [r[0] for r in rankings]
        enrichedRankedData = songData[songData['Name'].isin(names)]
        #re-sort from best to worst
        enrichedRankedData['Name'] = pd.Categorical(enrichedRankedData['Name'], names)
        enrichedRankedData.sort_values(['Name'])
        return enrichedRankedData

    def formatRankedSongsForHTML(self, rankedSongs):
        colors = ["#cedad9", "#a1c2aa", "#9eb5b3", "#9ea6a2", "#9eb5a8", "#6e7a73", "#badbc6", "#5d807c", "#708c94", "#8999ab"]
        formattedData = rankedSongs.drop(['ID', 'Start', 'End', 'Score', 'ScoreLength', 'SongLength','ArtistId', 'temp'], axis=1)
        formattedData = formattedData.head(10) #cutdown to top 10 songs
        formattedData.insert(0, 'Ranking', range(1, 1 + len(formattedData)))
        formattedData.insert(0, 'BackgroundColor', colors[:len(formattedData)])
        dictionaries = formattedData.to_dict(orient='records')
        # jsonDict = json.dumps(dictionaries)
        return {"success":True, "songs":dictionaries}

    def setRankedSongs(self, rankedSongs):
        self.rankedSongs = rankedSongs

    def getRankedSongs(self):
        return self.rankedSongs
        
    def generateRecommendedPlaylist(self, rankedSongs, access_token):
        colors = ["#a1af9b", "#93a3a3", "#6f8e94", "#6d778a", '#6f7b94', "#8d8696", "#8c8c8c", "#6f8594", "#a093a3", "#a3939a"]
    
        num_rows = len(rankedSongs.index)
        if num_rows > 10:
            rankedSongs = rankedSongs.head(10) #cutdown to top 10 songs

        tracks = rankedSongs['ID'].tolist()

        url = "https://api.spotify.com/v1/recommendations?seed_tracks=" + tracks[0]
        for index, track in enumerate(tracks):
            if index != 0:
                url += "," + track

        response = requests.get(url, headers={"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer %s" % (access_token)})
        if response.status_code != 200:
            return {'success': False, "errorMessage" : "ERROR: Can't generate recommended playlist, " + response.reason}

        suggested_tracks = response.json()['tracks']

        playlist = pd.DataFrame(columns=['Name', 'Artist', 'Image'])
        playlist['Name'] = [d['name']for d in suggested_tracks]
        playlist['Artist'] = [d['artists'][0]['name'] if len(d['artists']) > 0 else "" for d in suggested_tracks]
        playlist['Image'] = [d['album']['images'][0]['url'] if (len(d['album']) > 0 and len(d['album']['images']) > 0) else "" for d in suggested_tracks]
        playlist = playlist[~playlist.Name.isin(rankedSongs.Name)]
        playlist.insert(0, 'Ranking', range(1, 1 + len(playlist)))
        playlist = playlist.head(len(tracks))
        playlist.insert(0, 'BackgroundColor', colors[:len(playlist)])
        dictionaries = playlist.to_dict(orient='records')
        return {"success":True, "songs":dictionaries}


# analyzeData = analyzeData()
# songs = analyzeData.getSongs("blah")
# # splits = analyzeData.getSplits()
# # songsScores = analyzeData.getSongScores(songs, splits)
# # rankedSongs = analyzeData.calculateSongRankings(songsScores)
# # rankedSongs = analyzeData.enrichRankedSongs(rankedSongs, songs)
# # htmlRankedSongs = analyzeData.formatRankedSongsForHTML(rankedSongs)
# # access_token = "AQDMyqZgXoWX_fvaV2fyzRw-vkchrlmJqXk_XHhH_l3ay7emQ2N2DH4I5IxZEldK2HoZw0tBAs-OVkMwAQUvX47dU8I3jUr2qbLGUQ6t0knOKb_WqMM4hZFtDOekL15nEJzEcTQ2AtsXlpXhfR9pct0Cbl4AKsK2qxOfA4r1RvplntG27KO2Ev5RI_Lc4TMRh6bXEi_3e-csXLmsaILDCkH9Br0J67L8"
# # recommendedSongs = analyzeData.generateRecommendedPlaylist(rankedSongs, access_token)
# recommendedSongs = analyzeData.generateRecommendedPlaylist("blah", "blah")