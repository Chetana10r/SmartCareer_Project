import React, { useState } from 'react';

const JobOpenings = ({ role }) => {
    const [jobs, setJobs] = useState([]);

    const fetchJobs = async () => {
        const response = await fetch("http://localhost:5000/job_openings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role }),
        });

        const data = await response.json();
        setJobs(data.jobs);
    };

    return (
        <div>
            <button onClick={fetchJobs}>Get Job Openings</button>
            <ul>
                {jobs.map((job, index) => (
                    <li key={index}>{job.title} at {job.company} ({job.location})</li>
                ))}
            </ul>
        </div>
    );
};

export default JobOpenings;
