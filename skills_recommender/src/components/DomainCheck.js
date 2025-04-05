import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./DomainCheck.css";

function DomainCheck() {
  const [resumeFile, setResumeFile] = useState(null);
  const [domain, setDomain] = useState("");
  const [showPopup, setShowPopup] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [isProceeding, setIsProceeding] = useState(false); // Track if proceeding
  const navigate = useNavigate();

  const handleFileChange = (e) => setResumeFile(e.target.files[0]);

  const handleDetectDomain = async () => {
    if (!resumeFile) return alert("Please upload a PDF resume.");

    const formData = new FormData();
    formData.append("resume", resumeFile);

    try {
      const res = await axios.post("http://localhost:5000/detect_domain", formData);
      setDomain(res.data.domain);
      setShowPopup(true);  // Show the domain pop-up
    } catch (err) {
      console.error(err);
      alert("Failed to detect domain. Try again.");
    }
  };

  const handlePopupClick = () => {
    setShowConfirmation(true);  // Show the confirmation after clicking the pop-up
  };

  const handleProceed = () => {
    setIsProceeding(true);
    setTimeout(() => {
      navigate("/skill-predict", { state: { domain, resume: resumeFile } });
    }, 1500); // Simulating a slight delay before navigating
  };

  return (
    <div className="home-container">
      <section className="hero">
        <h1>Welcome to SmartCareer</h1>
        <p>Your personalized career path starts here!</p>
      </section>

      <div className="upload-card">
        <h2>Upload Your Resume</h2>
        <p>Let us analyze and guide your career journey</p>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <button className="detect-btn" onClick={handleDetectDomain}>Detect Domain</button>
      </div>

      {showPopup && (
        <div className="popup" onClick={handlePopupClick}>
          <p>🎯 Detected Domain: <strong>{domain}</strong></p>
          {showConfirmation && (
            <div className="popup-confirmation">
              <p>Can I show your analysis?</p>
              <button className="proceed-btn" onClick={handleProceed}>Proceed</button>
            </div>
          )}
        </div>
      )}

      <section id="testimonials" className="testimonials">
        <h3>What users say</h3>
        <div className="testimonial-card">SmartCareer helped me find skills I never thought I needed. 💼</div>
        <div className="testimonial-card">Super easy to use and spot on with suggestions! 🚀</div>
      </section>

      <footer className="footer">
        <p>&copy; 2025 SmartCareer. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default DomainCheck;
