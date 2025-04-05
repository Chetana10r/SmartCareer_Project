import React, { useEffect } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";

function SkillPrediction() {
  const location = useLocation();
  const navigate = useNavigate();

  const { domain, resume } = location.state || {};

  useEffect(() => {
    if (!domain || !resume) {
      alert("No resume data found. Please upload again.");
      navigate("/"); // Redirect to homepage or upload page
      return;
    }

    const fetchPrediction = async () => {
      try {
        const formData = new FormData();
        formData.append("resume", resume);
        formData.append("domain", domain);

        const response = await axios.post(
          "http://localhost:5000/proceed_prediction",
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );

        navigate("/result", { state: { ...response.data, domain } });
      } catch (error) {
        console.error("Skill prediction failed:", error);
        alert("Skill prediction failed. Please try again.");
      }
    };

    fetchPrediction();
  }, [domain, resume, navigate]);

  return (
    <div className="container">
      <h2>Processing Resume...</h2>
      <p>Please wait while we analyze your resume.</p>
    </div>
  );
}

export default SkillPrediction;
