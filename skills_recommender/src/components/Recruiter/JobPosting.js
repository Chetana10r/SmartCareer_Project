import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './JobPosting.css';

function JobPosting() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const [jobData, setJobData] = useState({
    title: '',
    company: '',
    location: '',
    jobType: 'full-time',
    experienceLevel: 'intermediate',
    salaryMin: '',
    salaryMax: '',
    description: '',
    responsibilities: [''],
    requirements: [''],
    skills: [''],
    benefits: [''],
    applicationDeadline: '',
    numberOfPositions: 1
  });

  const handleChange = (field, value) => {
    setJobData(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayChange = (field, index, value) => {
    const updated = [...jobData[field]];
    updated[index] = value;
    setJobData(prev => ({ ...prev, [field]: updated }));
  };

  const addArrayItem = (field) => {
    setJobData(prev => ({ ...prev, [field]: [...prev[field], ''] }));
  };

  const removeArrayItem = (field, index) => {
    const updated = jobData[field].filter((_, i) => i !== index);
    setJobData(prev => ({ ...prev, [field]: updated }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!jobData.title || !jobData.company || !jobData.description) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:5000/post_job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...jobData,
          recruiter_id: localStorage.getItem('userId') || 'recruiter_1'
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('✅ Job posted successfully!');
        setTimeout(() => {
          navigate('/recruiter-dashboard');
        }, 2000);
      } else {
        setError(data.error || 'Failed to post job');
      }
    } catch (err) {
      console.error('Error posting job:', err);
      setError('Failed to post job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-posting-container">
      <div className="posting-header">
        <button className="back-btn" onClick={() => navigate('/recruiter-dashboard')}>
          ← Back to Dashboard
        </button>
        <h1 className="posting-title">
          <span className="title-icon">📝</span>
          Post New Job
        </h1>
        <p className="posting-subtitle">Fill in the details to create a job opening</p>
      </div>

      {success && <div className="alert alert-success">{success}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <form className="job-form" onSubmit={handleSubmit}>
        {/* Basic Information */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">📋</span>
            Basic Information
          </h2>
          
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Job Title *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Senior Data Scientist"
                value={jobData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Company Name *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Tech Solutions Inc."
                value={jobData.company}
                onChange={(e) => handleChange('company', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Location</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Mumbai, India or Remote"
                value={jobData.location}
                onChange={(e) => handleChange('location', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Job Type</label>
              <select
                className="form-select"
                value={jobData.jobType}
                onChange={(e) => handleChange('jobType', e.target.value)}
              >
                <option value="full-time">Full Time</option>
                <option value="part-time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Experience Level</label>
              <select
                className="form-select"
                value={jobData.experienceLevel}
                onChange={(e) => handleChange('experienceLevel', e.target.value)}
              >
                <option value="entry">Entry Level (0-2 years)</option>
                <option value="intermediate">Intermediate (2-5 years)</option>
                <option value="senior">Senior (5+ years)</option>
                <option value="lead">Lead/Manager</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Number of Positions</label>
              <input
                type="number"
                className="form-input"
                min="1"
                value={jobData.numberOfPositions}
                onChange={(e) => handleChange('numberOfPositions', e.target.value)}
              />
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Salary Min (Annual)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., 800000"
                value={jobData.salaryMin}
                onChange={(e) => handleChange('salaryMin', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Salary Max (Annual)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., 1200000"
                value={jobData.salaryMax}
                onChange={(e) => handleChange('salaryMax', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Application Deadline</label>
              <input
                type="date"
                className="form-input"
                value={jobData.applicationDeadline}
                onChange={(e) => handleChange('applicationDeadline', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Job Description */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">📄</span>
            Job Description
          </h2>
          
          <div className="form-group">
            <label className="form-label">Description *</label>
            <textarea
              className="form-textarea"
              rows="6"
              placeholder="Provide a detailed job description..."
              value={jobData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              required
            />
          </div>
        </div>

        {/* Responsibilities */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">✅</span>
            Responsibilities
          </h2>
          
          {jobData.responsibilities.map((resp, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                className="form-input"
                placeholder={`Responsibility ${index + 1}`}
                value={resp}
                onChange={(e) => handleArrayChange('responsibilities', index, e.target.value)}
              />
              {jobData.responsibilities.length > 1 && (
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeArrayItem('responsibilities', index)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            className="add-btn"
            onClick={() => addArrayItem('responsibilities')}
          >
            + Add Responsibility
          </button>
        </div>

        {/* Requirements */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">📌</span>
            Requirements
          </h2>
          
          {jobData.requirements.map((req, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                className="form-input"
                placeholder={`Requirement ${index + 1}`}
                value={req}
                onChange={(e) => handleArrayChange('requirements', index, e.target.value)}
              />
              {jobData.requirements.length > 1 && (
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeArrayItem('requirements', index)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            className="add-btn"
            onClick={() => addArrayItem('requirements')}
          >
            + Add Requirement
          </button>
        </div>

        {/* Skills */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">🎯</span>
            Required Skills
          </h2>
          
          {jobData.skills.map((skill, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                className="form-input"
                placeholder={`Skill ${index + 1} (e.g., Python, Machine Learning)`}
                value={skill}
                onChange={(e) => handleArrayChange('skills', index, e.target.value)}
              />
              {jobData.skills.length > 1 && (
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeArrayItem('skills', index)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            className="add-btn"
            onClick={() => addArrayItem('skills')}
          >
            + Add Skill
          </button>
        </div>

        {/* Benefits */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">🎁</span>
            Benefits
          </h2>
          
          {jobData.benefits.map((benefit, index) => (
            <div key={index} className="array-input-group">
              <input
                type="text"
                className="form-input"
                placeholder={`Benefit ${index + 1}`}
                value={benefit}
                onChange={(e) => handleArrayChange('benefits', index, e.target.value)}
              />
              {jobData.benefits.length > 1 && (
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeArrayItem('benefits', index)}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            className="add-btn"
            onClick={() => addArrayItem('benefits')}
          >
            + Add Benefit
          </button>
        </div>

        {/* Submit Buttons */}
        <div className="form-actions">
          <button
            type="button"
            className="cancel-btn"
            onClick={() => navigate('/recruiter-dashboard')}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="submit-btn"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Posting...
              </>
            ) : (
              <>
                <span className="btn-icon">📤</span>
                Post Job
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default JobPosting;