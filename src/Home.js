import React, { useEffect, useState, useRef } from 'react';
import { Activity } from "./Activity";
import {Overview} from "./Overview";
import { Song } from "./Song";
import Button from 'react-bootstrap/Button';



export default function Home() {
    const isMounted = useRef(false);
    const [stravaAuthCode, setStravaAuthCode] = useState("")
    const [activity, setActivity] = useState([])

    const [spotifyAuthCode, setSpotifyAuthCode] = useState("")

    // const [topPlayedSongs, setTopPlayedSongs] = useState([{'Ranking': 1, 'Name': 'Waves', 'Artist': 'Kanye West', 'Image': 'https://i.scdn.co/image/ab67616d0000b2732a7db835b912dc5014bd37f4', 'BackgroundColor': '#b9c9a2'},
    // {'Ranking': 1, 'Name': 'Waves', 'Artist': 'Kanye West', 'Image': 'https://i.scdn.co/image/ab67616d0000b2732a7db835b912dc5014bd37f4', 'BackgroundColor': '#b9c9a2'},
    // {'Ranking': 1, 'Name': 'Waves', 'Artist': 'Miley Cyrus', 'Image': 'https://i.scdn.co/image/ab67616d0000b2732a7db835b912dc5014bd37f4', 'BackgroundColor': '#9eb5b3'}])
    const [topPlayedSongs, setTopPlayedSongs] = useState([])
    
    const [recommendedSongs, setRecommendedSongs] = useState([])

    useEffect(() => {
        if (isMounted.current){
            fetch('/getRecommendedPlaylist').then(res => res.json()).then(data => {
                if (data.success === true){
                    setRecommendedSongs(data.songs)
                }
            })
        }
    }, [topPlayedSongs])

    function querySpotifyAuthCode(retries){
        fetch('/spotifyAuthenticate').then(res => res.json()).then(data => {
            if (data.success === true){
                setSpotifyAuthCode(data.code)
            } else {
                if (retries > 0){ //wait 5 seconds and try again
                    setTimeout(function() {
                        querySpotifyAuthCode(retries-1);
                      }, 5000);
                } //want to add an else & say never logged in!
            }
        })
    }

    useEffect(() => {
        if (isMounted.current){
            querySpotifyAuthCode(5) 
        }
    }, [activity])

    useEffect(() => {
        if (isMounted.current){
            fetch('/spotifyRankedSongs?code='.concat(spotifyAuthCode)).then(res => res.json()).then(data => {
                if (data.success === true){
                    setTopPlayedSongs(data.songs)
                }
            })
        }
    }, [spotifyAuthCode])

    function queryStravaAuthCode(retries){
        fetch('/stravaAuthenticate').then(res => res.json()).then(data => {
            if (data.success === true){
                setStravaAuthCode(data.code)
            } else {
                if (retries > 0){ //wait 5 seconds and try again
                    setTimeout(function() {
                        queryStravaAuthCode(retries-1);
                      }, 5000);
                } //want to add an else & say never logged in!
            }
        })
    }

    function stravaAuthenticate(){
        queryStravaAuthCode(5) 
    };

    useEffect(() => {
        if (isMounted.current){
            fetch('/stravaWorkout?code='.concat(stravaAuthCode)).then(res => res.json()).then(data => {
                if (data.success === true){
                    setActivity(activity => {
                        return [
                          ...activity,
                          { date: data.date, distance: data.distance, activeTime: data.activeTime },
                        ]
                      })
                }
            })
        }
        else {
            isMounted.current= true
        }
    }, [stravaAuthCode])

    return(
        <>
            <div className= "flex-container">
                <div className="Stats equal-container">
                    {activity.map(item => <Activity activeTime={item.activeTime} distance={item.distance} date={item.date}/>)}
                    <p> </p>
                </div>
                <div className="Intro large-container">
                    <Overview/>
                    <Button variant="outline-info" onClick={e => stravaAuthenticate()}>Analyze my most recent workout</Button>
                </div>
                <div className = "Blankspace equal-container">

                </div>

            </div>
            <div className= "flex-container top-padding ">

                <div className="Played Songs song-container">
                    <h>{(topPlayedSongs.length > 0) && ("Your top songs:")}</h>
                    <p>{(topPlayedSongs.length > 0) && ("Ranked in order of output during your last workout")}</p>
                    {topPlayedSongs.map(item => <div className="list-padding"><Song key={item.Ranking} ranking={item.Ranking} name={item.Name} artist={item.Artist} image={item.Image} backgroundColor={item.BackgroundColor}/></div>)}
                </div>
                <div className="Recommended Playlist song-container">
                    <h>{(recommendedSongs.length > 0) && ("Your recommended playlist:")}</h>
                    <p>{(recommendedSongs.length > 0) && ("Based on songs we think will help you generate the highest output during your next workout")}</p>
                    {recommendedSongs.map(item => <div className="list-padding"><Song key={item.Ranking} ranking={item.Ranking} name={item.Name} artist={item.Artist} image={item.Image} backgroundColor={item.BackgroundColor}/></div>)}
                </div>
            </div>
        </>
    );
}