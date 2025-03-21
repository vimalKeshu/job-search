import React from 'react';
import {Route, Routes } from "react-router-dom" 
import Search from './search/Search';
import About from './about/About';
import Footer from './footer/Footer';
import Header from './header/Header';

function App() {
  return ( 
    <div> 
      <Header />
      <Routes>
        <Route exact path="/" element={<Search/> } />
        <Route path="/About" element={<About/> } />
      </Routes>
      <Footer />
    </div> 
  )
}

export default App;
