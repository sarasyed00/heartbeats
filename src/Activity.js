import React from 'react';
import { PiPersonSimpleRun } from "react-icons/pi";


export function Activity({ date, activeTime, distance }) {
    return (
    <>
        <p>Last Workout: {date} <PiPersonSimpleRun /></p> 
        <p>Total Time: {activeTime}</p>
        <p>Total Distance: {distance}</p>
    </>
    )
}