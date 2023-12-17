import React from 'react';


export function Error({ message }) {
    return (
    <>
        <div className="error" id="rcorners1">
            <p>{message}</p>
        </div>
    </>
    )
}