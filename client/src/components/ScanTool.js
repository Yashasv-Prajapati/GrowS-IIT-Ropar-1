import React from 'react'
// import shorid from 'shortid';
import shortid from 'shortid';

export default function ScanTool() {
  
  const arr = [
    {
      'skuNo': '69',
      'name': "yashasav 1",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
    {
      'skuNo': '69',
      'name': "yashasav 2",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
    {
      'skuNo': '69',
      'name': "yashasav 3",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
    {
      'skuNo': '69',
      'name': "yashasav 4",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
    {
      'skuNo': '69',
      'name': "yashasav 5",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
    {
      'skuNo': '69',
      'name': "yashasav 6",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
    {
      'skuNo': '69',
      'name': "yashasav 7",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
    {
      'skuNo': '69',
      'name': "yashasav 8",
      'address': 'IIT Roparfkaadsnvkadsnvknadadiovnkadfnvndfonvkdfnvondfvndfklnvdfnkvlndfionvjdfnnviojfks',
      'volume': '69 cubic cm',
      'length': '69 cm',
      'breadth': '69 cm',
      'height': '69 cm',
      'weight': '69 kg',
    },
  ]
  
  
  
  
  return (
    <div className='select-none lg:grid lg:grid-cols-3 lg:grid-row-3 flex flex-col justify-center items-center'>
      {/* search box */}


      {/* cards with latest first  */}

      {
        arr.map((item, index)=>(
          <div key={shortid.generate()} >
            {/* Test Card */}
              <div className="max-w-sm m-4 p-4 bg-gradient-to-r from-green-300 to-green-400 hover:bg-green-400 active:bg-green-300 rounded overflow-hidden shadow-lg">
                  <div className = "px-2 py-1">
                      <div className = "font-bold text-xl mb-2 text-center capitalize">{item.name}</div>
                      
                      <div className="flex flex-row justify-between items-center ">
                        <p className = "text-gray-700 text-xl p-2">
                            skuNo.:
                        </p>
                        <p className = "bg-gray-200 rounded my-2 p-2 text-gray-700 text-sm w-2/3 break-all">
                           {item.skuNo}
                        </p>
                      </div>

                      <div className="flex flex-row justify-between items-center">
                        <p className = "text-gray-700 text-xl p-2">
                            Volume:
                        </p>
                        <p className = "bg-gray-200 rounded my-2 p-2 text-gray-700 text-sm w-2/3 break-all">
                           {item.volume}
                        </p>
                      </div>

                      <div className="flex flex-row justify-between items-center w-3/2">
                        <p className = "text-gray-700 text-xl p-2">
                            Length:
                        </p>
                        <p className = "bg-gray-200 rounded my-2 p-2 text-gray-700 text-sm w-2/3 break-all">
                            {item.length}
                        </p>
                      </div>

                      <div className="flex flex-row justify-between items-center w-3/2">
                        <p className = "text-gray-700 text-xl p-2">
                            Breadth:
                        </p>
                        <p className = "bg-gray-200 rounded my-2 p-2 text-gray-700 text-sm w-2/3 break-all">
                            {item.breadth}
                        </p>
                      </div>

                      <div className="flex flex-row justify-between items-center w-3/2">
                        <p className = "text-gray-700 text-xl p-2">
                            Height:
                        </p>
                        <p className = "bg-gray-200 rounded my-2 p-2 text-gray-700 text-sm w-2/3 break-all">
                            {item.height}
                        </p>
                      </div>

                      <div className="flex flex-row justify-between items-center w-3/2">
                        <p className = "text-gray-700 text-xl p-2">
                          Weight:
                        </p>
                        <p className = "bg-gray-200 rounded my-2 p-2 text-gray-700 text-sm w-2/3 break-all">
                          {item.weight}
                        </p>
                      </div>
                  </div>
              </div>
          </div>
        ))
      }

    </div>
  )
}