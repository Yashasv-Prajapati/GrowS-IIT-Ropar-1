import React, { useEffect } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import "leaflet-routing-machine"
import "leaflet-routing-machine/dist/leaflet-routing-machine.css"
import { useMap } from 'react-leaflet'

export default function LeafletRoutingMachine(props) {
  const map = useMap()
  useEffect(() => {
    const waypoints = []
    props.waypoints.forEach(element => {
        waypoints.push(L.latLng(element[0], element[1]))
    })
    L.Routing.control({
        waypoints: waypoints,
        lineOptions: {
            styles: [{ color: "#6FA1EC", weight: 4 }]
        },
        show: false,
        addWaypoints: true,
        routeWhileDragging: true,
        draggableWaypoints: true,
        fitSelectedRoutes: true,
        showAlternatives: false
    }).addTo(map)
    
  }, [])

  return (
    <>
    </>
  )
}
