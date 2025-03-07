import React, { useState } from "react";
import axios from "axios";

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
  const submitResume = async () => {
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

  return (
    <div className="flex flex-col items-center p-5">
      <h2 className="text-xl font-bold mb-4">Resume Skill Recommender</h2>
      <input type="file" onChange={handleFileChange} className="mb-4" />
      <input 
        type="text" 
        placeholder="Enter the Job Role you are applying for" 
        value={jobRole} 
        onChange={handleRoleChange} 
        className="mb-4 p-2 border border-gray-300 rounded-md"
      />
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded-md"
        onClick={submitResume}
        disabled={loading}
      >
        {loading ? "Processing..." : "Upload Resume"}
      </button>
      {result && (
        <div className="mt-4 w-96 p-4 border border-gray-200 rounded-md">
          <h3 className="font-bold">
            Predicted Job Category: {result.Predicted_Job_Category}
          </h3>
          <p>
            <strong>Extracted Skills:</strong> {result.Extracted_Skills.join(", ")}
          </p>
          <p>
            <strong>Missing Skills:</strong> {result.Missing_Skills.join(", ")}
          </p>
          <h4 className="font-bold mt-2">Recommended Courses:</h4>
          <ul className="list-disc pl-5">
            {result.Recommended_Courses.map((course, index) => (
              <li key={index}>{course}</li>
            ))}
          </ul>
          {result.Recommended_Certifications && result.Recommended_Certifications.length > 0 && (
            <div>
              <h4 className="font-bold mt-2">Recommended Certifications:</h4>
              <ul className="list-disc pl-5">
                {result.Recommended_Certifications.map((cert, index) => (
                  <li key={index}>{cert}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ResumeRecommender;
