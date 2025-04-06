import React from "react";
import { Link } from "react-router-dom";
import { FaRocket, FaMagic } from "react-icons/fa";
import "./Home.css";

function Home() {
  return (
    <div className="home-container">
      <div className="overlay"></div>
      <div className="home-content animated-fade-in">
        <h1 className="home-title gradient-text">
          <FaRocket className="icon-bounce" /> Welcome to SmartCareer
        </h1>
        <p className="home-description">
          Empower your career with AI-driven skill prediction, personalized role
          recommendations, and curated learning paths.
        </p>
        <div className="home-buttons">
          <Link to="/domain-check" className="career-btn">
            <FaMagic /> Check My Career
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;
