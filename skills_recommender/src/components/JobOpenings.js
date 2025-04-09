import React, { useEffect, useState } from "react";
import "./JobOpenings.css";

function JobOpenings({ jobRole }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

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
            location: "remote",
            salary_min: "30000"
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
        <p>Loading job listings...</p>
      ) : jobs.length === 0 ? (
        <p>No job openings found.</p>
      ) : (
        <div className="job-cards">
          {jobs.map((job, index) => (
            <div key={index} className="job-card">
              <h3>{job.title}</h3>
              <p><strong>Company:</strong> {job.company}</p>
              <p><strong>Location:</strong> {job.location}</p>
              <p>
                <strong>Salary:</strong> {job.salary_min} - {job.salary_max}
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
