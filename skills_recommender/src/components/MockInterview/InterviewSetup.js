import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './InterviewSetup.css';

function InterviewSetup() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [config, setConfig] = useState({
    jobRole: '',
    interviewType: 'technical',
    difficulty: 'medium',
    duration: 20,
    resumeFile: null
  });

  const jobRoles = [
    'Data Scientist',
    'Software Engineer',
    'Machine Learning Engineer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'DevOps Engineer',
    'Product Manager',
    'Business Analyst',
    'UI/UX Designer'
  ];

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setConfig({ ...config, resumeFile: file });
      setError('');
    } else {
      setError('Please upload a valid PDF file');
      setConfig({ ...config, resumeFile: null });
    }
  };

  const handleStartInterview = async () => {
    if (!config.jobRole.trim()) {
      setError('Please select or enter a job role');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('job_role', config.jobRole);
      formData.append('interview_type', config.interviewType);
      formData.append('difficulty', config.difficulty);
      formData.append('duration', config.duration);
      
      if (config.resumeFile) {
        formData.append('resume', config.resumeFile);
      }

      const response = await fetch('http://127.0.0.1:5000/start_interview', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to start interview');
      }

      const data = await response.json();
      
      navigate('/interview-session', { 
        state: { 
          sessionId: data.session_id,
          config: config
        } 
      });
    } catch (err) {
      setError('Failed to start interview: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="interview-setup-container">
      <div className="setup-header">
        <div className="header-content">
          <h1 className="setup-title">
            <span className="title-icon">🎤</span>
            AI Mock Interview
          </h1>
          <p className="setup-subtitle">
            Practice interviews with AI-powered feedback and improve your skills
          </p>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          ⚠️ {error}
        </div>
      )}

      <div className="setup-content">
        <div className="setup-card">
          <div className="card-section">
            <div className="section-header">
              <span className="section-number">1</span>
              <h2 className="section-title">Job Details</h2>
            </div>
            
            <div className="form-group">
              <label className="form-label">
                <span className="label-icon">💼</span>
                Job Role *
              </label>
              <input
                type="text"
                list="job-roles"
                className="form-input"
                placeholder="Select or type a job role"
                value={config.jobRole}
                onChange={(e) => setConfig({ ...config, jobRole: e.target.value })}
              />
              <datalist id="job-roles">
                {jobRoles.map((role, idx) => (
                  <option key={idx} value={role} />
                ))}
              </datalist>
            </div>
          </div>

          <div className="card-section">
            <div className="section-header">
              <span className="section-number">2</span>
              <h2 className="section-title">Interview Configuration</h2>
            </div>

            <div className="config-grid">
              <div className="form-group">
                <label className="form-label">
                  <span className="label-icon">📋</span>
                  Interview Type
                </label>
                <select
                  className="form-select"
                  value={config.interviewType}
                  onChange={(e) => setConfig({ ...config, interviewType: e.target.value })}
                >
                  <option value="technical">Technical</option>
                  <option value="hr">HR/Behavioral</option>
                  <option value="mixed">Mixed (Technical + HR)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span className="label-icon">🎯</span>
                  Difficulty Level
                </label>
                <select
                  className="form-select"
                  value={config.difficulty}
                  onChange={(e) => setConfig({ ...config, difficulty: e.target.value })}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span className="label-icon">⏱️</span>
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  className="form-input"
                  min="5"
                  max="60"
                  value={config.duration}
                  onChange={(e) => setConfig({ ...config, duration: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div className="card-section">
            <div className="section-header">
              <span className="section-number">3</span>
              <h2 className="section-title">Resume Upload (Optional)</h2>
            </div>

            <div className="upload-area">
              <input
                type="file"
                id="resume-upload"
                accept=".pdf"
                onChange={handleFileChange}
                className="file-input"
              />
              <label htmlFor="resume-upload" className="upload-label">
                <div className="upload-icon">📄</div>
                <p className="upload-text">
                  {config.resumeFile ? (
                    <>
                      <span className="file-name">{config.resumeFile.name}</span>
                      <span className="file-size">
                        {' '}({(config.resumeFile.size / 1024).toFixed(2)} KB)
                      </span>
                    </>
                  ) : (
                    'Click to upload or drag and drop'
                  )}
                </p>
                <p className="upload-hint">
                  Upload your resume for personalized questions
                </p>
              </label>
            </div>
          </div>

          <div className="features-preview">
            <h3 className="features-title">What to Expect</h3>
            <div className="features-grid">
              <div className="feature-card">
                <span className="feature-icon">🎙️</span>
                <h4>Voice Interaction</h4>
                <p>Speak naturally and get real-time responses</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🤖</span>
                <h4>AI Analysis</h4>
                <p>Get instant feedback on your answers</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">📊</span>
                <h4>Detailed Report</h4>
                <p>Comprehensive performance analytics</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">💡</span>
                <h4>Improvement Tips</h4>
                <p>Personalized suggestions to excel</p>
              </div>
            </div>
          </div>

          <div className="action-section">
            <button
              className="start-button"
              onClick={handleStartInterview}
              disabled={loading || !config.jobRole.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  <span>Preparing Interview...</span>
                </>
              ) : (
                <>
                  <span className="button-icon">🚀</span>
                  <span>Start Interview</span>
                </>
              )}
            </button>
            
            <button
              className="history-button"
              onClick={() => navigate('/interview-history')}
            >
              <span className="button-icon">📜</span>
              <span>View History</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InterviewSetup;