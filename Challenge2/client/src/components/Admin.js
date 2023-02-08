import React,{useState,useEffect, useCallback} from 'react'
// import MapContainerRoutes from './MapContainerRoutes';
import AdminForm from './AdminForm';
import axios from 'axios';
import { Button, Card, Container, Dropdown } from 'react-bootstrap';
// import { GoogleMap, useJsApiLoader, Marker, InfoWindow, DirectionsRenderer, DirectionsService } from '@react-google-maps/api';
import driver_routes from './driver_routes.json';
import { useMemo, useRef } from 'react';
// import React from 'react'
import {MapContainer,TileLayer, Marker} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'
import { useContext } from 'react';
import {Context} from './context.js';


const MapContainerRoutes= (props) =>{

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


export default function Admin() {

  const {setRouteChanged, routeChanged} = useContext(Context)


  const [routes,setRoutes] = useState([
    [
      [12.9120799, 77.5745235, "a"],
      [12.9088826, 77.5857567, "b"], 
      [12.9122542, 77.63633109999999, "c"],
      [12.9120766, 77.6494981, "d"]
    ],
    [
      [12.9120799, 77.5745235, "e"],
      [12.9088826, 77.5857567, "f"], 
      [12.9122542, 77.63633109999999, "g"],
      [12.9120766, 77.6494981, "h"]
    ]
  ]);
  const point1 = useRef(0);
  const point2 = useRef(0);
  const [intraRoute, setInRoute] =  useState(true);
  const change = ['Swap points in a route', 'Swap points between two routes'];

  const [analytics, setAnalytics] = useState({
    time_taken: 0,
    total_distance: 0,
  });

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
    // console.log("File:", file);


    axios.post("http://localhost:8000/dispatch_addresses", payload, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }  
    });
  }

  const getRoutes = async () => {
      const rte = await fetch('http://localhost:8000/admin_routes')
      const data = await rte.json()
      // console.log("data :",data)
      setRoutes(data.routes)  
  }

  const getAnalytics = async () => {
    const response = await fetch('http://localhost:8000/get_analytics')
    const data = await response.json();
    // console.log("Analytics", data)
    setAnalytics(data)
  }

  const setPoints=(e)=>{
    if(e.target.name==="point1"){
      point1.current = parseInt(e.target.value);
    }else{
      point2.current = parseInt(e.target.value);
    }

  }

  const changeGlobalRoute = (e)=>{
    e.preventDefault();

    let temproutes = [...routes];

    [temproutes[routetoshow1][point1.current], temproutes[routetoshow2][point2.current]] = [temproutes[routetoshow2][point2.current], temproutes[routetoshow1][point1.current]]

    setRoutes(temproutes)

  }




  const changeRoute = async (e,routeIndex) => {
    e.preventDefault();

    // swapping the points on the route
    const p1=point1.current;
    const p2=point2.current;  
    
    let tempRoutes = [...routes];
    
    [tempRoutes[routeIndex][p1], tempRoutes[routeIndex][p2]] = [tempRoutes[routeIndex][p2], tempRoutes[routeIndex][p1]];

    setRoutes(tempRoutes);

    
  }

  useEffect(() => {
    getRoutes()
    getAnalytics()
  }, [])
  
  useEffect(()=>{
    // console.log('Route to show', routetoshow)

  }, [routes])

  const [routetoshow1, setRouteToShow1] = useState(0);
  const [routetoshow2, setRouteToShow2] = useState(0);
  const [routetoshow3, setRouteToShow3] = useState(0);
  
  const routeIndexes = [];
  for(let i=0;i<routes.length;i++){
    routeIndexes.push(i)
  }


  return (
    <div>
      {routes.length !==0 ?
                ( <MapContainerRoutes routes={routes}/>
                ):null
              } 
      <div className='w-full flex justify-center'>
      <button className='mx-auto border rounded border-blue shadow-lg bg-blue-300 p-2 m-2' onClick={()=>{setInRoute(!intraRoute)}}> {intraRoute? change[0] : change[1]} </button>
      </div>

      

      {
        intraRoute?(
          <div>
              
              {/* Add a form to add a dynamic waypoint */}
              {/* Display the current routes */}
              <Container className=''>
                
                <h3 className='text-3xl text-center my-4'>Current Routes</h3>


                <ul className='flex flex-col justify-between items-center py-4'>
                
                <label for="routeindex" class="mb-2 text-sm font-medium text-gray-900 dark:text-gray-500">Choose Route</label>

                <select id="routeindex" onChange={(event)=>{setRouteToShow3(event.target.value)}}
                class="block border border-grey-light w-1/3 p-3 rounded mb-4" >

                    {routeIndexes.map((sIndex, index)=>{
                      return <option className='h-80' value = {sIndex} key={index}>{index+1}</option>
                    })}

                </select>

                    <li>
                      <div className='border border-black rounded p-2 h-fit max-h-[50vh] overflow-y-scroll'> 


                        {
                          routes[routetoshow3].map( (point, pointIndex) =>(
                            <div >
                              <div>
                              {pointIndex+1} - {point[2]}
                              </div>
                            </div>)
                          )
                        }

                      </div>
                      <br/>
                      <div  className='flex flex-row my-4'>
                        <div className='flex flex-row items-center justify-center mx-auto'>

                          <label>Enter Route Number: (Integer)</label>
                          <input type="text" name="point1" onChange={setPoints} className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />

                          <label>Enter Route Number: (Integer)</label>
                          <input type="text" name="point1" onChange={setPoints} className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
                        </div>
                        
                        <div >
                          <button type="button" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" onClick={(e)=>{changeRoute(e, routetoshow3)}}> Change </button>

                        </div>

                      </div>
                      
                    </li>
                  
                  {/* ))} */}

                </ul>
              </Container>
              {/* Card displaying the analytics info*/}
              

          </div>

        ):
        (
          <div>
            <Container className=''>
                
                <h3 className='text-3xl text-center my-4'>Current Routes</h3>


                <ul className='flex flex-col justify-between items-center py-4'>
                <label for="routeindex" class="mb-2 text-sm font-medium text-gray-900 dark:text-gray-500">Choose Route</label>

                <select id="routeindex" onChange={(event)=>{setRouteToShow2(event.target.value)}}
                class="block border border-grey-light w-1/3 p-3 rounded mb-4" >

                    {routeIndexes.map((sIndex, index)=>{
                      return <option className='h-80' value = {sIndex} key={index}>{index+1}</option>
                    })}

                </select>

                    <li>
                      <div className='border border-black rounded p-2 h-fit max-h-[50vh] overflow-y-scroll'> 


                        {
                          routes[routetoshow2].map( (point, pointIndex) =>(
                            <div >
                              <div>
                              {pointIndex+1} - {point[2]}
                              </div>
                            </div>)
                          )
                        }

                      </div>
                      <br/>
                      <div  className='flex flex-row my-4'>
                        <div className='flex flex-row items-center justify-center mx-auto'>

                          <label>Enter Route Number: (Integer)</label>
                          <input type="text" name="point1" onChange={setPoints} className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />

                        </div>
                        
                        <div >
                          {/* <button type="button" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" onClick={(e)=>{changeRoute(e,route, routeIndex)}}> Change </button> */}

                        </div>

                      </div>
                      
                    </li>

                <label for="routeindex" class="mb-2 text-sm font-medium text-gray-900 dark:text-gray-500">Choose Route</label>

                <select id="routeindex" onChange={(event)=>{setRouteToShow1(event.target.value)}}
                class="block border border-grey-light w-1/3 p-3 rounded mb-4" >

                    {routeIndexes.map((sIndex, index)=>{
                      return <option className='h-80' value = {sIndex} key={index}>{index+1}</option>
                    })}

                </select>

                    <li>
                      <div className='border border-black rounded p-2 h-fit max-h-[50vh] overflow-y-scroll'> 


                        {
                          routes[routetoshow1].map( (point, pointIndex) =>(
                            <div >
                              <div>
                              {pointIndex+1} - {point[2]}
                              </div>
                            </div>)
                          )
                        }

                      </div>
                      <br/>
                      <div  className='flex flex-row my-4'>
                        <div className='flex flex-row items-center justify-center mx-auto'>

                          <label>Enter Route Number: (Integer)</label>
                          <input type="text" name="point1" onChange={setPoints} className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
                        </div>
                        
                        <div >
                          <button type="button" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" onClick={(e)=>{changeGlobalRoute(e)}}> Change </button>

                        </div>

                      </div>
                      
                    </li>
                  
                  {/* ))} */}

                </ul>
              </Container>


          </div>
        )
      }




      <Card className='w-1/3 mx-auto my-4 rounded bg-blue-200 p-2 shadow-lg flex justify-center items-center'>
                <Card.Body>
                  <Card.Title className="font-sans">Analytics</Card.Title>
                  <Card.Text>
                    <ul className="font-mono">
                      {/* <li>Number of Routes: ${}</li> */}
                      <li>Total Distance Covered: {parseInt(analytics["total_distance"])} km</li>
                      <li>Total Time Taken: {parseInt(parseInt(analytics["total_time"])/60)} min</li>
                      <li>Percent Delivery Items: {parseFloat(analytics["percentage_ontime_deliveries"]).toFixed(2)}</li>
                      <li>Number of Successful Deliveries: {parseInt(analytics["total_ontime_deliveries"])}</li>
                    </ul>
                    {/* Dropdown to show a particular driver analytics, a particular index */}
                  </Card.Text>
                </Card.Body>
              </Card>

      


      {/* Add a form to manually edit the routes */}
    </div>
  )
}



/*
{/* <h2>Admin</h2>
      {
        isLoaded ? (
          <>
            <div>Google Map</div>
            <GoogleMap center={{lat: 28, lng: 77}} zoom={10} mapContainerStyle={{width:'70vw',height:'70vh','marginLeft':'auto','marginRight':'auto'}}>
              

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
      } */
