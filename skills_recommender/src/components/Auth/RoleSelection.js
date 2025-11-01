import React from "react";
import { useNavigate } from "react-router-dom";
import "./RoleSelection.css";

function RoleSelection() {
  const navigate = useNavigate();

  const selectRole = (role) => {
    // Store role in localStorage
    localStorage.setItem('userRole', role);
    
    if (role === 'recruiter') {
      navigate('/recruiter-dashboard');
    } else {
      navigate('/');
    }
  };

  return (
    <div className="role-selection-container">
      <div className="role-header">
        <h1 className="role-title">Welcome to SmartCareer</h1>
        <p className="role-subtitle">Choose your account type to continue</p>
      </div>

      <div className="role-cards">
        <div className="role-card candidate-card" onClick={() => selectRole('candidate')}>
          <div className="role-icon">🎓</div>
          <h2>Job Seeker / Candidate</h2>
          <p>Find jobs, optimize resume, practice interviews</p>
          <ul className="role-features">
            <li>✓ Resume Analysis</li>
            <li>✓ Mock Interviews</li>
            <li>✓ Job Recommendations</li>
            <li>✓ Skill Gap Analysis</li>
          </ul>
          <button className="role-button candidate-button">
            Continue as Candidate
          </button>
        </div>

        <div className="role-card recruiter-card" onClick={() => selectRole('recruiter')}>
          <div className="role-icon">💼</div>
          <h2>Recruiter / Employer</h2>
          <p>Post jobs, search candidates, shortlist profiles</p>
          <ul className="role-features">
            <li>✓ Post Job Openings</li>
            <li>✓ Smart Candidate Search</li>
            <li>✓ AI Resume Matching</li>
            <li>✓ Shortlist Management</li>
          </ul>
          <button className="role-button recruiter-button">
            Continue as Recruiter
          </button>
        </div>
      </div>
    </div>
  );
}

export default RoleSelection;