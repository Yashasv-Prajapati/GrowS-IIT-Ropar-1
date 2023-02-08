import React from 'react'
import {MapContainer,TileLayer, Marker} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'

export default function MapContainerRoutes(props) {
  console.log(props.routes)
  return (
    <MapContainer center={props.routes[0][0]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"70vh",marginTop:"80px", marginBottom:'90px',width:"80%",marginLeft:"auto",marginRight:"auto"
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
