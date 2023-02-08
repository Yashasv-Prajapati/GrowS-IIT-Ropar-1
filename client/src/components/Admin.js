import React,{useState,useEffect, useCallback} from 'react'
import MapContainerRoutes from './MapContainerRoutes';
import AdminForm from './AdminForm';
import axios from 'axios';
import { Button, Card, Container } from 'react-bootstrap';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow, DirectionsRenderer, DirectionsService } from '@react-google-maps/api';
import driver_routes from './driver_routes.json';
import { useMemo } from 'react';



export default function Admin() {

  const [routes,setRoutes] = useState(
    [
      [
        [12.9120799, 77.5745235],
        [12.9088826, 77.5857567], 
        [12.9122542, 77.63633109999999],
        [12.9120766, 77.6494981]
      ]
    ]
  );

  const [point1, setPoint1] = useState(-1);
  const [point2, setPoint2] = useState(-1);

  const [file, setFile] = useState(null);
  const [directionInfo, setDirectionInfo] = useState(new Array(routes.length).fill(null));

  const isLoaded = false;

  // const {isLoaded} = useJsApiLoader({
  //   googleMapsApiKey: "AIzaSyDAHiXvLdpAhTMfnWbQgL2cigqtsFkfuFQ"
  // })
  
  const sendFile = async (e) => {
    e.preventDefault();
    
    var payload = new FormData();
    payload.append("file", file);
    console.log("File:", file);


    axios.post("http://localhost:8000/dispatch_addresses", payload, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }  
    });
  }

  const getRoutes = async () => {
      const rte = await fetch('http://localhost:8000/admin_routes')
      const data = await rte.json()
      console.log("data :",data)
      setRoutes(data.routes)
      
  }

  const addWayPoint = async (e) => {
    e.preventDefault();
    const waypoint = e.target.waypoint.value;
    const response = await axios.get(`http://localhost:8000/get_waypoint_to_coord?query=${waypoint}`)
    const data = await response.json();

  }
  

  const changeRoute = async (e, Routes,routeIndex) => {
    e.preventDefault();

    // swapping the points on the route

    const p1=point1;
    const p2=point2;
    

    setRoutes(routes=>{
      let data = [...routes];
      let temp = data[routeIndex][p1];
      data[routeIndex][p1]=data[routeIndex][p2];
      data[routeIndex][p2]=temp;
      console.log("Swapped", data)
      return data;
    })

    console.log(routes)
    
  }

  // useEffect(() => {
  //   // getRoutes()
  //   console.log(routes)
  // }, [routes])

  useEffect(() => {
    getRoutes()
  }, [])


  return (
    <div>
      <h2>Admin</h2>
      {
        isLoaded ? (
          <>
            <div>Google Map</div>
            <GoogleMap center={{lat: 28, lng: 77}} zoom={10} mapContainerStyle={{width:'70vw',height:'70vh','marginLeft':'auto','marginRight':'auto'}}>
              {/* Write a code to plot a route on Google Maps */}
              

              {routes.map((route,index) => {
                return (
                  <DirectionsService options={
                    {
                      origin : { lat: route[0][0], lng: route[0][1] },
                      destination: { lat: route[route.length-1][0], lng: route[route.length-1][1] },
                      waypoints: route.slice(1,route.length-1).map((point) => {
                        return {
                          location: { lat: point[0], lng: point[1] },
                          stopover: true,
                        }
                      }
                      ),
                      travelMode: 'DRIVING',
                    }
                  }
                  
                  callback={(res) => {
                    // if (res != null) {
                    //   let newDirectionInfo = directionInfo; 
                    //   newDirectionInfo[index] = res;
                    //   setDirectionInfo(newDirectionInfo)
                    // }
                  }}/>
                )})
              }

              {  directionInfo.map((direction,index) => {
                  // if (direction == null) {
                  //   console.log("Direction is null")
                  //   return;
                  // }

                  return (
                    <DirectionsRenderer options={{directions: direction}}/>
                  )
              })}

            </GoogleMap>
          </>
        ) : (
          <div>Loading...</div>
        )
      }
      <MapContainerRoutes routes={routes}/>
      {/* Add a form to add a dynamic waypoint */}
      {/* Display the current routes */}
      <Container className=''>
        



        <h3 className='text-3xl text-center my-4'>Current Routes</h3>


        <ul className='flex flex-col justify-between items-center py-4'>
          
          {routes.map( (route, routeIndex) => (
            <li key={routeIndex}>
              <div className='border border-black rounded p-2 h-fit max-h-[50vh] overflow-y-scroll'> 


                {
                  route.map( (point, pointIndex) =>(
                    <div >
                      <div>
                      {pointIndex} - {point[1]} {point[1]}
                      </div>
                    </div>)
                  )
                }

              </div>


              <br/>

              <div  className='flex flex-row my-4'>
                <div className='flex flex-row '>

                  <label>Enter Route 1: (Integer)</label>
                  <input type="text" onChange={(e)=>{setPoint1(parseInt(e.target.value))}} className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" name="route" />

                  <label>Enter Route 2: (Integer)</label>
                  <input type="text" onChange={(e)=>{setPoint2(parseInt(e.target.value))}} className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" name="route" />
                </div>
                
                <div >

                  
                  <button type="button" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" onClick={(e)=>{changeRoute(e,route, routeIndex)}}> Change </button>

                </div>

              </div>
              
            </li>
          
          ))}

        </ul>
      </Container>
      {/* Card displaying the analytics info*/}
      <Card className='w-1/3 mx-auto my-4 rounded bg-blue-200 p-2 shadow-lg flex justify-center items-center'>
        <Card.Body>
          <Card.Title className="font-sans">Analytics</Card.Title>
          <Card.Text>
            <ul className="font-mono">
              <li>Number of Routes: 8</li>
              <li>Number of Waypoints: 216</li>
              <li>Total Distance Covered: 1243 km</li>
              <li>Total Time Taken: 52310 sec</li>
              <li>Percent Delivery Items: 91%</li>
              <li>Number of Successful Deliveries: 197</li>
            </ul>
          </Card.Text>
        </Card.Body>
      </Card>


      {/* Add a form to manually edit the routes */}
    </div>
  )
}
