// App.js - Updated for Role-based Layout
import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";

import Navbar from "./components/Navbar";
import Home from "./components/Home";
import DomainCheck from "./components/DomainCheck";
import SkillPrediction from "./components/SkillPrediction";
import PredictionResult from "./components/PredictionResult";
import About from "./components/About";
import Footer from "./components/Footer";
import Testimonials from "./components/Testimonials";
import Contact from "./components/Contact";
import ResumeOptimizer from "./components/ResumeOptimizer";
import InterviewSetup from "./components/MockInterview/InterviewSetup";
import InterviewSession from "./components/MockInterview/InterviewSession";
import InterviewFeedback from "./components/MockInterview/InterviewFeedback";
import InterviewHistory from "./components/MockInterview/InterviewHistory";

// Mock Test
import SubjectSelection from "./components/MockTest/SubjectSelection";
import MockTestQuiz from "./components/MockTest/MockTestQuiz";
import ResultPage from "./components/MockTest/ResultPage";
import TestHistory from "./components/MockTest/TestHistory";

// Recruiter
import RoleSelection from "./components/Auth/RoleSelection";
import Login from "./components/Auth/Login";
import RecruiterDashboard from "./components/Recruiter/RecruiterDashboard";
import JobPosting from "./components/Recruiter/JobPosting";
import JobListings from "./components/Recruiter/JobListings";
import CandidateSearch from "./components/Recruiter/CandidateSearch";
import ResumeMatching from "./components/Recruiter/ResumeMatching";
import RecruiterNavbar from "./components/Recruiter/RecruiterNavbar";
import ShortlistManager from "./components/Recruiter/ShortlistManager";

import "./App.css";

function LayoutWrapper({ children }) {
  const location = useLocation();

  // Show Recruiter Navbar only on recruiter pages
  const isRecruiterPage = location.pathname.startsWith("/recruiter");

  return (
    <div className="app-container">
      {!isRecruiterPage && <Navbar />}
      {isRecruiterPage && <RecruiterNavbar />}

      <div className="content-wrap">{children}</div>

      {!isRecruiterPage && <Footer />}
    </div>
  );
}

function App() {
  return (
    <Router>
      <LayoutWrapper>
        <Routes>
          {/* Candidate / General Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/domain-check" element={<DomainCheck />} />
          <Route path="/skill-predict" element={<SkillPrediction />} />
          <Route path="/result" element={<PredictionResult />} />
          <Route path="/about" element={<About />} />
          <Route path="/testimonials" element={<Testimonials />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/resume-optimizer" element={<ResumeOptimizer />} />

          {/* Interview */}
          <Route path="/mock-interview" element={<InterviewSetup />} />
          <Route path="/interview-session" element={<InterviewSession />} />
          <Route path="/interview-feedback" element={<InterviewFeedback />} />
          <Route path="/interview-history" element={<InterviewHistory />} />

          {/* Mock Test */}
          <Route path="/mock-test" element={<SubjectSelection />} />
          <Route path="/mock-test/quiz" element={<MockTestQuiz />} />
          <Route path="/mock-test/result" element={<ResultPage />} />
          <Route path="/mock-test/history" element={<TestHistory />} />

          {/* Auth */}
          <Route path="/role-selection" element={<RoleSelection />} />
          <Route path="/login" element={<Login />} />

          {/* Recruiter */}
          <Route path="/recruiter-dashboard" element={<RecruiterDashboard />} />
          <Route path="/post-job" element={<JobPosting />} />
          <Route path="/search-candidates" element={<CandidateSearch />} />
          <Route path="/resume-matching" element={<ResumeMatching />} />
          <Route path="/job-listings" element={<JobListings />} />
          <Route path="/shortlist-manager" element={<ShortlistManager />} />
        </Routes>
      </LayoutWrapper>
    </Router>
  );
}

export default App;
