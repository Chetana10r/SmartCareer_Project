import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ShortlistManager.css';

function ShortlistManager() {
  const navigate = useNavigate();
  const [shortlistedCandidates, setShortlistedCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedCandidates, setSelectedCandidates] = useState([]);

  useEffect(() => {
    fetchShortlistedCandidates();
  }, []);

  const fetchShortlistedCandidates = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_shortlisted', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruiter_id: localStorage.getItem('userId') || 'recruiter_1'
        })
      });

      const data = await response.json();
      setShortlistedCandidates(data.candidates || []);
    } catch (error) {
      console.error('Error fetching shortlisted candidates:', error);
      // Mock data for demo
      setShortlistedCandidates([
        {
          id: 1,
          name: 'Rahul Sharma',
          email: 'rahul.sharma@email.com',
          phone: '+91-9876543210',
          job_applied: 'Senior Data Scientist',
          match_score: 92,
          status: 'shortlisted',
          shortlisted_date: '2025-10-28',
          experience: '3 years',
          location: 'Mumbai, India',
          skills: ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
          resume_url: '/resumes/rahul_sharma.pdf',
          notes: 'Strong ML background, excellent communication'
        },
        {
          id: 2,
          name: 'Priya Patel',
          email: 'priya.patel@email.com',
          phone: '+91-9876543211',
          job_applied: 'Full Stack Developer',
          match_score: 88,
          status: 'interview_scheduled',
          shortlisted_date: '2025-10-26',
          interview_date: '2025-11-05',
          experience: '5 years',
          location: 'Bangalore, India',
          skills: ['React', 'Node.js', 'MongoDB', 'AWS'],
          resume_url: '/resumes/priya_patel.pdf',
          notes: 'Great portfolio, ready to join immediately'
        },
        {
          id: 3,
          name: 'Amit Kumar',
          email: 'amit.kumar@email.com',
          phone: '+91-9876543212',
          job_applied: 'DevOps Engineer',
          match_score: 85,
          status: 'contacted',
          shortlisted_date: '2025-10-25',
          experience: '4 years',
          location: 'Delhi, India',
          skills: ['Docker', 'Kubernetes', 'CI/CD', 'AWS'],
          resume_url: '/resumes/amit_kumar.pdf',
          notes: 'Strong DevOps experience'
        },
        {
          id: 4,
          name: 'Sneha Reddy',
          email: 'sneha.reddy@email.com',
          phone: '+91-9876543213',
          job_applied: 'Senior Data Scientist',
          match_score: 90,
          status: 'rejected',
          shortlisted_date: '2025-10-20',
          experience: '6 years',
          location: 'Hyderabad, India',
          skills: ['Python', 'Deep Learning', 'NLP', 'PyTorch'],
          resume_url: '/resumes/sneha_reddy.pdf',
          notes: 'Salary expectations too high'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'shortlisted': { color: '#f39c12', text: 'Shortlisted', icon: '⭐' },
      'contacted': { color: '#3498db', text: 'Contacted', icon: '📧' },
      'interview_scheduled': { color: '#9b59b6', text: 'Interview Scheduled', icon: '📅' },
      'rejected': { color: '#e74c3c', text: 'Rejected', icon: '❌' },
      'hired': { color: '#2ecc71', text: 'Hired', icon: '✅' }
    };
    return badges[status] || badges['shortlisted'];
  };

  const updateStatus = async (candidateId, newStatus) => {
    try {
      await fetch('http://127.0.0.1:5000/update_candidate_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidateId,
          status: newStatus
        })
      });

      setShortlistedCandidates(prev =>
        prev.map(c => c.id === candidateId ? { ...c, status: newStatus } : c)
      );
    } catch (error) {
      console.error('Error updating status:', error);
      // Update locally for demo
      setShortlistedCandidates(prev =>
        prev.map(c => c.id === candidateId ? { ...c, status: newStatus } : c)
      );
    }
  };

  const scheduleInterview = (candidateId) => {
    const date = prompt('Enter interview date (YYYY-MM-DD):');
    if (date) {
      updateStatus(candidateId, 'interview_scheduled');
      alert(`Interview scheduled for ${date}`);
    }
  };

  const removeFromShortlist = async (candidateId) => {
    if (window.confirm('Remove this candidate from shortlist?')) {
      try {
        await fetch('http://127.0.0.1:5000/remove_from_shortlist', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ candidate_id: candidateId })
        });

        setShortlistedCandidates(prev => prev.filter(c => c.id !== candidateId));
      } catch (error) {
        console.error('Error removing candidate:', error);
        setShortlistedCandidates(prev => prev.filter(c => c.id !== candidateId));
      }
    }
  };

  const toggleSelectCandidate = (candidateId) => {
    setSelectedCandidates(prev =>
      prev.includes(candidateId)
        ? prev.filter(id => id !== candidateId)
        : [...prev, candidateId]
    );
  };

  const bulkAction = (action) => {
    if (selectedCandidates.length === 0) {
      alert('Please select candidates first');
      return;
    }

    switch (action) {
      case 'email':
        alert(`Sending email to ${selectedCandidates.length} candidates`);
        break;
      case 'schedule':
        alert(`Scheduling interviews for ${selectedCandidates.length} candidates`);
        break;
      case 'reject':
        if (window.confirm(`Reject ${selectedCandidates.length} candidates?`)) {
          selectedCandidates.forEach(id => updateStatus(id, 'rejected'));
        }
        break;
      default:
        break;
    }
    setSelectedCandidates([]);
  };

  const filteredCandidates = filterStatus === 'all'
    ? shortlistedCandidates
    : shortlistedCandidates.filter(c => c.status === filterStatus);

  const stats = {
    total: shortlistedCandidates.length,
    shortlisted: shortlistedCandidates.filter(c => c.status === 'shortlisted').length,
    interviewed: shortlistedCandidates.filter(c => c.status === 'interview_scheduled').length,
    hired: shortlistedCandidates.filter(c => c.status === 'hired').length
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner-large"></div>
        <p>Loading shortlisted candidates...</p>
      </div>
    );
  }

  return (
    <div className="shortlist-manager-container">
      <div className="manager-header">
        <button className="back-btn" onClick={() => navigate('/recruiter-dashboard')}>
          ← Back to Dashboard
        </button>
        <h1 className="manager-title">
          <span className="title-icon">📝</span>
          Shortlist Manager
        </h1>
        <p className="manager-subtitle">Manage and track shortlisted candidates</p>
      </div>

      {/* Stats */}
      <div className="shortlist-stats">
        <div className="stat-item">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Shortlisted</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{stats.shortlisted}</div>
          <div className="stat-label">Pending Review</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{stats.interviewed}</div>
          <div className="stat-label">Interviews Scheduled</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{stats.hired}</div>
          <div className="stat-label">Hired</div>
        </div>
      </div>

      {/* Filters and Actions */}
      <div className="controls-bar">
        <div className="filter-section">
          <label className="filter-label">Filter by Status:</label>
          <select
            className="status-filter"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Candidates</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="contacted">Contacted</option>
            <option value="interview_scheduled">Interview Scheduled</option>
            <option value="rejected">Rejected</option>
            <option value="hired">Hired</option>
          </select>
        </div>

        {selectedCandidates.length > 0 && (
          <div className="bulk-actions">
            <span className="selected-count">
              {selectedCandidates.length} selected
            </span>
            <button className="bulk-btn email" onClick={() => bulkAction('email')}>
              ✉️ Send Email
            </button>
            <button className="bulk-btn schedule" onClick={() => bulkAction('schedule')}>
              📅 Schedule Interview
            </button>
            <button className="bulk-btn reject" onClick={() => bulkAction('reject')}>
              ❌ Reject
            </button>
          </div>
        )}
      </div>

      {/* Candidates List */}
      {filteredCandidates.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>No candidates found</h3>
          <p>No candidates match the selected filter</p>
          <button className="primary-btn" onClick={() => navigate('/search-candidates')}>
            Search Candidates
          </button>
        </div>
      ) : (
        <div className="candidates-table">
          <div className="table-header">
            <div className="header-cell checkbox-cell">
              <input
                type="checkbox"
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedCandidates(filteredCandidates.map(c => c.id));
                  } else {
                    setSelectedCandidates([]);
                  }
                }}
                checked={selectedCandidates.length === filteredCandidates.length}
              />
            </div>
            <div className="header-cell">Candidate</div>
            <div className="header-cell">Job Applied</div>
            <div className="header-cell">Match Score</div>
            <div className="header-cell">Status</div>
            <div className="header-cell">Date</div>
            <div className="header-cell">Actions</div>
          </div>

          {filteredCandidates.map((candidate) => (
            <div key={candidate.id} className="table-row">
              <div className="table-cell checkbox-cell">
                <input
                  type="checkbox"
                  checked={selectedCandidates.includes(candidate.id)}
                  onChange={() => toggleSelectCandidate(candidate.id)}
                />
              </div>

              <div className="table-cell candidate-cell">
                <div className="candidate-avatar">
                  {candidate.name.charAt(0)}
                </div>
                <div className="candidate-details">
                  <div className="candidate-name">{candidate.name}</div>
                  <div className="candidate-contact">
                    <span>📧 {candidate.email}</span>
                    <span>📱 {candidate.phone}</span>
                  </div>
                  <div className="candidate-skills">
                    {candidate.skills.slice(0, 3).map((skill, idx) => (
                      <span key={idx} className="skill-tag-small">{skill}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="table-cell">
                <strong>{candidate.job_applied}</strong>
                <div className="job-meta">
                  <span>📍 {candidate.location}</span>
                  <span>💼 {candidate.experience}</span>
                </div>
              </div>

              <div className="table-cell">
                <div className="match-score-badge">
                  {candidate.match_score}%
                </div>
              </div>

              <div className="table-cell">
                <span
                  className="status-badge"
                  style={{ backgroundColor: getStatusBadge(candidate.status).color }}
                >
                  {getStatusBadge(candidate.status).icon} {getStatusBadge(candidate.status).text}
                </span>
              </div>

              <div className="table-cell">
                <div className="date-info">
                  <div>Shortlisted: {candidate.shortlisted_date}</div>
                  {candidate.interview_date && (
                    <div className="interview-date">
                      Interview: {candidate.interview_date}
                    </div>
                  )}
                </div>
              </div>

              <div className="table-cell actions-cell">
                <div className="action-dropdown">
                  <button className="action-btn-small">⋮</button>
                  <div className="dropdown-menu">
                    <button onClick={() => window.open(candidate.resume_url, '_blank')}>
                      📄 View Resume
                    </button>
                    <button onClick={() => scheduleInterview(candidate.id)}>
                      📅 Schedule Interview
                    </button>
                    <button onClick={() => updateStatus(candidate.id, 'contacted')}>
                      📧 Mark as Contacted
                    </button>
                    <button onClick={() => updateStatus(candidate.id, 'hired')}>
                      ✅ Mark as Hired
                    </button>
                    <button onClick={() => updateStatus(candidate.id, 'rejected')}>
                      ❌ Reject
                    </button>
                    <button
                      className="danger"
                      onClick={() => removeFromShortlist(candidate.id)}
                    >
                      🗑️ Remove from Shortlist
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ShortlistManager;