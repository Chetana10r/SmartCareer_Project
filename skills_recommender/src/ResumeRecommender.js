import React, { useState } from "react";
import axios from "axios";
import { FaFileUpload, FaSpinner, FaCheckCircle } from "react-icons/fa";
import "./ResumeRecommender.css";

function ResumeRecommender() {
  const [file, setFile] = useState(null);
  const [jobRole, setJobRole] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle file upload change
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // Handle job role input change
  const handleRoleChange = (event) => {
    setJobRole(event.target.value);
  };

  // Submit the resume and job role to the backend
  const submitAnalysis = async () => {
    if (!file || !jobRole) {
      alert("Please upload a resume and enter the job role.");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_role", jobRole);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error processing resume:", error);
      alert("Error processing your resume. Please try again.");
    }
    setLoading(false);
  };

  // If result exists, show the output screen only
  if (result) {
    return (
      <div className="output-container">
        <h2 className="output-title">Analysis Result</h2>
        <div className="output-card">
          <h3 className="output-header">
            <FaCheckCircle color="#4caf50" size={24} /> Predicted Job Category: {result.Predicted_Job_Category}
          </h3>
          <p><strong>Extracted Skills:</strong> {result.Extracted_Skills.join(", ")}</p>
          <p><strong>Missing Skills:</strong> {result.Missing_Skills.join(", ")}</p>
          <h4>Recommended Courses:</h4>
          <ul>
            {result.Recommended_Courses.map((course, index) => (
              <li key={index}>{course}</li>
            ))}
          </ul>
          {result.Recommended_Certifications && result.Recommended_Certifications.length > 0 && (
            <>
              <h4>Recommended Certifications:</h4>
              <ul>
                {result.Recommended_Certifications.map((cert, index) => (
                  <li key={index}>{cert}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
    );
  }

  // Input form view
  return (
    <div className="input-container">
      <h2 className="input-title">Resume Skill Recommender</h2>
      <div className="input-group">
        <label htmlFor="file-upload" className="custom-file-upload">
          <FaFileUpload size={20} /> Upload Resume (PDF)
        </label>
        <input
          id="file-upload"
          type="file"
          onChange={handleFileChange}
          accept="application/pdf"
          className="file-input"
        />
      </div>
      <div className="input-group">
        <input
          type="text"
          placeholder="Enter the Job Role you are applying for"
          value={jobRole}
          onChange={handleRoleChange}
          className="role-input"
        />
      </div>
      <button
        className="submit-button"
        onClick={submitAnalysis}
        disabled={loading}
      >
        {loading ? (
          <span>
            <FaSpinner className="spinner" /> Processing...
          </span>
        ) : (
          "Check Analysis"
        )}
      </button>
    </div>
  );
}

export default ResumeRecommender;
