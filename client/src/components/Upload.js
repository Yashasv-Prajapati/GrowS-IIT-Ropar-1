import React from 'react'
import {useState} from 'react' 
import ReactCardFlip from 'react-card-flip'
import shortid from'shortid'
import img1 from '../images/SKU_1_A.jpg'
import img2 from '../images/SKU_1.jpg'


export default function Upload() {
    const [flip, setFlip] = useState(false);
    const item = {
        skuNo: 7,
        volume:8,
        height: 10,
        width: 10,
        length: 10,
        weight: 10
    }


  return (
    <>
    {/* To be added by anant */}

    <ReactCardFlip isFlipped={flip} flipDirection="vertical" >
    <div key={shortid.generate()} onClick={()=>{setFlip(!flip)}}>
        {/* Photo Card */}
            <div className="max-w-sm m-4 p-4 bg-gradient-to-r from-green-300 to-green-400 hover:bg-green-400 active:bg-green-300 rounded overflow-hidden shadow-lg">
                <div className = "px-2 py-1">
                    <img src = {"https://cdn-icons-png.flaticon.com/512/149/149071.png"} alternate ="Img1" />
                </div>
            </div>
        </div>

        <div key={shortid.generate()} onClick = {()=>{setFlip(!flip)}}>
        {/* Photo Card */}
            <div className="max-w-sm m-4 p-4 bg-gradient-to-r from-green-300 to-green-400 hover:bg-green-400 active:bg-green-300 rounded overflow-hidden shadow-lg">
                <div className = "px-2 py-1">
                    
                    <div className="flex flex-row justify-between items-center ">

                    <img src = {"../images/SKU_1.jpg"} alternate ="Img1" />
                                        </div>
                </div>
            </div>
        </div>
        </ReactCardFlip>
    </>
  )
}
