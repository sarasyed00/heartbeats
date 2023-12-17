import requests
import webbrowser
import Tokens
import time
from datetime import datetime

"""Class for handling calls to Strava Api. 
Includes authentication & gathering latest workouts.
"""
class Strava():

    def __init__(self):
      self.stravaAuthCode = None

    def getAuthCodeRoute(self):
       url = "http://www.strava.com/oauth/authorize?client_id="
       url += str(Tokens.STRAVA_APP_CLIENT_ID)
       url += "&response_type=code&redirect_uri="
       url += "http://127.0.0.1:5000/stravaAuthenticate"
       url += "&approval_prompt=force&scope=activity:read_all,activity:write"
       r = webbrowser.open(url, new = 0)

    def setAuthCode(self, code):
      self.stravaAuthCode = code

    def getAuthCode(self):
      return self.stravaAuthCode

    # helper function to parse date into beautified string
    def parseDate(self, timeStamp):
      monthMap = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
      dateTime = datetime.fromisoformat(timeStamp)
      return monthMap[dateTime.month]+" "+str(dateTime.day)+", "+str(dateTime.year)

    #helper function to convert distance (meters) -> miles
    def parseDistance(self, distance):
      distance = distance / 1609
      return "{:.2f} miles".format(distance)

    # helper function to convert time in seconds to readable time in hours, mins, secs
    def parseTimeInSeconds(self, time):
      minutes, seconds = divmod(time, 60)
      hours, minutes = divmod(minutes, 60)
      return '{:d}hrs {:02d}mins {:02d}secs'.format(hours, minutes, seconds)



    # Api Call to get most recent workout. Returns boolean indicating success.
    def getLatestWorkout(self, code):
        token = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                       data={'client_id': Tokens.STRAVA_APP_CLIENT_ID,
                             'client_secret': Tokens.STRAVA_APP_CLIENT_SECRET,
                             'code': code,
                             'grant_type': 'authorization_code'})

        if token.status_code != 200:
          return False
        #Save json response as a variable
        strava_token = token.json()

        access_token = strava_token[ 'access_token' ]
        activities_url = f"https://www.strava.com/api/v3/athlete/activities?" \
          f"access_token={access_token}"

        athlete_activities = requests.get(activities_url)

        #need to handle supported activities.... run vs bike?'
        if athlete_activities.status_code == 200 and len(athlete_activities.json()) > 0:
          response = requests.get("https://www.strava.com/api/v3/activities/" + str(athlete_activities.json()[0]['id']), headers={"Authorization" : "Bearer %s" %(strava_token[ 'access_token' ])})
          
          if response.json()['type'] != "Run":
            return {"success" : False, "message": "Unsupported activity type. Only support Runs"}
          
          # will need to format these properly
          Date = response.json()['start_date']
          Date = self.parseDate(Date)
          Distance = response.json()['distance']
          Distance = self.parseDistance(Distance)
          Time = response.json()['moving_time']
          Time = self.parseTimeInSeconds(Time)

          text_file = open( "TestRecentActivity.json", "w")
          text_file.write( response.text)
          text_file.close()
          return {"success" : True, "date" : Date, "activeTime" : Time, "distance" : Distance}
        else:
          return {"success" : False}
