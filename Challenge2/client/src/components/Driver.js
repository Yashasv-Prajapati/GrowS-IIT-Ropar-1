import React, { useEffect, useRef,useState } from 'react'
import {MapContainer, Marker, Popup, TileLayer} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'
import driver_routes from './driver_routes.json'
import MapContainerRoutes from './MapContainerRoutes';
import { useNavigate, useParams} from 'react-router-dom'
import { Card } from 'react-bootstrap'


const Map = ({route}) => {
    console.log("Running Map")
    console.log("route", route)
    // window.location.reload(true)

    return (

        <MapContainer center={[route[0][0], route[0][1]]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"70vh",marginTop:"80px", marginBottom:'90px',width:"80%",marginLeft:"auto",marginRight:"auto"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
            <LeafletRoutingMachine waypoints={route}/>
        </MapContainer>

    )

}

export default function Driver() {

    const routes = [[]]
    const [route,setRoute] = useState([])
    const [analytics,setAnalytics] = useState([])
    const driver = useParams().id
    
    const getRoute = async () => {
        const rte = await fetch(`http://localhost:8000/driver_route?index=${driver}`, {
            method:'get',
            headers:{
                'Content-Type':'application/json'
            }
        })
        const data = await rte.json()
        // console.log("Data is", data)
        setRoute(data.route)
    }

    const getAnalytics = async () => {
        const response = await fetch('http://localhost:8000/get_analytics')
        const data = await response.json();
        // console.log("Analytics", data)
        setAnalytics(data)
      }

    useEffect(() => {
        setRoute(routes[driver-1])
        // console.log(route)
    }, [])

    useEffect(() => {
        getRoute()
        getAnalytics()
    }, [])

  return (
    <div>

    {/* <MapContainer center={route[0]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"400px",marginTop:"80px", marginBottom:'90px',width:"50%",marginLeft:"25%",marginRight:"25%"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        return <LeafletRoutingMachine waypoints={route}/>
    </MapContainer> */}
    {(route?.length !== 0 && route?.length!==undefined && route!==undefined) ? ( <Map route={route} />) : null}

    {/* <MapContainerRoutes routes={[route]} /> */}

    <Card className='w-1/3 mx-auto my-4 rounded bg-blue-200 p-2 shadow-lg flex justify-center items-center'>
        <Card.Body>
        <Card.Title className="font-sans">Analytics</Card.Title>
        <Card.Text>
            <ul className="font-mono">
            {/* <li>Number of Routes: ${}</li> */}
            <li>Number of ontime deliveries of driver: {analytics['driver_analytics'] !==undefined && analytics['driver_analytics']?.length!==0 ? parseInt(analytics["driver_analytics"][driver]['ontime_deliveries']) : 'NA'}</li>
            <li>Number of ontime deliveries of driver: {analytics['driver_analytics']!==undefined && analytics['driver_analytics']?.length!==0 ? parseInt(analytics["driver_analytics"][driver]['total_time']) : 'NA'}</li>
            <li>Total Distance Covered: {parseInt(analytics["total_distance"])} km</li>
            <li>Total Time Taken: {parseInt(parseInt(analytics["total_time"])/3600)} min</li>
            <li>Percent Delivery Items: {parseFloat(analytics["percentage_ontime_deliveries"]).toFixed(2)}</li>
            <li>Number of Successful Deliveries: {parseInt(analytics["total_ontime_deliveries"])}</li>
            </ul>
            {/* Dropdown to show a particular driver analytics, a particular index */}
        </Card.Text>
        </Card.Body>
    </Card>
    
    </div>
  )
}
