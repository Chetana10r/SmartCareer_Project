import React, { useState } from 'react';
import axios from 'axios';
import './ResumeOptimizer.css';

const ResumeOptimizer = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    linkedin: '',
    github: '',
  });
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
      setErrorMessage('');
    } else {
      setErrorMessage('Please upload a valid PDF file');
      setResumeFile(null);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAdditionalInfo((prev) => ({ ...prev, [name]: value }));
  };

  const handleOptimize = async () => {
    if (!resumeFile) {
      setErrorMessage('Please upload a resume file');
      return;
    }
    if (!jobDescription.trim()) {
      setErrorMessage('Please enter the job description');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('job_description', jobDescription);
      formData.append('additional_info', JSON.stringify(additionalInfo));

      const response = await axios.post('http://127.0.0.1:5000/optimize_resume', formData, {
        responseType: 'blob',
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'optimized_resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      setSuccessMessage('✅ Resume optimized successfully! Check your downloads.');
      setTimeout(() => setSuccessMessage(''), 5000);
    } catch (error) {
      setErrorMessage('❌ Error optimizing resume. Please try again.');
      console.error('Error:', error);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="optimizer-container">
      {/* Header */}
      <div className="header-section">
        <div className="header-content">
          <h1 className="main-title">
            <span className="title-icon">🎯</span>
            AI Resume Optimizer
          </h1>
          <p className="subtitle">
            Transform your resume with AI-powered optimization tailored to your dream job
          </p>
        </div>
      </div>

      {/* Messages */}
      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
        </div>
      )}
      {errorMessage && (
        <div className="alert alert-error">
          {errorMessage}
        </div>
      )}

      <div className="content-wrapper">
        {/* Step 1: Upload Resume */}
        <div className="card">
          <div className="card-header">
            <span className="step-number">1</span>
            <h2 className="card-title">Upload Your Resume</h2>
          </div>
          <div className="card-body">
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
                  {resumeFile ? (
                    <>
                      <span className="file-name">{resumeFile.name}</span>
                      <span className="file-size"> ({(resumeFile.size / 1024).toFixed(2)} KB)</span>
                    </>
                  ) : (
                    'Click to upload or drag and drop'
                  )}
                </p>
                <p className="upload-hint">PDF files only (Max 5MB)</p>
              </label>
            </div>
          </div>
        </div>

        {/* Step 2: Job Description */}
        <div className="card">
          <div className="card-header">
            <span className="step-number">2</span>
            <h2 className="card-title">Job Description</h2>
          </div>
          <div className="card-body">
            <textarea
              rows={8}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the complete job description here...&#10;&#10;Include:&#10;• Job requirements&#10;• Required skills&#10;• Responsibilities&#10;• Qualifications"
              className="textarea"
            />
            <div className="char-count">
              {jobDescription.length} characters
            </div>
          </div>
        </div>

        {/* Step 3: Personal Information */}
        <div className="card">
          <div className="card-header">
            <span className="step-number">3</span>
            <h2 className="card-title">Personal Information</h2>
            <span className="optional-badge">Optional</span>
          </div>
          <div className="card-body">
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="name" className="form-label">
                  <span className="label-icon">👤</span>
                  Full Name
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={additionalInfo.name}
                  onChange={handleInputChange}
                  placeholder="John Doe"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email" className="form-label">
                  <span className="label-icon">📧</span>
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={additionalInfo.email}
                  onChange={handleInputChange}
                  placeholder="john.doe@example.com"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone" className="form-label">
                  <span className="label-icon">📱</span>
                  Phone Number
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={additionalInfo.phone}
                  onChange={handleInputChange}
                  placeholder="+91-1234567890"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="location" className="form-label">
                  <span className="label-icon">📍</span>
                  Location
                </label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={additionalInfo.location}
                  onChange={handleInputChange}
                  placeholder="City, Country"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="linkedin" className="form-label">
                  <span className="label-icon">💼</span>
                  LinkedIn Profile
                </label>
                <input
                  type="url"
                  id="linkedin"
                  name="linkedin"
                  value={additionalInfo.linkedin}
                  onChange={handleInputChange}
                  placeholder="linkedin.com/in/username"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="github" className="form-label">
                  <span className="label-icon">💻</span>
                  GitHub Profile
                </label>
                <input
                  type="url"
                  id="github"
                  name="github"
                  value={additionalInfo.github}
                  onChange={handleInputChange}
                  placeholder="github.com/username"
                  className="form-input"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {loading && uploadProgress > 0 && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="progress-text">{uploadProgress}% Uploaded</p>
          </div>
        )}

        {/* Action Button */}
        <div className="action-section">
          <button
            onClick={handleOptimize}
            disabled={loading || !resumeFile || !jobDescription.trim()}
            className={`optimize-button ${loading ? 'loading' : ''}`}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                <span>Optimizing Your Resume...</span>
              </>
            ) : (
              <>
                <span className="button-icon">✨</span>
                <span>Optimize Resume</span>
              </>
            )}
          </button>
          
          <div className="features-list">
            <div className="feature-item">
              <span className="feature-icon">🤖</span>
              <span>AI-Powered Analysis</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🎯</span>
              <span>Job-Tailored Content</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">⚡</span>
              <span>ATS-Friendly Format</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <p>💡 Tip: Provide accurate personal information for better results</p>
      </div>
    </div>
  );
};

export default ResumeOptimizer;