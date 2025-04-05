// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import DomainCheck from "./components/DomainCheck";
import SkillPrediction from "./components/SkillPrediction";
import PredictionResult from "./components/PredictionResult";

import './App.css';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<DomainCheck />} />
        <Route path="/skill-predict" element={<SkillPrediction />} />
        <Route path="/result" element={<PredictionResult />} />
      </Routes>
    </Router>
  );
}

export default App;