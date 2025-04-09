import React, { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./PredictionResult.css";
import JobOpenings from "./JobOpenings";
import CourseRecommendations from "./CourseRecommendations";

function PredictionResult() {
  const location = useLocation();
  const result = location.state;
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollContainerRef = useRef(null);
  const [showJobs, setShowJobs] = useState(false);
  const [showCourses, setShowCourses] = useState(false);

  const cards = [
    {
      id: "domain",
      icon: "🌐",
      title: "Domain",
      content: result?.domain || "N/A",
    },
    {
      id: "skills",
      icon: "🛠️",
      title: "Predicted Skills",
      content: result?.predicted_skills || "N/A",
    },
    {
      id: "role",
      icon: "👨‍💼",
      title: "Predicted Role",
      content: result?.predicted_role || "N/A",
    },
    {
      id: "resume",
      icon: "📄",
      title: "Resume Skills",
      content:
        result?.resume_skills?.length > 0
          ? result.resume_skills.join(", ")
          : "None detected",
    },
    {
      id: "missing",
      icon: "⚠️",
      title: "Missing Skills",
      content:
        result?.missing_skills?.length > 0
          ? result.missing_skills.join(", ")
          : "No missing skills",
    },
    {
      id: "recommendation",
      icon: "🎓",
      title: "Recommendations",
      content: `📘 Course: ${
        result?.recommendation?.course || "N/A"
      }\n📜 Certificate: ${result?.recommendation?.certificate || "N/A"}`,
    },
  ];

  const scrollToCard = (index) => {
    const container = scrollContainerRef.current;
    const cardWidth = container.offsetWidth / 3;
    container.scrollTo({ left: index * cardWidth, behavior: "smooth" });
    setCurrentIndex(index);
  };

  const handleGoBack = () => navigate("/domain-check");

  useEffect(() => {
    scrollToCard(0);
  }, []);

  return (
    <div className="result-container">
      <h1 className="result-heading">🎯 Your Personalized Career Snapshot</h1>

      <div className="card-scroll-container" ref={scrollContainerRef}>
        {cards.map((card, index) => (
          <div className="stylish-card fade-in" key={card.id}>
            <h3>
              {card.icon} {card.title}
            </h3>
            <p style={{ whiteSpace: "pre-line" }}>{card.content}</p>
          </div>
        ))}
      </div>

      <div className="dots-container">
        {cards.map((_, index) => (
          <span
            key={index}
            className={`dot ${currentIndex === index ? "active" : ""}`}
            onClick={() => scrollToCard(index)}
          ></span>
        ))}
      </div>

      <div className="button-group">
        <button
          onClick={() => {
            setShowJobs(!showJobs);
            setShowCourses(false); // Close courses when Jobs is opened
          }}
          className="apply-btn"
        >
          💼 View Job Openings
        </button>

        <button
          onClick={() => {
            setShowCourses(!showCourses);
            setShowJobs(false); // Close jobs when Courses is opened
          }}
          className="apply-btn"
        >
          📚 Apply for Courses
        </button>
      </div>

      {showJobs && <JobOpenings jobRole={result?.predicted_role} />}

      {showCourses && result?.recommendation?.course && (
        <CourseRecommendations courseQuery={result.recommendation.course} />
      )}
    </div>
  );
}

export default PredictionResult;
