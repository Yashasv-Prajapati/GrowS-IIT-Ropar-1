import React,{useState,useEffect, useCallback} from 'react'
import MapContainerRoutes from './MapContainerRoutes';
import AdminForm from './AdminForm';
import axios from 'axios';
import { Button, Container } from 'react-bootstrap';

export default function Admin() {
  const [routes,setRoutes] = useState([[[28,77],[28.5,77.5]],[[29.5,77.5],[29,77], [30,79], [40.5,79.5]]])
  const [file, setFile] = useState(null);

  const [changedRoute, setChangedRoute] = useState("");
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
      console.log(data)
      // setRoutes(data.routes)
  }

  const addWayPoint = async (e) => {
    e.preventDefault();
    const waypoint = e.target.waypoint.value;
    const response = await axios.get(`http://localhost:8000/get_waypoint_to_coord?query=${waypoint}`)
    const data = await response.json();
    
    // In this data
  }
  
  const debounce = (func)=>{
    let timer;
    return function(...args){
      const context = this;
      if(timer){
        clearTimeout(timer);
      }
      timer = setTimeout(()=>{
        timer=null
        func.apply(context, args)
      }, 500);
    }
  }

  const changeRoute = async (e, Routes,routeIndex) => {
    e.preventDefault();
    const route = e.target.value;
    // parse route string to Number array
    const changedRoutes = route.split(" ").map(Number);
    
    // new array to store the changed points order
    const newPoints = [];

    // changing routes according to the given manual info
    changedRoutes.forEach(new_pointIndex => {
      newPoints.push(Routes[new_pointIndex-1]);
    });

    // changing old route to new route
    routes[routeIndex] = Routes;
    setRoutes(routes);

    return newPoints;

  }

  const optimizedChangeRoutes = useCallback(debounce(changeRoute), []);


  useEffect(() => {
      // getRoutes()
  }, [])

  return (
    <div>
      <h2 className='bg-blue-400 p-4 m-4 text-center w-1/3 mx-auto'>Admin</h2>
      <MapContainerRoutes routes={routes}/>
      {/* Add a form to add a dynamic waypoint */}
      <AdminForm />
      <form className='flex flex-col justify-center items-center' onSubmit={addWayPoint}>
        <label className='text-3xl text-center my-4'>Add Way Points</label>
        <div className='flex flex-row'>
          <input className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" type="text" name="waypoint" />
          <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Add Waypoint</button>
        </div>
      </form>
      {/* Display the current routes */}
      <Container className=''>
        <h3 className='text-3xl text-center my-4'>Current Routes</h3>

        <ul className='flex flex-col justify-between items-center py-4'>
          {routes.map((route, routeIndex) => (
            <li key={routeIndex}>
              {route.map((point, pointIndex) =>(
                <span key={pointIndex} className='text-bold'> Point - {pointIndex+1}. [{point[0]}, {point[1]}] </span>
              ))}
              <br/>
              <label>Change Route: (In the format of 2 1 4 3)</label>
              <input type="text" className="shadow appearance-none border rounded m-2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" onChange={(e)=>{optimizedChangeRoutes(e,route,routeIndex)}} name="route" />
              <button type="button" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Change</button>
            </li>
          ))}
        </ul>
      </Container>
      {/* Add a form to manually edit the routes */}
    </div>
  )
}
