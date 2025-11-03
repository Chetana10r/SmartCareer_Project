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
    type: 'Full Time', // Changed from jobType
    experience: 'Intermediate (2-5 years)', // Changed from experienceLevel
    salary: '', // Combined salary field
    description: '',
    requirements: '', // Changed to string (backend expects string)
    skills: [], // Keep as array
    applicationDeadline: '',
    numberOfPositions: 1
  });

  const handleChange = (field, value) => {
    setJobData(prev => ({ ...prev, [field]: value }));
  };

  const handleSkillsChange = (index, value) => {
    const updated = [...jobData.skills];
    updated[index] = value;
    setJobData(prev => ({ ...prev, skills: updated }));
  };

  const addSkill = () => {
    setJobData(prev => ({ ...prev, skills: [...prev.skills, ''] }));
  };

  const removeSkill = (index) => {
    const updated = jobData.skills.filter((_, i) => i !== index);
    setJobData(prev => ({ ...prev, skills: updated }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!jobData.title || !jobData.company || !jobData.description || !jobData.requirements) {
      setError('Please fill in all required fields (Title, Company, Description, Requirements)');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Get recruiterId from localStorage
      const recruiterId = localStorage.getItem('userId');
      
      if (!recruiterId) {
        setError('Please login as a recruiter first');
        setLoading(false);
        return;
      }

      // Prepare payload according to backend expectations
      const payload = {
        title: jobData.title,
        company: jobData.company,
        location: jobData.location || 'Not specified',
        type: jobData.type,
        experience: jobData.experience,
        salary: jobData.salary || 'Competitive',
        description: jobData.description,
        requirements: jobData.requirements, // String format
        skills: jobData.skills.filter(skill => skill.trim() !== ''), // Remove empty skills
        recruiterId: recruiterId
      };

      console.log('Sending payload:', payload); // Debug log

      const response = await fetch('http://127.0.0.1:5000/api/recruiter/post-job', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
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
              <label className="form-label">Job Type *</label>
              <select
                className="form-select"
                value={jobData.type}
                onChange={(e) => handleChange('type', e.target.value)}
              >
                <option value="Full Time">Full Time</option>
                <option value="Part Time">Part Time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Experience Level</label>
              <select
                className="form-select"
                value={jobData.experience}
                onChange={(e) => handleChange('experience', e.target.value)}
              >
                <option value="Entry Level (0-2 years)">Entry Level (0-2 years)</option>
                <option value="Intermediate (2-5 years)">Intermediate (2-5 years)</option>
                <option value="Senior (5+ years)">Senior (5+ years)</option>
                <option value="Lead/Manager">Lead/Manager</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Salary Range (Annual)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., ₹8-12 LPA or Competitive"
                value={jobData.salary}
                onChange={(e) => handleChange('salary', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Job Description */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">📄</span>
            Job Description *
          </h2>
          
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-textarea"
              rows="6"
              placeholder="Provide a detailed job description including responsibilities and what the role entails..."
              value={jobData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              required
            />
          </div>
        </div>

        {/* Requirements */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">📌</span>
            Requirements *
          </h2>
          
          <div className="form-group">
            <label className="form-label">Requirements (one per line)</label>
            <textarea
              className="form-textarea"
              rows="6"
              placeholder="Enter job requirements, qualifications, and must-have skills (one per line)&#10;Example:&#10;- Bachelor's degree in Computer Science&#10;- 3+ years of experience in Python&#10;- Strong knowledge of machine learning"
              value={jobData.requirements}
              onChange={(e) => handleChange('requirements', e.target.value)}
              required
            />
          </div>
        </div>

        {/* Skills */}
        <div className="form-section">
          <h2 className="section-title">
            <span className="section-icon">🎯</span>
            Required Skills (Optional)
          </h2>
          
          {jobData.skills.length === 0 ? (
            <button
              type="button"
              className="add-btn"
              onClick={addSkill}
            >
              + Add Skill
            </button>
          ) : (
            <>
              {jobData.skills.map((skill, index) => (
                <div key={index} className="array-input-group">
                  <input
                    type="text"
                    className="form-input"
                    placeholder={`Skill ${index + 1} (e.g., Python, Machine Learning)`}
                    value={skill}
                    onChange={(e) => handleSkillsChange(index, e.target.value)}
                  />
                  <button
                    type="button"
                    className="remove-btn"
                    onClick={() => removeSkill(index)}
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button
                type="button"
                className="add-btn"
                onClick={addSkill}
              >
                + Add Another Skill
              </button>
            </>
          )}
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