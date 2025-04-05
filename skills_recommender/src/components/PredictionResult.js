import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./PredictionResult.css";

function PredictionResult() {
  const location = useLocation();
  const result = location.state;
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate("/domain-check"); // Navigate back to DomainCheck.js page
  };

  return (
    <div className="result-container">
      <div className="result-card">
        <h2 className="result-title">Prediction Summary</h2>

        {result ? (
          <>
            <div className="grid-container">
              {/* Domain Card */}
              <div className="card domain-card">
                <h3>Domain</h3>
                <p>{result.domain}</p>
              </div>

              {/* Predicted Skills Card */}
              <div className="card skills-card">
                <h3>Predicted Skills</h3>
                <p>{result.predicted_skills}</p>
              </div>

              {/* Predicted Role Card */}
              <div className="card role-card">
                <h3>Predicted Role</h3>
                <p>{result.predicted_role}</p>
              </div>

              {/* Resume Skills Card */}
              <div className="card resume-skills-card">
                <h3>Resume Skills</h3>
                <p>
                  {result.resume_skills?.length
                    ? result.resume_skills.join(", ")
                    : "None detected"}
                </p>
              </div>

              {/* Missing Skills Card */}
              <div className="card missing-skills-card">
                <h3>Missing Skills</h3>
                <p>
                  {result.missing_skills?.length
                    ? result.missing_skills.join(", ")
                    : "No missing skills"}
                </p>
              </div>

              {/* Recommendations Card */}
              <div className="card recommendations-card">
                <h3>Recommendations</h3>
                <ul>
                  <li>
                    <strong>Course:</strong> {result.recommendation?.course || "Not available"}
                  </li>
                  <li>
                    <strong>Certificate:</strong> {result.recommendation?.certificate || "Not available"}
                  </li>
                </ul>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="action-buttons">
              <button onClick={handleGoBack} className="back-button">
                Go Back
              </button>
              <div className="apply-links">
                <a href="/apply-job" className="apply-link">Apply for Jobs</a>
                <a href="/apply-course" className="apply-link">Apply for Courses</a>
              </div>
            </div>
          </>
        ) : (
          <p className="no-data">No data to display.</p>
        )}
      </div>
    </div>
  );
}

export default PredictionResult;
