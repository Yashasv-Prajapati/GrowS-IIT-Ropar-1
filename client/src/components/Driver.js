import React, { useEffect, useRef,useState } from 'react'
import {MapContainer, Marker, Popup, TileLayer} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'
import driver_routes from './driver_routes.json'
import MapContainerRoutes from './MapContainerRoutes';


const Map = ({route}) => {
    console.log("Running Map")
    // window.location.reload(true)

    return (

        <MapContainer center={route[0]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"400px",marginTop:"80px", marginBottom:'90px',width:"50%",marginLeft:"25%",marginRight:"25%"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
            <LeafletRoutingMachine waypoints={route}/>
        </MapContainer>

    )

}

export default function Driver() {

    const routes = [
        [[28,77],[24,71],[26,76]],
        [[23,74],[25,72],[26,78]],
        [[22,73],[24,70],[27,71]]
    ]

    const [route,setRoute] = useState(routes[0])

    const [driver,setDriver] = useState(1)

    const [drivers,setDrivers] = useState([1,2,3])

    const getRoute = async () => {
        const rte = await fetch('http://localhost:8000/admin_routes', {
            method:'get',
            headers:{
                'Content-Type':'application/json'
            }
        })
        const data = await rte.json()
        console.log(data)
        //setRoute(data.routes)
        // setDrivers based on number
    }
    
    const changeRoute = (driverNum)=>{
        // console.log(route[driverNum-1])
        
        setRoute(routes[driverNum-1])
        console.log(route)
    }


    useEffect(() => {

        changeRoute(driver)
        console.log("driver is " ,driver)
        console.log(route)

    }, [driver])

  return (
    <div>
    <div>Driver</div>

    {/* <MapContainer center={route[0]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"400px",marginTop:"80px", marginBottom:'90px',width:"50%",marginLeft:"25%",marginRight:"25%"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        return <LeafletRoutingMachine waypoints={route}/>
    </MapContainer> */}
    <Map route={route} />


    {/* <MapContainerRoutes routes={[route]} /> */}
    
    <div className="w-1/3 mx-auto mb-20">

        {/* {/* for selecting batch  */}
        <label for="user" class="mb-2 text-sm font-medium text-gray-900 dark:text-gray-500">Drivers</label>

        <select id="user" onChange={(event)=>{setDriver(event.target.value)}}
        class="block border border-grey-light w-full p-3 rounded mb-4" >

            {drivers.map((sDriver, index)=>{
            return <option className='h-80' value = {sDriver} key={index}>{sDriver}</option>
            })}

        </select>
    
    </div>
    </div>
  )
}
