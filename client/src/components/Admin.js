import React,{useState,useEffect} from 'react'
import MapContainerRoutes from './MapContainerRoutes';
import AdminForm from './AdminForm';
import axios from 'axios';
import { Button, Container } from 'react-bootstrap';

export default function Admin() {
  const [routes,setRoutes] = useState([[[28,77],[28.5,77.5]],[[29.5,77.5],[29,77]]])
  const [file, setFile] = useState(null);

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

  const changeRoute = async (e) => {
    e.preventDefault();
    const route = e.target.route.value;
  }

  useEffect(() => {
      getRoutes()
  }, [])

  return (
    <div>
      <h2>Admin</h2>
      <MapContainerRoutes routes={routes}/>
      {/* Add a form to add a dynamic waypoint */}
      <AdminForm />
      <form onSubmit={addWayPoint}>
        <input type="text" name="waypoint" />
        <button type="submit">Add Waypoint</button>
      </form>
      {/* Display the current routes */}
      <Container>
        <h3>Current Routes</h3>
        <ul>
          {routes.map((route, index) => (
            <li key={index}>
              {route.map((point, index) =>(
                <span key={index}> - {index+1}. [{point[0]}, {point[1]}] </span>
              ))}
              <br/>
              <label>Change Route: (In the format of 2 1 4 3)</label>
              <input type="text" name="route" />
              <Button type="button" className="btn-primary" onClick={changeRoute(route)}>Change</Button>
            </li>
          ))}
        </ul>
      </Container>
      {/* Add a form to manually edit the routes */}
    </div>
  )
}
