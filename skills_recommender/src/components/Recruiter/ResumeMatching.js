import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ResumeMatching.css';

function ResumeMatching() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [matchingResults, setMatchingResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
      // Mock data
      setJobs([
        { id: 1, title: 'Senior Data Scientist', company: 'Tech Corp' },
        { id: 2, title: 'Full Stack Developer', company: 'StartupXYZ' },
        { id: 3, title: 'ML Engineer', company: 'AI Solutions' }
      ]);
    }
  };

  const handleJobSelect = (jobId) => {
    setSelectedJob(jobId);
    const job = jobs.find(j => j.id === parseInt(jobId));
    if (job) {
      setJobDescription(job.description || '');
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
      setError('');
    } else {
      setError('Please upload a valid PDF file');
      setResumeFile(null);
    }
  };

  const handleMatch = async () => {
    if (!resumeFile) {
      setError('Please upload a resume');
      return;
    }

    if (!selectedJob && !jobDescription) {
      setError('Please select a job or enter job description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('job_id', selectedJob);
      formData.append('job_description', jobDescription);

      const response = await fetch('http://127.0.0.1:5000/match_resume', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setMatchingResults(data);
    } catch (error) {
      console.error('Error matching resume:', error);
      // Mock results
      setMatchingResults({
        match_score: 87,
        matched_skills: ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
        missing_skills: ['AWS', 'Docker'],
        experience_match: 85,
        education_match: 90,
        overall_recommendation: 'Highly Recommended',
        candidate_name: 'John Doe',
        key_strengths: [
          'Strong machine learning background',
          'Relevant project experience',
          'Good educational qualification'
        ],
        areas_for_improvement: [
          'Limited cloud platform experience',
          'Could benefit from containerization knowledge'
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#2ecc71';
    if (score >= 60) return '#f39c12';
    return '#e74c3c';
  };

  const getRecommendationBadge = (recommendation) => {
    const badges = {
      'Highly Recommended': { color: '#2ecc71', icon: '⭐' },
      'Recommended': { color: '#f39c12', icon: '👍' },
      'Consider': { color: '#e67e22', icon: '🤔' },
      'Not Recommended': { color: '#e74c3c', icon: '❌' }
    };
    return badges[recommendation] || badges['Consider'];
  };

  return (
    <div className="resume-matching-container">
      <div className="matching-header">
        <button className="back-btn" onClick={() => navigate('/recruiter-dashboard')}>
          ← Back to Dashboard
        </button>
        <h1 className="matching-title">
          <span className="title-icon">🎯</span>
          AI Resume Matching
        </h1>
        <p className="matching-subtitle">Match candidate resumes to job requirements</p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="matching-content">
        {/* Input Section */}
        <div className="input-section">
          <div className="input-card">
            <h2 className="card-title">
              <span className="card-icon">📋</span>
              Select Job Posting
            </h2>
            <select
              className="job-select"
              value={selectedJob}
              onChange={(e) => handleJobSelect(e.target.value)}
            >
              <option value="">-- Select a Job --</option>
              {jobs.map(job => (
                <option key={job.id} value={job.id}>
                  {job.title} - {job.company}
                </option>
              ))}
            </select>

            <div className="divider">
              <span>OR</span>
            </div>

            <h3 className="input-label">Enter Job Description</h3>
            <textarea
              className="job-description-input"
              rows="6"
              placeholder="Paste job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </div>

          <div className="input-card">
            <h2 className="card-title">
              <span className="card-icon">📄</span>
              Upload Resume
            </h2>
            
            <div className="upload-zone">
              <input
                type="file"
                id="resume-upload"
                accept=".pdf"
                onChange={handleFileUpload}
                className="file-input"
              />
              <label htmlFor="resume-upload" className="upload-label">
                <div className="upload-icon">📤</div>
                {resumeFile ? (
                  <div className="file-info">
                    <p className="file-name">{resumeFile.name}</p>
                    <p className="file-size">
                      {(resumeFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                ) : (
                  <p className="upload-text">Click to upload resume (PDF only)</p>
                )}
              </label>
            </div>

            <button
              className="match-btn"
              onClick={handleMatch}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                <>
                  <span className="btn-icon">🔍</span>
                  Match Resume
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {matchingResults && (
          <div className="results-section">
            <h2 className="results-title">
              <span className="title-icon">📊</span>
              Matching Results
            </h2>

            {/* Overall Score */}
            <div className="score-showcase">
              <div 
                className="score-circle"
                style={{ borderColor: getScoreColor(matchingResults.match_score) }}
              >
                <div className="score-value">{matchingResults.match_score}</div>
                <div className="score-label">Match Score</div>
              </div>

              <div className="recommendation-badge-large">
                <span className="badge-icon">
                  {getRecommendationBadge(matchingResults.overall_recommendation).icon}
                </span>
                <span 
                  className="badge-text"
                  style={{ 
                    color: getRecommendationBadge(matchingResults.overall_recommendation).color 
                  }}
                >
                  {matchingResults.overall_recommendation}
                </span>
              </div>
            </div>

            {/* Detailed Scores */}
            <div className="detailed-scores">
              <div className="score-item">
                <span className="score-label-small">Experience Match</span>
                <div className="score-bar">
                  <div 
                    className="score-bar-fill"
                    style={{ 
                      width: `${matchingResults.experience_match}%`,
                      background: getScoreColor(matchingResults.experience_match)
                    }}
                  >
                    <span className="score-value-small">
                      {matchingResults.experience_match}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="score-item">
                <span className="score-label-small">Education Match</span>
                <div className="score-bar">
                  <div 
                    className="score-bar-fill"
                    style={{ 
                      width: `${matchingResults.education_match}%`,
                      background: getScoreColor(matchingResults.education_match)
                    }}
                  >
                    <span className="score-value-small">
                      {matchingResults.education_match}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Skills Analysis */}
            <div className="skills-analysis">
              <div className="skills-section matched">
                <h3 className="skills-title">
                  <span className="skills-icon">✅</span>
                  Matched Skills ({matchingResults.matched_skills.length})
                </h3>
                <div className="skills-grid">
                  {matchingResults.matched_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge matched">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div className="skills-section missing">
                <h3 className="skills-title">
                  <span className="skills-icon">⚠️</span>
                  Missing Skills ({matchingResults.missing_skills.length})
                </h3>
                <div className="skills-grid">
                  {matchingResults.missing_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge missing">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Strengths & Improvements */}
            <div className="analysis-details">
              <div className="analysis-card strengths">
                <h3 className="analysis-title">
                  <span className="analysis-icon">💪</span>
                  Key Strengths
                </h3>
                <ul className="analysis-list">
                  {matchingResults.key_strengths.map((strength, idx) => (
                    <li key={idx}>{strength}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-card improvements">
                <h3 className="analysis-title">
                  <span className="analysis-icon">📈</span>
                  Areas for Improvement
                </h3>
                <ul className="analysis-list">
                  {matchingResults.areas_for_improvement.map((area, idx) => (
                    <li key={idx}>{area}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Actions */}
            <div className="results-actions">
              <button className="action-btn shortlist">
                <span>⭐</span> Shortlist Candidate
              </button>
              <button className="action-btn schedule">
                <span>📅</span> Schedule Interview
              </button>
              <button className="action-btn contact">
                <span>✉️</span> Contact Candidate
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResumeMatching;