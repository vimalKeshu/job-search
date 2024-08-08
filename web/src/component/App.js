import React from 'react';
import {Route, Routes } from "react-router-dom" 
import Search from './search/Search';
import About from './about/About';

function App() {
  return ( 
    <div> 
      <Routes>
        <Route exact path="/" element={<Search/> } />
        <Route path="/About" element={<About/> } />
      </Routes>
    </div> 
  )
}

export default App;
