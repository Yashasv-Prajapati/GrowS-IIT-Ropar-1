import React from 'react'
import {MapContainer,TileLayer} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'

export default function MapContainerRoutes(props) {
  return (
    <MapContainer center={[28,77]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"400px",marginTop:"80px", marginBottom:'90px',width:"50%",marginLeft:"25%",marginRight:"25%"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {props.routes.map((route,index) => {
          return <LeafletRoutingMachine index={index} waypoints={route}/>
        }
        )}
        </MapContainer>
  )
}
