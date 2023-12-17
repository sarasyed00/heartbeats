import React from 'react';
import { PiHeartbeat, PiHeadphones } from "react-icons/pi";

export function Overview({}) {
    return (
    <>
        <p>By connecting to Strava and Spotify apis, we will analyze your most recent workout to provide analytics on which listening preferences lead to your highest workout outputs. 
            Given limitations on the data we can collect, this analysis will work best immediately following the workout.<PiHeartbeat /> <PiHeadphones /></p> 
    </>
    )
}