import React, { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./PredictionResult.css";
import JobOpenings from "./JobOpenings";
import CourseRecommendations from "./CourseRecommendations";

function PredictionResult() {
  const location = useLocation();
  const result   = location.state;
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollContainerRef = useRef(null);
  const [showJobs,    setShowJobs]    = useState(false);
  const [showCourses, setShowCourses] = useState(false);

  // Normalise data — backend may return skills as string or array
  const predictedSkills = result?.predicted_skills
    ? (Array.isArray(result.predicted_skills)
        ? result.predicted_skills.join(", ")
        : result.predicted_skills)
    : "N/A";

  const resumeSkills = result?.resume_skills?.length > 0
    ? (Array.isArray(result.resume_skills) ? result.resume_skills.join(", ") : result.resume_skills)
    : "None detected";

  const missingSkills = result?.missing_skills?.length > 0
    ? (Array.isArray(result.missing_skills) ? result.missing_skills.join(", ") : result.missing_skills)
    : "No missing skills identified";

  const cards = [
    { id: "domain",         icon: "🌐", title: "Domain",            content: result?.domain || "N/A" },
    { id: "skills",         icon: "🛠️", title: "Predicted Skills",  content: predictedSkills },
    { id: "role",           icon: "👨‍💼", title: "Predicted Role",   content: result?.predicted_role || "N/A" },
    { id: "resume",         icon: "📄", title: "Resume Skills",      content: resumeSkills },
    { id: "missing",        icon: "⚠️", title: "Missing Skills",    content: missingSkills },
    {
      id: "recommendation", icon: "🎓", title: "Recommendations",
      content: `📘 Course: ${result?.recommendation?.course || "N/A"}\n📜 Certificate: ${result?.recommendation?.certificate || "N/A"}`,
    },
  ];

  const scrollToCard = (index) => {
    const container = scrollContainerRef.current;
    if (!container) return;
    const cardWidth = container.offsetWidth / 3;
    container.scrollTo({ left: index * cardWidth, behavior: "smooth" });
    setCurrentIndex(index);
  };

  useEffect(() => { scrollToCard(0); }, []); // eslint-disable-line

  if (!result) {
    return (
      <div className="container" style={{ textAlign: "center" }}>
        <h2>No Results Found</h2>
        <p>Please upload and analyze your resume first.</p>
        <button onClick={() => navigate("/domain-check")}>← Analyze Resume</button>
      </div>
    );
  }

  return (
    <div className="result-container">
      <h1 className="result-heading">🎯 Your Personalized Career Snapshot</h1>

      <div className="card-scroll-container" ref={scrollContainerRef}>
        {cards.map((card) => (
          <div className="stylish-card fade-in" key={card.id}>
            <h3>{card.icon} {card.title}</h3>
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
          />
        ))}
      </div>

      <div className="button-group">
        <button
          className="apply-btn"
          onClick={() => { setShowJobs(!showJobs); setShowCourses(false); }}
        >
          💼 View Job Openings
        </button>
        <button
          className="apply-btn"
          onClick={() => { setShowCourses(!showCourses); setShowJobs(false); }}
        >
          📚 Apply for Courses
        </button>
        <button
          className="apply-btn"
          onClick={() => navigate("/mock-interview")}
          style={{ background: "#10b981" }}
        >
          🎤 Practice Interview
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
