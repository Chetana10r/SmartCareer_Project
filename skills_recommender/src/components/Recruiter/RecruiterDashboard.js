import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './RecruiterDashboard.css';

function RecruiterDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    activeJobs: 0,
    totalCandidates: 0,
    shortlisted: 0,
    interviewed: 0
  });

  const [recentJobs, setRecentJobs] = useState([]);
  const [recentCandidates, setRecentCandidates] = useState([]);

  useEffect(() => {
    // Check if user is recruiter
    const userRole = localStorage.getItem('userRole');
    if (userRole !== 'recruiter') {
      navigate('/role-selection');
      return;
    }

    fetchDashboardData();
  }, [navigate]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/recruiter_dashboard', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      setStats(data.stats || stats);
      setRecentJobs(data.recent_jobs || []);
      setRecentCandidates(data.recent_candidates || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use mock data for demo
      setStats({
        activeJobs: 8,
        totalCandidates: 124,
        shortlisted: 23,
        interviewed: 12
      });
      setRecentJobs([
        { id: 1, title: 'Senior Data Scientist', applications: 45, posted: '2 days ago' },
        { id: 2, title: 'Full Stack Developer', applications: 67, posted: '5 days ago' },
        { id: 3, title: 'Machine Learning Engineer', applications: 34, posted: '1 week ago' }
      ]);
    }
  };

  const logout = () => {
    localStorage.removeItem('userRole');
    navigate('/role-selection');
  };

  return (
    <div className="recruiter-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-left">
          <h1 className="dashboard-title">
            <span className="title-icon">💼</span>
            Recruiter Dashboard
          </h1>
          <p className="dashboard-subtitle">Manage jobs and candidates efficiently</p>
        </div>
        <div className="header-right">
          <button className="logout-btn" onClick={logout}>
            <span>🚪</span> Logout
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card active-jobs">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-value">{stats.activeJobs}</div>
            <div className="stat-label">Active Jobs</div>
          </div>
        </div>

        <div className="stat-card total-candidates">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalCandidates}</div>
            <div className="stat-label">Total Candidates</div>
          </div>
        </div>

        <div className="stat-card shortlisted">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <div className="stat-value">{stats.shortlisted}</div>
            <div className="stat-label">Shortlisted</div>
          </div>
        </div>

        <div className="stat-card interviewed">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-value">{stats.interviewed}</div>
            <div className="stat-label">Interviewed</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2 className="section-title">Quick Actions</h2>
        <div className="actions-grid">
          <div className="action-card" onClick={() => navigate('/post-job')}>
            <div className="action-icon">➕</div>
            <h3>Post New Job</h3>
            <p>Create and publish a new job opening</p>
          </div>

          <div className="action-card" onClick={() => navigate('/search-candidates')}>
            <div className="action-icon">🔍</div>
            <h3>Search Candidates</h3>
            <p>Find candidates matching your criteria</p>
          </div>

          <div className="action-card" onClick={() => navigate('/resume-matching')}>
            <div className="action-icon">🎯</div>
            <h3>Match Resumes</h3>
            <p>AI-powered resume matching to job</p>
          </div>

          <div className="action-card" onClick={() => navigate('/shortlist-manager')}>
            <div className="action-icon">📝</div>
            <h3>Manage Shortlist</h3>
            <p>View and manage shortlisted candidates</p>
          </div>

          <div className="action-card" onClick={() => navigate('/job-listings')}>
            <div className="action-icon">📊</div>
            <h3>View All Jobs</h3>
            <p>See all your job postings</p>
          </div>

          <div className="action-card" onClick={() => navigate('/analytics')}>
            <div className="action-icon">📈</div>
            <h3>Analytics</h3>
            <p>View hiring statistics and trends</p>
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      {recentJobs.length > 0 && (
        <div className="recent-section">
          <h2 className="section-title">Recent Job Postings</h2>
          <div className="recent-jobs-list">
            {recentJobs.map((job) => (
              <div key={job.id} className="job-item">
                <div className="job-info">
                  <h3 className="job-title">{job.title}</h3>
                  <p className="job-meta">
                    <span>📬 {job.applications} applications</span>
                    <span>📅 Posted {job.posted}</span>
                  </p>
                </div>
                <button className="view-btn" onClick={() => navigate(`/job/${job.id}`)}>
                  View Details →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tips Section */}
      <div className="tips-section">
        <h2 className="section-title">💡 Hiring Tips</h2>
        <div className="tips-grid">
          <div className="tip-card">
            <span className="tip-icon">🎯</span>
            <p>Use AI matching to find the best candidates faster</p>
          </div>
          <div className="tip-card">
            <span className="tip-icon">📝</span>
            <p>Clear job descriptions attract quality candidates</p>
          </div>
          <div className="tip-card">
            <span className="tip-icon">⚡</span>
            <p>Respond quickly to increase candidate engagement</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecruiterDashboard;