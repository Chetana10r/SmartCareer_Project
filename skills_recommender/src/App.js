// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Home from "./components/Home";
import DomainCheck from "./components/DomainCheck";
import SkillPrediction from "./components/SkillPrediction";
import PredictionResult from "./components/PredictionResult";
import About from "./components/About"; 
import Footer from "./components/Footer";
import Testimonials from "./components/Testimonials";
import Contact from "./components/Contact";
import Login from "./components/Login";


import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <div className="content-wrap">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/domain-check" element={<DomainCheck />} />
            <Route path="/skill-predict" element={<SkillPrediction />} />
            <Route path="/result" element={<PredictionResult />} />
            <Route path="/about" element={<About />} /> 
            <Route path="/testimonials" element={<Testimonials />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
