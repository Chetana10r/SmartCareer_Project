import React, { useEffect, useState } from "react";
import "./JobOpenings.css";

function JobOpenings({ jobRole }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  const DEFAULT_LOCATION = "remote";
  const DEFAULT_MIN_SALARY = "30000";

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch("http://localhost:5000/scrape-jobs", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            job_role: jobRole,
            location: DEFAULT_LOCATION,
            salary_min: DEFAULT_MIN_SALARY,
          }),
        });

        const data = await response.json();
        setJobs(data.length > 0 ? data : []);
      } catch (error) {
        console.error("❌ Error fetching jobs:", error);
        setJobs([]);
      } finally {
        setLoading(false);
      }
    };

    if (jobRole) {
      setLoading(true);
      fetchJobs();
    }
  }, [jobRole]);

  return (
    <div className="job-openings">
      <h2>Job Openings for: {jobRole || "..."}</h2>

      {loading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading job listings...</p>
        </div>
      ) : jobs.length === 0 ? (
        <p>No job openings found.</p>
      ) : (
        <div className="job-cards">
          {jobs.map((job, index) => (
            <div key={index} className="job-card">
              <h3>{job.title || "No title available"}</h3>
              <p><strong>Company:</strong> {job.company || "N/A"}</p>
              <p><strong>Location:</strong> {job.location || "Remote/Unknown"}</p>
              <p>
                <strong>Salary:</strong>{" "}
                {job.salary_min ? `${job.salary_min}` : "Not specified"} -{" "}
                {job.salary_max ? `${job.salary_max}` : "Not specified"}
              </p>
              <a href={job.url} target="_blank" rel="noopener noreferrer">
                View Job
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default JobOpenings;
