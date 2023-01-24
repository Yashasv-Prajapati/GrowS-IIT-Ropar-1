import React,{useState} from 'react'
import httpClient from "../httpClient";
import {MapContainer,TileLayer} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import LeafletRoutingMachine from './LeafletRoutingMachine'

export default function Admin() {
  const routes = [[[28,77],[30,77]],[[28,78],[30,78],[32,78]]]
  const [file, setFile] = useState('');

  function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');


  const sendFile = async (e) => {
    e.preventDefault();
    console.log(file['file']);
    
    const payload = new FormData();
    payload.append("msg", "Excel File");
    payload.append("file", file);
    const response = await httpClient.post("http://localhost:8000/dispatch_addresses", payload, {
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': "multipart/form-data",
      }
    });
    console.log(response);

    // const response = await httpClient.post("http://localhost:8000/dispatch_addresses");
  }
  return (
    <div>
      <h2>Admin</h2>
      <form>
        <input type="file" name="file" 
          accept=".xls,.xlsx,.csv,.txt" 
          onChange={e => setFile({ file: e.target.files[0] })} />
        <button type="submit" onClick={sendFile}>Send</button>
      </form>

      <MapContainer center={[28,77]} zoom={6} scrollWheelZoom={false} 
        style={{ height:"400px",marginTop:"80px", marginBottom:'90px',width:"50%",marginLeft:"25%",marginRight:"25%"
            }} >
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {routes.map((route,index) => {
          return <LeafletRoutingMachine key={index} waypoints={route}/>
        }
        )}
        </MapContainer>
    </div>
  )
}
