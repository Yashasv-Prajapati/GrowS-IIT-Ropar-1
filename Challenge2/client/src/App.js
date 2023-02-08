import './App.css';
import React, {useEffect, useState} from 'react';
import { Routes, Route } from 'react-router-dom';
import ScanTool from './components/ScanTool';
import Admin from './components/Admin';
import Driver from './components/Driver';
import Header from './components/Header';
import Data from './components/Data'
import { Context } from './components/context';
import "bootstrap/dist/css/bootstrap.min.css"

function App() {

  const [routeChanged, setRouteChanged] = useState(false);
  const contextParams = {
    routeChanged, setRouteChanged
  }

  useEffect(()=>{

  }, [])

  return (
    <>
    <Header/>
    <Context.Provider value={contextParams}>
    <Routes>
      <Route path="/" element={<Admin/>} />
      <Route path="scan-tool" element={<ScanTool/>} />
      <Route path="admin" element={<Admin/>} />
      <Route path="driver/:id" element={<Driver/>} />
      <Route path="data" element={<Data/>} />
    </Routes>
    </Context.Provider>
    </>
  );
}

export default App;
