import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './JobDetail.css';

function JobDetail() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJob();
  }, [id]);

  const fetchJob = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_recruiter_jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recruiter_id: localStorage.getItem('userId') || 'recruiter_1' })
      });
      const data = await response.json();
      const found = (data.jobs || []).find(j => String(j.id) === String(id));
      setJob(found || null);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusStyle = (status) => {
    if (status === 'active') return { background: '#e8f8f0', color: '#27ae60', border: '1px solid #27ae60' };
    if (status === 'closed') return { background: '#fdecea', color: '#e74c3c', border: '1px solid #e74c3c' };
    return { background: '#f0f0f0', color: '#7f8c8d', border: '1px solid #bdc3c7' };
  };

  if (loading) return (
    <div className="jd-loading">
      <div className="jd-spinner"></div>
      <p>Loading job details...</p>
    </div>
  );

  if (!job) return (
    <div className="jd-not-found">
      <div className="jd-nf-icon">📭</div>
      <h2>Job Not Found</h2>
      <p>This job posting doesn't exist or has been removed.</p>
      <button className="jd-back-btn" onClick={() => navigate('/recruiter-dashboard')}>← Back to Dashboard</button>
    </div>
  );

  return (
    <div className="jd-container">
      {/* Header */}
      <div className="jd-header">
        <button className="jd-back-btn" onClick={() => navigate('/recruiter-dashboard')}>
          ← Back to Dashboard
        </button>
        <div className="jd-header-actions">
          <button className="jd-btn-secondary" onClick={() => navigate('/job-listings')}>View All Jobs</button>
          <button className="jd-btn-primary" onClick={() => navigate(`/job/${job.id}/applicants`)}>
            👥 View Applicants ({job.applications})
          </button>
        </div>
      </div>

      {/* Job Title Card */}
      <div className="jd-title-card">
        <div className="jd-title-left">
          <div className="jd-company-logo">{job.company.charAt(0)}</div>
          <div>
            <h1 className="jd-job-title">{job.title}</h1>
            <p className="jd-company-name">{job.company}</p>
          </div>
        </div>
        <span className="jd-status-badge" style={getStatusStyle(job.status)}>
          {job.status === 'active' ? '✅ Active' : '❌ Closed'}
        </span>
      </div>

      {/* Meta Info Grid */}
      <div className="jd-meta-grid">
        <div className="jd-meta-card">
          <span className="jd-meta-icon">📍</span>
          <div>
            <div className="jd-meta-label">Location</div>
            <div className="jd-meta-value">{job.location}</div>
          </div>
        </div>
        <div className="jd-meta-card">
          <span className="jd-meta-icon">💼</span>
          <div>
            <div className="jd-meta-label">Job Type</div>
            <div className="jd-meta-value">{job.type || job.jobType}</div>
          </div>
        </div>
        <div className="jd-meta-card">
          <span className="jd-meta-icon">📊</span>
          <div>
            <div className="jd-meta-label">Experience</div>
            <div className="jd-meta-value">{job.experience}</div>
          </div>
        </div>
        <div className="jd-meta-card">
          <span className="jd-meta-icon">💰</span>
          <div>
            <div className="jd-meta-label">Salary</div>
            <div className="jd-meta-value">₹{job.salary}</div>
          </div>
        </div>
        <div className="jd-meta-card">
          <span className="jd-meta-icon">📬</span>
          <div>
            <div className="jd-meta-label">Applications</div>
            <div className="jd-meta-value">{job.applications} received</div>
          </div>
        </div>
        <div className="jd-meta-card">
          <span className="jd-meta-icon">📅</span>
          <div>
            <div className="jd-meta-label">Posted On</div>
            <div className="jd-meta-value">{job.postedDate}</div>
          </div>
        </div>
        <div className="jd-meta-card">
          <span className="jd-meta-icon">⏰</span>
          <div>
            <div className="jd-meta-label">Deadline</div>
            <div className="jd-meta-value">{job.deadline}</div>
          </div>
        </div>
      </div>

      {/* Skills */}
      <div className="jd-section">
        <h2 className="jd-section-title">🎯 Required Skills</h2>
        <div className="jd-skills-wrap">
          {(job.skills || []).map((skill, i) => (
            <span key={i} className="jd-skill-tag">{skill}</span>
          ))}
        </div>
      </div>

      {/* Description */}
      <div className="jd-section">
        <h2 className="jd-section-title">📄 Job Description</h2>
        <p className="jd-description">{job.description}</p>
      </div>

      {/* Requirements */}
      <div className="jd-section">
        <h2 className="jd-section-title">📌 Requirements</h2>
        <div className="jd-requirements">
          {(job.requirements || '').split('\n').filter(r => r.trim()).map((req, i) => (
            <div key={i} className="jd-req-item">
              <span className="jd-req-bullet">✓</span>
              <span>{req.replace(/^[-•]\s*/, '')}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="jd-bottom-actions">
        <button className="jd-btn-outline" onClick={() => navigate('/job-listings')}>
          📊 Manage All Jobs
        </button>
        <button className="jd-btn-outline" onClick={() => navigate('/search-candidates')}>
          🔍 Search Candidates
        </button>
        <button className="jd-btn-primary" onClick={() => navigate(`/job/${job.id}/applicants`)}>
          👥 View All Applicants
        </button>
      </div>
    </div>
  );
}

export default JobDetail;
