import React, { useEffect, useRef,useState } from 'react'
import {MapContainer, Marker, Popup, TileLayer} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'

export default function Driver() {

    const [route,setRoute] = useState([])

    const getRoute = async () => {
        
        const rte = await fetch('http://localhost:8000/driver_route', {
            method:'get',
            headers:{
                'Content-Type':'application/json'
            }
        })

        const data = await rte.json()
        console.log(data)
        setRoute(data.route)
    }

    useEffect(() => {
        getRoute()
    }, [])

  return (
    <div>
    <div>Driver</div>
    <MapContainer center={[28,77]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"400px",marginTop:"80px", marginBottom:'90px',width:"50%",marginLeft:"25%",marginRight:"25%"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {/* <Marker position={[28,77]} />
        <Popup position={[28,77]}> 
            <div>Popup for any custom information.</div>
        </Popup> */}
        <LeafletRoutingMachine waypoints={route}/>
        </MapContainer>
    </div>
  )
}
