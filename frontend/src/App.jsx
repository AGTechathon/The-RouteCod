import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import { Toaster } from 'react-hot-toast';


function App() {
  return (
    <Router>
      <div className="relative">
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={
            <>
              <Navbar />
              <Home />
              
            </>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
