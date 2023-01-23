import React, { useEffect } from 'react'
import { MapContainer, TileLayer, LocationMarker } from 'react-leaflet'

export default function Driver() {

    const fetchData = async () => {
        const data = await fetch('http://localhost:8000/')
        const json = await data.json()
        console.log(json)
    }

  
    useEffect(() => {
        fetchData()
    }, [])

  return (
    <div style={{'width':'50%','height':'50%'}}>
    {/* <div>Driver</div> */}
    {/* <MapContainer
        center={{ lat: 51.505, lng: -0.09 }}
        zoom={13}
        scrollWheelZoom={false}>
        <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker />
    </MapContainer> */}
    </div>
  )
}
