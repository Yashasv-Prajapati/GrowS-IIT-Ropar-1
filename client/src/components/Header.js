import React from 'react'
import { Navbar, Nav } from 'react-bootstrap'
import { useState, useEffect } from'react'

export default function Header() {
  const [flag,setFlag ] = useState(0)

// 1 2 3 4

  useEffect(()=>{

  })

  return (
    <>
    <Navbar bg="light" expand="lg" className='p-2 mb-4'>
        <Navbar.Brand href="/">Grow-S</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        {/* <Navbar.Collapse id="basic-navbar-nav"> */}
            <Nav className="m-auto">
                <Nav.Link href="/scan-tool">Scan Tool</Nav.Link>
                <Nav.Link href="/admin">Admin</Nav.Link>
                <Nav.Link href="/driver">Driver</Nav.Link>
                <Nav.Link href="/data">Data</Nav.Link>
                <Nav.Link href="/upload">Upload Data</Nav.Link>
            </Nav>
        {/* </Navbar.Collapse> */}
    </Navbar>
    </>
  )
}
