import React from 'react'
import { useState, useEffect } from 'react'

function Data() {
  
    const [vehicleNum, setvehicleNum] = useState(0)
    //const [CapacityArr, setCapacityArr ] = useState(new Array(vehicleNum))
    const [bagNum1, setbagNum1]=useState(0) // 60 60 100
    const [bagNum2, setbagNum2]=useState(0) // 80 80 100
    const [dispatchAdd, setDispatchAdd] = useState(null)
    const [pickupAdd, setPickUpAdd] = useState(null)
    const [SKUVolumeMapping, setSKUVolumeMapping] = useState(null)
    const [date, setDate] = useState(null)
    const [time, setTime] = useState(null)
    const [depotAdd, setDepotAdd] = useState(null)
    const [driverStartWindow, setDriverStartWindow] = useState(null)
    const [driverEndWindow, setDriverEndWindow] = useState(null)
    const [firstSolutionStrategy, setFirstSolutionStrategy] = useState("AUTOMATIC")
    const [metaHeuristic, setMetaHeuristic] = useState("AUTOMATIC")
    
    async function sendData(e){
      e.preventDefault()

      // setting data for sending
      const formData = new FormData();
      formData.append('vehicleNum', vehicleNum)
      //formData.append('CapacityArr', CapacityArr)
      formData.append('dispatchAdd', dispatchAdd)
      formData.append('bagNum1', bagNum1)
      formData.append('bagNum2', bagNum2)
      formData.append('date', date)
      formData.append('depotAdd', depotAdd)
      formData.append('driverStartWindow', driverStartWindow)
      formData.append('driverEndWindow', driverEndWindow)
      formData.append('firstSolutionStrategy', firstSolutionStrategy)
      formData.append('metaHeuristic', metaHeuristic)
      formData.append('SKUVolumeMapping', SKUVolumeMapping)

      fetch("http://localhost:8000/add_data", {
        method:'post',
        body:formData
      }).then(response=>{
        response.json().then((data)=>{
          console.log(data)
          console.log(data)
        })
      }).catch(err=>{
        console.log(err)

      })
      
    }


  function setMyData(e){
    if(e.target.name==="bagNum1"){
      setbagNum1(parseInt(e.target.value))
    }else{
      setbagNum2(parseInt(e.target.value))
    }
  }

  async function addPickup(e){
    e.preventDefault()

    // setting data for pickup addresses
    const formData = new FormData();
    formData.append('pickupAdd', pickupAdd)
    formData.append('time', time)
    
    fetch("http://localhost:8000/add_pickup_points", {
      method:'post',
      body:formData
    }).then(response=>{
      response.json().then((data)=>{
        console.log(data)
      })
    }
    ).catch(err=>{
      console.log(err)
    }
    )
  }

  

  // const setVehicleNumber = (e) => {
  //   try {
  //     console.log(e.target.value)
  //     if (e.target.value ===JSON.parse || e.target.value === "" || e.target.value === null || e.target.value === NaN || e.target.value === undefined || parseInt(e.target.value) < 0) {
  //       setVehicleNumber(0)
  //     } else {
  //       setvehicleNum(parseInt(e.target.value))
  //     }
  //   } catch (err) {

  //   }
  // }

  // const setCapacity = (e, index) => {
  //   CapacityArr[index] = parseInt(e.target.value)
  //   setCapacityArr(CapacityArr)
  //   console.log(CapacityArr)
  // }


  return (
    <>
    <form onSubmit={sendData} className="w-full max-w-2xl lg:mx-auto md:mx-auto bg-orange-200 p-4 m-4 mx-auto border-8 border-orange-100 rounded"
      // action="http://localhost:8000/data_form"
      // method="POST" enctype="multipart/form-data"
    >
      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-first-name">
          Dispatch Addresses
        </label>
        <input onChange={(e)=>{setDispatchAdd(e.target.files[0])}} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-red-500 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white"
          id="grid-first-name" type="file"
          name="dispatch_addresses"
          accept=".xls,.xlsx,.csv,.txt" />
      </div>

      <div className="w-full px-3 mb-3 md:mb-0">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-state">
          Date
        </label>
        <input onChange={(e)=>setDate(e.target.value)} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="grid-state" type="date" name="date"/>
      </div>

      <div className="w-full px-3 mb-3 md:mb-0">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-state">
          SKU Volume Mapping
        </label>
        <input onChange={(e)=>setSKUVolumeMapping(e.target.files[0])} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-red-500 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white"
          id="grid-first-name" type="file"
          name="sku_volume_mapping"
          accept=".xls,.xlsx,.csv,.txt" />
      </div>

      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
          Number of Vehicles
        </label>
        <input onChange={(e)=>setvehicleNum(e.target.value)} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" 
        id="grid-password" type="number" name = "number_of_vehicles"/>
      </div>

      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
          Depot Address
        </label>
        <input onChange={(e)=>setDepotAdd(e.target.value)} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
          id="grid-password" type="text" name="depot_address" />
      </div>

      {/* <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
          Driver Start Window
        </label>
        <input onChange={(e)=>setDriverStartWindow(e.target.value)} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
          id="grid-password" type="time" name="driver_start_window" />
      </div>

      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
          Driver End Window
        </label>
        <input onChange={(e)=>setDriverEndWindow(e.target.value)} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
          id="grid-password" type="time" name="driver_end_window" />
      </div> */}

      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
          Select First Solution Strategy
        </label>
      {/* Dropdown for first solution strategy */}
        <select onChange={(e)=>setFirstSolutionStrategy(e.target.value)} className="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="grid-state">
          <option value="AUTOMATIC">AUTOMATIC</option>
          <option value="PATH_CHEAPEST_ARC">PATH_CHEAPEST_ARC</option>
          <option value="PATH_MOST_CONSTRAINED_ARC">PATH_MOST_CONSTRAINED_ARC</option>
          <option value="SAVINGS">SAVINGS</option>
          <option value="SWEEP">SWEEP</option>
          <option value="CHRISTOFIDES">CHRISTOFIDES</option>
          
        </select>
      </div>

      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
          Select Route Improvement Strategy
        </label>
        <select onChange={(e)=>setMetaHeuristic(e.target.value)} className="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="grid-state">
          <option value="AUTOMATIC">AUTOMATIC</option>
          <option value="GUIDED_LOCAL_SEARCH">GUIDED_LOCAL_SEARCH</option>
          <option value="GREEDY_DESCENT">GREEDY_DESCENT</option>
          <option value="TABU_SEARCH">TABU_SEARCH</option>
          <option value="SIMULATED_ANNEALING">SIMULATED_ANNEALING</option>
          <option value="GENERIC_TABU_SEARCH">GENERIC_TABU_SEARCH</option>
        </select>
      </div>

      <div className='w-full mb-2 flex justify-center flex-col md:flex-col lg:flex-col'>
            {/* Batch menu button */} 
            <div className="w-full px-3">
              <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
                Number of Bags of Dim (60 x 60 x 100 cms)
              </label>
              <input onChange={setMyData} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="grid-password" type="number" name="bagNum1" />

            </div>
            <div className="w-full px-3">
              <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
                Number of Bags of Dim (80 x 80 x 100 cms)
              </label>
              <input onChange={setMyData} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="grid-password" type="number" name="bagNum2"/>

            </div>
      </div>

      <div className="flex flex-wrap -mx-3 mb-2">

        <button className='bg-blue-300 hover:bg-blue-400 active:bg-blue-300 p-4 m-2 mx-auto rounded' type='submit'>
          Add Information
        </button>

      </div>

    </form>
    <form onSubmit={addPickup} className="w-full max-w-2xl lg:mx-auto md:mx-auto bg-orange-200 p-4 m-4 mx-auto border-8 border-orange-100 rounded">
      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-last-name">
          Dynamic Pickup Addresses
        </label>
        <input onChange={(e)=>{setPickUpAdd(e.target.files[0])}} className="appearance-none bl  ock w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
          id="grid-last-name" type="file"
          name="pickup_addresses"
          accept=".xls,.xlsx,.csv,.txt" />
      </div>

      <div className="p-2 m-2">
        <label className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2" htmlFor="grid-password">
          Time at which the pickup_addresses file are to be added
        </label>
        {/* Input needs to only of time */}
        <input onChange={(e)=>{setTime(e.target.value)}} className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
          id="grid-password" type="time" name="time" />
      </div>

      <div className="flex flex-wrap -mx-3 mb-2">

        <button className='bg-blue-300 hover:bg-blue-400 active:bg-blue-300 p-4 m-2 mx-auto rounded' type='submit'>
          Add Pickup Addresses
        </button>

      </div>
    </form>
    </>
  )
}

export default Data