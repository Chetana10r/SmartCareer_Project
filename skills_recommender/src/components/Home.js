import React from "react";
import { Link } from "react-router-dom";
import { FaRocket, FaMagic, FaFileAlt } from "react-icons/fa";
import "./Home.css";

function Home() {
  return (
    <div className="home-container">
      <div className="overlay"></div>

      <div className="home-content">
        <h1 className="home-title">
          <FaRocket className="icon" /> Welcome to <span>SmartCareer</span>
        </h1>

        <p className="home-description">
          Empower your journey with <strong>AI-driven tools</strong> that shape your career.
          Explore smart predictions, resume insights, and personalized learning paths — 
          all in one place.
        </p>

        <div className="home-buttons">
          <Link to="/domain-check" className="career-btn">
            <FaMagic /> Check My Career
          </Link>
          <Link to="/resume-optimizer" className="career-btn secondary">
            <FaFileAlt /> Resume Optimizer
          </Link>
        </div>

        <p className="tagline">✨ Build. Learn. Grow with SmartCareer.</p>
      </div>
    </div>
  );
}

export default Home;
