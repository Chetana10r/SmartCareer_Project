import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./DomainCheck.css";

function DomainCheck() {
  const navigate   = useNavigate();
  const [resumeFile, setResumeFile] = useState(null);
  const [domain,     setDomain]     = useState("");
  const [detecting,  setDetecting]  = useState(false);
  const [detected,   setDetected]   = useState(false);
  const [proceeding, setProceeding] = useState(false);
  const [error,      setError]      = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.type !== "application/pdf") {
      setError("Please upload a valid PDF file.");
      setResumeFile(null);
      return;
    }
    setError("");
    setResumeFile(file);
    setDetected(false);
    setDomain("");
  };

  const handleDetectDomain = async () => {
    if (!resumeFile) { setError("Please select a PDF resume first."); return; }
    setDetecting(true);
    setError("");
    setDetected(false);

    const formData = new FormData();
    formData.append("resume", resumeFile);

    try {
      const res  = await fetch("http://localhost:5000/detect_domain", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Detection failed");
      setDomain(data.domain);
      setDetected(true);
    } catch (err) {
      setError("Failed to detect domain: " + err.message);
    } finally {
      setDetecting(false);
    }
  };

  const handleProceed = () => {
    setProceeding(true);
    setTimeout(() => {
      navigate("/skill-predict", { state: { domain, resume: resumeFile } });
    }, 600);
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

        {/* Hidden file input + styled label */}
        <input
          id="file-upload"
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        <label htmlFor="file-upload" className="custom-upload-label">
          📄 Choose PDF Resume
        </label>

        {resumeFile && (
          <p className="file-name">
            ✅ Selected: <strong>{resumeFile.name}</strong>{" "}
            <span style={{ color: "#888", fontSize: "0.82rem" }}>
              ({(resumeFile.size / 1024).toFixed(1)} KB)
            </span>
          </p>
        )}

        {error && (
          <p style={{ color: "#e74c3c", marginTop: "0.5rem", fontSize: "0.88rem" }}>
            ⚠️ {error}
          </p>
        )}

        <button
          className="detect-btn"
          onClick={handleDetectDomain}
          disabled={!resumeFile || detecting}
          style={{ opacity: (!resumeFile || detecting) ? 0.65 : 1 }}
        >
          {detecting ? "⏳ Detecting..." : "🔍 Detect Domain"}
        </button>
      </div>

      {detected && (
        <div className="popup">
          <p>🎯 Detected Domain: <strong>{domain}</strong></p>
          <p style={{ fontSize: "0.88rem", color: "#555", marginTop: "0.4rem" }}>
            {domain === "IT"
              ? "Your resume is in the IT/Technology domain."
              : "Your resume is in the Non-IT domain."}
          </p>
          <div className="popup-confirmation">
            <p>Would you like to see a personalized skill analysis?</p>
            <button
              className="proceed-btn"
              onClick={handleProceed}
              disabled={proceeding}
            >
              {proceeding ? "⏳ Processing..." : "✅ Proceed with Analysis"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DomainCheck;
