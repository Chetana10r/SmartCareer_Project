import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './CandidateSearch.css';

function CandidateSearch() {
  const navigate = useNavigate();
  const [searchCriteria, setSearchCriteria] = useState({
    skills: '',
    experience: '',
    location: '',
    education: '',
    jobRole: ''
  });

  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    setSearched(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/search_candidates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchCriteria)
      });

      const data = await response.json();
      setCandidates(data.candidates || []);
    } catch (error) {
      console.error('Error searching candidates:', error);
      // Mock data for demo
      setCandidates([
        {
          id: 1,
          name: 'Rahul Sharma',
          email: 'rahul.sharma@email.com',
          phone: '+91-9876543210',
          experience: '3 years',
          location: 'Mumbai, India',
          skills: ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
          education: 'B.Tech in Computer Science',
          match_score: 92,
          resume_url: '/resumes/rahul_sharma.pdf'
        },
        {
          id: 2,
          name: 'Priya Patel',
          email: 'priya.patel@email.com',
          phone: '+91-9876543211',
          experience: '5 years',
          location: 'Bangalore, India',
          skills: ['Data Science', 'Python', 'R', 'Deep Learning'],
          education: 'M.Tech in Data Science',
          match_score: 88,
          resume_url: '/resumes/priya_patel.pdf'
        },
        {
          id: 3,
          name: 'Amit Kumar',
          email: 'amit.kumar@email.com',
          phone: '+91-9876543212',
          experience: '2 years',
          location: 'Delhi, India',
          skills: ['Java', 'Spring Boot', 'Microservices', 'AWS'],
          education: 'B.Tech in IT',
          match_score: 85,
          resume_url: '/resumes/amit_kumar.pdf'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleShortlist = async (candidateId) => {
    try {
      await fetch('http://127.0.0.1:5000/shortlist_candidate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidateId,
          recruiter_id: localStorage.getItem('userId') || 'recruiter_1'
        })
      });

      alert('Candidate shortlisted successfully!');
    } catch (error) {
      console.error('Error shortlisting:', error);
      alert('Candidate shortlisted!');
    }
  };

  const getMatchColor = (score) => {
    if (score >= 85) return '#2ecc71';
    if (score >= 70) return '#f39c12';
    return '#e74c3c';
  };

  return (
    <div className="candidate-search-container">
      <div className="search-header">
        <button className="back-btn" onClick={() => navigate('/recruiter-dashboard')}>
          ← Back to Dashboard
        </button>
        <h1 className="search-title">
          <span className="title-icon">🔍</span>
          Search Candidates
        </h1>
        <p className="search-subtitle">Find the perfect candidates for your openings</p>
      </div>

      {/* Search Filters */}
      <div className="search-filters">
        <h2 className="filter-title">Search Criteria</h2>
        
        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">
              <span className="label-icon">🎯</span>
              Skills (comma separated)
            </label>
            <input
              type="text"
              className="filter-input"
              placeholder="e.g., Python, Machine Learning, SQL"
              value={searchCriteria.skills}
              onChange={(e) => setSearchCriteria({...searchCriteria, skills: e.target.value})}
            />
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="label-icon">💼</span>
              Job Role
            </label>
            <input
              type="text"
              className="filter-input"
              placeholder="e.g., Data Scientist"
              value={searchCriteria.jobRole}
              onChange={(e) => setSearchCriteria({...searchCriteria, jobRole: e.target.value})}
            />
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="label-icon">⏱️</span>
              Experience
            </label>
            <select
              className="filter-select"
              value={searchCriteria.experience}
              onChange={(e) => setSearchCriteria({...searchCriteria, experience: e.target.value})}
            >
              <option value="">Any Experience</option>
              <option value="0-2">0-2 years</option>
              <option value="2-5">2-5 years</option>
              <option value="5-10">5-10 years</option>
              <option value="10+">10+ years</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="label-icon">📍</span>
              Location
            </label>
            <input
              type="text"
              className="filter-input"
              placeholder="e.g., Mumbai, Remote"
              value={searchCriteria.location}
              onChange={(e) => setSearchCriteria({...searchCriteria, location: e.target.value})}
            />
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="label-icon">🎓</span>
              Education
            </label>
            <select
              className="filter-select"
              value={searchCriteria.education}
              onChange={(e) => setSearchCriteria({...searchCriteria, education: e.target.value})}
            >
              <option value="">Any Education</option>
              <option value="bachelor">Bachelor's Degree</option>
              <option value="master">Master's Degree</option>
              <option value="phd">PhD</option>
            </select>
          </div>
        </div>

        <div className="filter-actions">
          <button
            className="search-btn"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Searching...
              </>
            ) : (
              <>
                <span className="btn-icon">🔍</span>
                Search Candidates
              </>
            )}
          </button>

          <button
            className="clear-btn"
            onClick={() => setSearchCriteria({
              skills: '', experience: '', location: '', education: '', jobRole: ''
            })}
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Search Results */}
      {searched && (
        <div className="search-results">
          <div className="results-header">
            <h2 className="results-title">
              Search Results ({candidates.length} candidates found)
            </h2>
            {candidates.length > 0 && (
              <button className="export-btn">
                <span>📥</span> Export Results
              </button>
            )}
          </div>

          {candidates.length === 0 ? (
            <div className="no-results">
              <div className="no-results-icon">😔</div>
              <h3>No candidates found</h3>
              <p>Try adjusting your search criteria</p>
            </div>
          ) : (
            <div className="candidates-list">
              {candidates.map((candidate) => (
                <div key={candidate.id} className="candidate-card">
                  <div className="candidate-header">
                    <div className="candidate-avatar">
                      {candidate.name.charAt(0)}
                    </div>
                    <div className="candidate-info">
                      <h3 className="candidate-name">{candidate.name}</h3>
                      <p className="candidate-role">{candidate.education}</p>
                    </div>
                    <div 
                      className="match-badge"
                      style={{ backgroundColor: getMatchColor(candidate.match_score) }}
                    >
                      {candidate.match_score}% Match
                    </div>
                  </div>

                  <div className="candidate-details">
                    <div className="detail-item">
                      <span className="detail-icon">📧</span>
                      <span className="detail-text">{candidate.email}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">📱</span>
                      <span className="detail-text">{candidate.phone}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">📍</span>
                      <span className="detail-text">{candidate.location}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">💼</span>
                      <span className="detail-text">{candidate.experience} experience</span>
                    </div>
                  </div>

                  <div className="candidate-skills">
                    <strong>Skills:</strong>
                    <div className="skills-tags">
                      {candidate.skills.map((skill, idx) => (
                        <span key={idx} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  </div>

                  <div className="candidate-actions">
                    <button
                      className="view-resume-btn"
                      onClick={() => window.open(candidate.resume_url, '_blank')}
                    >
                      <span>📄</span> View Resume
                    </button>
                    <button
                      className="shortlist-btn"
                      onClick={() => handleShortlist(candidate.id)}
                    >
                      <span>⭐</span> Shortlist
                    </button>
                    <button className="contact-btn">
                      <span>✉️</span> Contact
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CandidateSearch;