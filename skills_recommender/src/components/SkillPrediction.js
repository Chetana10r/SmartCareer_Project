import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

function SkillPrediction() {
  const location  = useLocation();
  const navigate  = useNavigate();
  const [status,  setStatus]  = useState("Uploading resume...");
  const [errMsg,  setErrMsg]  = useState("");
  const [failed,  setFailed]  = useState(false);

  const { domain, resume } = location.state || {};

  useEffect(() => {
    if (!domain || !resume) {
      navigate("/domain-check");
      return;
    }
    runPrediction();
    // eslint-disable-next-line
  }, []);

  const runPrediction = async () => {
    try {
      setStatus("Analyzing resume content...");
      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("domain",  domain);

      setStatus("Running AI skill prediction...");
      const response = await fetch("http://localhost:5000/proceed_prediction", {
        method: "POST",
        body:   formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Prediction failed");

      setStatus("Done! Loading results...");
      setTimeout(() => navigate("/result", { state: { ...data, domain } }), 500);

    } catch (err) {
      console.error("Skill prediction error:", err);
      setErrMsg(err.message || "An unexpected error occurred.");
      setFailed(true);
    }
  };

  if (failed) {
    return (
      <div className="container" style={{ textAlign: "center" }}>
        <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>⚠️</div>
        <h2 style={{ color: "#e74c3c" }}>Prediction Failed</h2>
        <p style={{ color: "#555", margin: "0.8rem 0" }}>{errMsg}</p>
        <p style={{ color: "#888", fontSize: "0.82rem", marginBottom: "1.2rem" }}>
          The Flask server may not be running, or the ML models are not loaded. Check the terminal for errors.
        </p>
        <button onClick={() => navigate("/domain-check")}>← Try Again</button>
      </div>
    );
  }

  return (
    <div className="container" style={{ textAlign: "center" }}>
      <div style={{
        width: 48, height: 48, border: "5px solid #e2e8f0",
        borderTopColor: "#0a74da", borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
        margin: "0 auto 1rem",
        display: "inline-block"
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <h2>Processing Your Resume</h2>
      <p style={{ color: "#0a74da", fontWeight: 600, marginTop: "0.5rem" }}>{status}</p>
      <p style={{ color: "#888", fontSize: "0.82rem", marginTop: "0.5rem" }}>
        Please wait while we analyze your skills and predict your career path.
      </p>
    </div>
  );
}

export default SkillPrediction;
