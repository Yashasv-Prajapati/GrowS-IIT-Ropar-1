import React,{useState,useEffect} from 'react'
import MapContainerRoutes from './MapContainerRoutes';
import AdminForm from './AdminForm';
import axios from 'axios';

export default function Admin() {
  const [routes,setRoutes] = useState([])

  const getRoutes = async () => {
      const rte = await fetch('http://localhost:8000/admin_routes')
      const data = await rte.json()
      console.log(data)
      setRoutes(data.routes)
  }

  const addWayPoint = async (e) => {
    e.preventDefault();
    const waypoint = e.target.waypoint.value;
    const response = await axios.get(`http://localhost:8000/get_waypoint_to_coord?query=${waypoint}`)
    const data = await response.json();
    
    // In this data
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
    </div>
  )
}
