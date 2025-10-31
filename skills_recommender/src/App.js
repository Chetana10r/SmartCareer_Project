// App.js - UPDATED VERSION
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
import ResumeOptimizer from "./components/ResumeOptimizer";
import InterviewSetup from "./components/MockInterview/InterviewSetup";
import InterviewSession from "./components/MockInterview/InterviewSession";
import InterviewFeedback from "./components/MockInterview/InterviewFeedback";
import InterviewHistory from "./components/MockInterview/InterviewHistory";

// NEW: Mock Test Components
import SubjectSelection from "./components/MockTest/SubjectSelection";
import MockTestQuiz from "./components/MockTest/MockTestQuiz";
import ResultPage from "./components/MockTest/ResultPage";
import TestHistory from "./components/MockTest/TestHistory";

import "./App.css";

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
            <Route path="/resume-optimizer" element={<ResumeOptimizer />} />
            
            {/* Interview Routes */}
            <Route path="/mock-interview" element={<InterviewSetup />} />
            <Route path="/interview-session" element={<InterviewSession />} />
            <Route path="/interview-feedback" element={<InterviewFeedback />} />
            <Route path="/interview-history" element={<InterviewHistory />} />
            
            {/* NEW: Mock Test Routes */}
            <Route path="/mock-test" element={<SubjectSelection />} />
            <Route path="/mock-test/quiz" element={<MockTestQuiz />} />
            <Route path="/mock-test/result" element={<ResultPage />} />
            <Route path="/mock-test/history" element={<TestHistory />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;