import React from 'react';

export function Song({props, ranking, name, artist, image, backgroundColor}) {
    return (
        <>
            <div className= "flex-container" id="rcorners1" style={{"background-color": backgroundColor}}>
                <div className="Image">
                    <img src={image} width="75" height="75"/>
                </div>
                <div className="Content song-content">
                    <span className="songlisting-font">
                        <p>{ranking}. {name}</p>
                        <p> by {artist}</p>
                    </span>
                </div>
            </div>
        </>
    )
}