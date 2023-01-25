import React,{useState,useEffect} from 'react'
import MapContainerRoutes from './MapContainerRoutes';
import axios from 'axios';

export default function Admin() {
  const [routes,setRoutes] = useState([])
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
      <form 
      onSubmit={sendFile}
      //action="http://localhost:8000/dispatch_addresses" 
      method="POST" enctype="multipart/form-data" >
        <input type="file" name="file" 
          accept=".xls,.xlsx,.csv,.txt" 
          onChange={e => setFile({ file: e.target.files[0] })} />
        <button type="submit">Send</button>
      </form>
      <MapContainerRoutes routes={routes}/>
      {/* Add a form to add a dynamic waypoint */}
      <form onSubmit={addWayPoint}>
        <input type="text" name="waypoint" />
        <button type="submit">Add Waypoint</button>
      </form>
    </div>
  )
}
