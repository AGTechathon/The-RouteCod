import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./components/Home";
import { Toaster } from "react-hot-toast";
import ServiceSection from "./components/ServiceSection";
import Reviews from "./components/Reviews";
function App() {
  return (
    <Router>
      <div className="relative">
        <Toaster position="top-right" />
        <Routes>
          <Route
            path="/"
            element={
              <>
                <Navbar />
                <Home />
                <ServiceSection />
                <Reviews />
              </>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
