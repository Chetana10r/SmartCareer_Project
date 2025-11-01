import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './JobListings.css';

function JobListings() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_recruiter_jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruiter_id: localStorage.getItem('userId') || 'recruiter_1'
        })
      });

      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      // Mock data for demo
      setJobs([
        {
          id: 1,
          title: 'Senior Data Scientist',
          company: 'Tech Corp',
          location: 'Mumbai, India',
          jobType: 'full-time',
          experienceLevel: 'senior',
          salaryMin: '1500000',
          salaryMax: '2000000',
          description: 'Looking for an experienced Data Scientist...',
          skills: ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
          applications: 45,
          status: 'active',
          postedDate: '2025-10-28',
          deadline: '2025-11-30'
        },
        {
          id: 2,
          title: 'Full Stack Developer',
          company: 'StartupXYZ',
          location: 'Bangalore, India',
          jobType: 'full-time',
          experienceLevel: 'intermediate',
          salaryMin: '1000000',
          salaryMax: '1500000',
          description: 'We are looking for a talented Full Stack Developer...',
          skills: ['React', 'Node.js', 'MongoDB', 'AWS'],
          applications: 67,
          status: 'active',
          postedDate: '2025-10-25',
          deadline: '2025-11-25'
        },
        {
          id: 3,
          title: 'DevOps Engineer',
          company: 'Cloud Solutions',
          location: 'Remote',
          jobType: 'contract',
          experienceLevel: 'intermediate',
          salaryMin: '1200000',
          salaryMax: '1800000',
          description: 'Seeking a DevOps Engineer with strong automation skills...',
          skills: ['Docker', 'Kubernetes', 'CI/CD', 'AWS'],
          applications: 34,
          status: 'active',
          postedDate: '2025-10-20',
          deadline: '2025-11-20'
        },
        {
          id: 4,
          title: 'Frontend Developer',
          company: 'Design Hub',
          location: 'Pune, India',
          jobType: 'part-time',
          experienceLevel: 'entry',
          salaryMin: '500000',
          salaryMax: '800000',
          description: 'Looking for a creative Frontend Developer...',
          skills: ['React', 'CSS', 'JavaScript', 'Tailwind'],
          applications: 23,
          status: 'closed',
          postedDate: '2025-10-15',
          deadline: '2025-10-30'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'active': { color: '#2ecc71', text: 'Active', icon: '✅' },
      'closed': { color: '#e74c3c', text: 'Closed', icon: '❌' },
      'draft': { color: '#95a5a6', text: 'Draft', icon: '📝' }
    };
    return badges[status] || badges['active'];
  };

  const toggleJobStatus = async (jobId, currentStatus) => {
    const newStatus = currentStatus === 'active' ? 'closed' : 'active';
    
    try {
      await fetch('http://127.0.0.1:5000/update_job_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId, status: newStatus })
      });

      setJobs(prev =>
        prev.map(job => job.id === jobId ? { ...job, status: newStatus } : job)
      );
    } catch (error) {
      console.error('Error updating job status:', error);
      setJobs(prev =>
        prev.map(job => job.id === jobId ? { ...job, status: newStatus } : job)
      );
    }
  };

  const deleteJob = async (jobId) => {
    if (window.confirm('Are you sure you want to delete this job posting?')) {
      try {
        await fetch('http://127.0.0.1:5000/delete_job', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ job_id: jobId })
        });

        setJobs(prev => prev.filter(job => job.id !== jobId));
      } catch (error) {
        console.error('Error deleting job:', error);
        setJobs(prev => prev.filter(job => job.id !== jobId));
      }
    }
  };

  const editJob = (jobId) => {
    navigate(`/edit-job/${jobId}`);
  };

  const viewApplicants = (jobId) => {
    navigate(`/job/${jobId}/applicants`);
  };

  const filteredJobs = jobs
    .filter(job => filterStatus === 'all' || job.status === filterStatus)
    .filter(job =>
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company.toLowerCase().includes(searchTerm.toLowerCase())
    );

  const stats = {
    total: jobs.length,
    active: jobs.filter(j => j.status === 'active').length,
    closed: jobs.filter(j => j.status === 'closed').length,
    totalApplications: jobs.reduce((sum, job) => sum + job.applications, 0)
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner-large"></div>
        <p>Loading job listings...</p>
      </div>
    );
  }

  return (
    <div className="job-listings-container">
      <div className="listings-header">
        <button className="back-btn" onClick={() => navigate('/recruiter-dashboard')}>
          ← Back to Dashboard
        </button>
        <h1 className="listings-title">
          <span className="title-icon">📊</span>
          Job Listings
        </h1>
        <p className="listings-subtitle">Manage all your job postings</p>
      </div>

      {/* Stats */}
      <div className="listings-stats">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Jobs</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{stats.active}</div>
            <div className="stat-label">Active Jobs</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <div className="stat-value">{stats.closed}</div>
            <div className="stat-label">Closed Jobs</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📬</div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalApplications}</div>
            <div className="stat-label">Total Applications</div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="listings-controls">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search jobs by title or company..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-box">
          <select
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Jobs</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
            <option value="draft">Draft</option>
          </select>
        </div>

        <button className="add-job-btn" onClick={() => navigate('/post-job')}>
          <span>➕</span> Post New Job
        </button>
      </div>

      {/* Jobs Grid */}
      {filteredJobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>No jobs found</h3>
          <p>No jobs match your search criteria</p>
          <button className="primary-btn" onClick={() => navigate('/post-job')}>
            Post Your First Job
          </button>
        </div>
      ) : (
        <div className="jobs-grid">
          {filteredJobs.map((job) => (
            <div key={job.id} className="job-card">
              <div className="job-card-header">
                <div className="job-title-section">
                  <h3 className="job-title">{job.title}</h3>
                  <p className="job-company">{job.company}</p>
                </div>
                <span
                  className="status-badge"
                  style={{ backgroundColor: getStatusBadge(job.status).color }}
                >
                  {getStatusBadge(job.status).icon} {getStatusBadge(job.status).text}
                </span>
              </div>

              <div className="job-meta">
                <div className="meta-item">
                  <span className="meta-icon">📍</span>
                  <span>{job.location}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon">💼</span>
                  <span>{job.jobType}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon">📊</span>
                  <span>{job.experienceLevel}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon">💰</span>
                  <span>₹{parseInt(job.salaryMin)/100000}L - ₹{parseInt(job.salaryMax)/100000}L</span>
                </div>
              </div>

              <div className="job-skills">
                {job.skills.slice(0, 4).map((skill, idx) => (
                  <span key={idx} className="skill-tag">{skill}</span>
                ))}
                {job.skills.length > 4 && (
                  <span className="skill-tag more">+{job.skills.length - 4}</span>
                )}
              </div>

              <div className="job-stats">
                <div className="stat-item">
                  <span className="stat-icon">📬</span>
                  <span className="stat-text">{job.applications} Applications</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">📅</span>
                  <span className="stat-text">Posted {job.postedDate}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">⏰</span>
                  <span className="stat-text">Deadline {job.deadline}</span>
                </div>
              </div>

              <div className="job-actions">
                <button
                  className="action-btn primary"
                  onClick={() => viewApplicants(job.id)}
                >
                  <span>👥</span> View Applicants ({job.applications})
                </button>
                <button
                  className="action-btn secondary"
                  onClick={() => editJob(job.id)}
                >
                  <span>✏️</span> Edit
                </button>
                <button
                  className={`action-btn ${job.status === 'active' ? 'warning' : 'success'}`}
                  onClick={() => toggleJobStatus(job.id, job.status)}
                >
                  <span>{job.status === 'active' ? '⏸️' : '▶️'}</span>
                  {job.status === 'active' ? 'Close' : 'Activate'}
                </button>
                <button
                  className="action-btn danger"
                  onClick={() => deleteJob(job.id)}
                >
                  <span>🗑️</span> Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default JobListings;