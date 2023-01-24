import './App.css';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import ScanTool from './components/ScanTool';
import Admin from './components/Admin';
import Driver from './components/Driver';
import Header from './components/Header';
import "bootstrap/dist/css/bootstrap.min.css"

function App() {
  return (
    <>
    <Header/>
    <Routes>
      <Route path="/" element={<LandingPage/>} />
      <Route path="scan-tool" element={<ScanTool/>} />
      <Route path="admin" element={<Admin/>} />
      <Route path="driver" element={<Driver/>} />
    </Routes>
    </>
  );
}

export default App;
