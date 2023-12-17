# Overview:

- This application connects user's Strava and Spotify accounts to analyze their most recent workout and the music they listened to during it. We rank the songs the user listened to during their last workout based on the amount of output they produced while listneing to it. For outdoor run workouts, this output takes into consideration both user's running speed and incline. These tops songs are then used to generate a playlist of new songs that we believe will encourage high output for their next workout.
- Video demo of the application: https://github.com/sarasyed00/heartbeats/assets/61920970/11da2886-f4e4-4365-925a-3671a909d561


# How to run:

Open two terminals.
In one terminal run "npm start" to start react app for frontend side.
In the second terminal, run "npm run start-api" to start flask app for backend logic.

# Design Decisions:

- Flask backend, react frontend
  - I decided to use Flask for the backend because of its ability to easily connect Python to web applications. I knew I wanted users to be able to interact with this app from a clean and simple webpage. Give the goal of the application to provide data anlytics, I wanted the backend to be in Python to be able to leverage the numerous python packages (pandas, numpy) that would be useful for data analysis. I also had never used Flask before, so I thought this would be a great opportunity to explore using it!
  - Later in the project, I decided to connect the flask application to a react frontend. A lot of what I wanted to display on the UI, I knew could be easily acheived using React to create a clean user experience. For example, I was able to leverage reusable components to displaying the ranked & recommended songs.
- I incorporated some aspects of object oriented design, by creating separate Spotify and Strava classes. Currently, there were few publically available APIs that provided the data necessary for the anlaysis I wanted to acheive, but in the future this design approach enables easy scalability to expand beyond Strava as the fitness data source and Spotify as the music data source. For example, I could easily create and instantiate Nike, Peloton objects to gather data should they offer apis.

# Next Steps:

- Have song titles link to the spotify urls of the track
- Add link to generated playlist on Spotify
- Support analysis of bike workouts
- Handle connecting to Strava & Spotify Apis in same tab
