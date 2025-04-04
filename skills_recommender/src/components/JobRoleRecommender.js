import React, { useState } from "react";
import axios from "axios";

const JobRoleRecommender = () => {
  const [skills, setSkills] = useState("");
  const [projects, setProjects] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/predict_job_role", {
        skills,
        projects,
      });
      setJobRole(response.data.job_role);
    } catch (error) {
      console.error("Prediction error:", error);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-2xl shadow-md mt-6">
      <h2 className="text-xl font-semibold mb-4 text-center">Job Role Recommender</h2>
      <textarea
        className="w-full p-2 border border-gray-300 rounded-md mb-4"
        placeholder="Enter your skills (comma separated)"
        value={skills}
        onChange={(e) => setSkills(e.target.value)}
        rows={3}
      />
      <textarea
        className="w-full p-2 border border-gray-300 rounded-md mb-4"
        placeholder="Enter your projects (comma separated)"
        value={projects}
        onChange={(e) => setProjects(e.target.value)}
        rows={3}
      />
      <button
        onClick={handleSubmit}
        className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700"
        disabled={loading}
      >
        {loading ? "Recommending..." : "Recommend Job Role"}
      </button>

      {jobRole && (
        <div className="mt-4 p-3 bg-green-100 text-green-800 rounded-md">
          <strong>Recommended Job Role:</strong> {jobRole}
        </div>
      )}
    </div>
  );
};

export default JobRoleRecommender;
