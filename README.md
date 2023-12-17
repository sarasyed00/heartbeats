# How to start:

Open two terminals.
In one terminal run "npm start" to start react app for frontend side.
In the second terminal, run "npm run start-api" to start flask app for backend logic.

# Overview:

- This application allows users to connect to their Strava and Spotify accounts to analyze their most recent workout and the music they listened to during it. We will display a ranked list, of the user's top five songs they listened to during their last workout, ranked form the song that led to the highest output during their workout. These tops songs are then used to generate a playlist of new songs they may enjoy for their next workout.

# Design Decisions:

- Flask backend, react frontend
- Object oriented design approach enables easy scalability to expand beyond Strava as the fitness data source and Spotify as the music data source. Could easily create Nike, Peloton objects to gather data from should they offer apis.

# Next Steps:

- Have song titles link to spotify urls of the track
- Support analysis of bike workouts
- Improve frontend messaging on errors
