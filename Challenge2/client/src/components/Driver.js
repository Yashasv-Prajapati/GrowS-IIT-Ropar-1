import React, { useEffect, useRef,useState } from 'react'
import {MapContainer, Marker, Popup, TileLayer} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'
import { useNavigate, useParams} from 'react-router-dom'
import { Card } from 'react-bootstrap'
// import { useNavigate } from 'react-router-dom'


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
    const driver_id = useParams().id
    const [Driver, setDriver] = useState(driver_id)
    

    const getRoute = async () => {
        const rte = await fetch(`http://localhost:8000/driver_route?index=${driver_id}`, {
            method:'get',
            headers:{
                'Content-Type':'application/json'
            }
        })
        const data = await rte.json()
        setRoute(data.route)
    }

    const getAnalytics = async () => {
        const response = await fetch('http://localhost:8000/get_analytics')
        const data = await response.json();
        console.log("Analytics", data)
        setAnalytics(data)
      }

      const navigate = useNavigate();

    const changeDriver = () =>{
        
        if(Driver === NaN || Driver === undefined || Driver === "" || Driver === null){
            alert("Please enter a driver");
            return;  
        }

        navigate(`/driver/${Driver}`)

        window.location.reload(true)



    }

    useEffect(() => {
        setRoute(routes[driver_id-1])
    }, [])

    useEffect(() => {
        getRoute()
        getAnalytics()
    }, [])

  return (
    <div>

    {
    /* <MapContainer center={route[0]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"400px",marginTop:"80px", marginBottom:'90px',width:"50%",marginLeft:"25%",marginRight:"25%"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        return <LeafletRoutingMachine waypoints={route}/>
    </MapContainer> 
    */
    }

    {(route?.length !== 0 && route?.length!==undefined && route!==undefined) ? ( <Map route={route} />) : null}

    {/* <MapContainerRoutes routes={[route]} /> */}

    <div className='flex flex-col justify-center items-center'>
        <label className='mx-auto text-2xl p-2'>Enter Driver ID</label>
        <input className='bg-gray-200 text-2xl rounded p-2' type="text" placeholder={'1'} onChange={(e) => setDriver(e.target.value)}/>
        <button className='p-2 bg-blue-300 hover:bg-blue-400 active:bg-blue-300 rounded m-2' onClick={changeDriver}>Get Route</button>    
    </div>


    <Card className='w-1/3 mx-auto my-4 rounded bg-blue-200 p-2 shadow-lg flex justify-center items-center'>
        <Card.Body>
        <Card.Title className="font-sans">Analytics</Card.Title>
        <Card.Text>
            <ul className="font-mono">
                {/* <li>Number of Routes: ${}</li> */}
                <li>Number of ontime deliveries of driver: {analytics['driver_analytics'] !==undefined && analytics['driver_analytics']?.length!==0 ? parseInt(analytics["driver_analytics"][driver_id-1]['ontime_deliveries']) : 'NA'}</li>
                <li>Time taken by driver: {analytics['driver_analytics']!==undefined && analytics['driver_analytics']?.length!==0 ? parseInt(parseInt(analytics["driver_analytics"][driver_id-1]['total_time'])/60) : 'NA'} min</li>
                <li>Total Distance Covered: {analytics['driver_analytics']!==undefined && analytics['driver_analytics']?.length!==0 ? parseInt(parseInt(analytics["driver_analytics"][driver_id-1]['total_time'])/3600 * 40) : 'NA'} km</li>
            </ul>
            {/* Dropdown to show a particular driver analytics, a particular index */}
        </Card.Text>
        </Card.Body>
    </Card>
    
    </div>
  )
}
