import React, { useEffect } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import "leaflet-routing-machine"
import "leaflet-routing-machine/dist/leaflet-routing-machine.css"
import { useMap } from 'react-leaflet'
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow
});

L.Marker.prototype.options.icon = DefaultIcon;

export default function LeafletRoutingMachine(props) {
  const map = useMap()
  const colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']
  useEffect(() => {
    const waypoints = []
    console.log(props)
    props.waypoints.forEach(element => {
        waypoints.push(L.latLng(element[0], element[1]))
    })
    L.Routing.control({
        waypoints: waypoints,
        lineOptions: {
            styles: [{ color: colors[props.index!=undefined? props.index : Math.floor(Math.random()*20)], weight: 4 }]
        },
        show: false,
        addWaypoints: false,
        routeWhileDragging: true,
        draggableWaypoints: false,
        fitSelectedRoutes: true,
        showAlternatives: false
    }).addTo(map)
    
  }, [props])

  return (
    <>
    </>
  )
}
