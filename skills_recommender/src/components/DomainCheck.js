import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./DomainCheck.css";

function DomainCheck() {
  const [resumeFile, setResumeFile] = useState(null);
  const [domain, setDomain] = useState("");
  const [showPopup, setShowPopup] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [isProceeding, setIsProceeding] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setResumeFile(e.target.files[0]);
    setShowPopup(false);
    setShowConfirmation(false);
    setDomain("");
  };

  const handleDetectDomain = async () => {
    if (!resumeFile) {
      alert("Please upload a PDF resume.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resumeFile);

    try {
      const res = await axios.post("http://localhost:5000/detect_domain", formData);
      setDomain(res.data.domain);
      setShowPopup(true);
    } catch (err) {
      console.error(err);
      alert("Failed to detect domain. Try again.");
    }
  };

  const handlePopupClick = () => {
    setShowConfirmation(true);
  };

  const handleProceed = () => {
    setIsProceeding(true);
    setTimeout(() => {
      navigate("/skill-predict", { state: { domain, resume: resumeFile } });
    }, 1500);
  };

  return (
    <div className="domain-container">
      <section className="hero">
        <h1>🎓 Welcome to <span className="highlight-text">SmartCareer</span></h1>
        <p>Your personalized AI-powered career path starts here 🚀</p>
      </section>

      <div className="upload-card">
        <h2>📌 Upload Your Resume for Domain Detection</h2>
        <p>Let us analyze and guide your career journey based on your skills!</p>

        <label htmlFor="file-upload" className="custom-upload-label">
          📄 Choose PDF Resume
        </label>
        <input
          id="file-upload"
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
        />

        {resumeFile && (
          <p className="file-name">
            ✅ Selected File: <strong>{resumeFile.name}</strong>
          </p>
        )}

        <button className="detect-btn" onClick={handleDetectDomain}>
          🔍 Detect Domain
        </button>
      </div>

      {showPopup && (
        <div className="popup" onClick={handlePopupClick}>
          <p>🎯 Detected Domain: <strong>{domain}</strong></p>
          {showConfirmation && (
            <div className="popup-confirmation">
              <p>Would you like to see a personalized skill analysis?</p>
              <button className="proceed-btn" onClick={handleProceed}>
                {isProceeding ? "Loading..." : "✅ Proceed"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DomainCheck;
