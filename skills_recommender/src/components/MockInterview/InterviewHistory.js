import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './InterviewHistory.css';

function InterviewHistory() {
  const navigate = useNavigate();
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_interview_history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'user123' })
      });

      const data = await response.json();
      setInterviews(data.interviews || []);
    } catch (error) {
      console.error('Error fetching history:', error);
      // Mock data for demo
      setInterviews([
        {
          session_id: '1',
          job_role: 'Data Scientist',
          interview_type: 'technical',
          overall_score: 7.5,
          date: '2025-10-28',
          duration: 20,
          questions_answered: 5
        },
        {
          session_id: '2',
          job_role: 'Software Engineer',
          interview_type: 'mixed',
          overall_score: 8.2,
          date: '2025-10-25',
          duration: 20,
          questions_answered: 5
        },
        {
          session_id: '3',
          job_role: 'Product Manager',
          interview_type: 'hr',
          overall_score: 6.8,
          date: '2025-10-22',
          duration: 15,
          questions_answered: 4
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8) return '#42e695';
    if (score >= 6) return '#ffc107';
    if (score >= 4) return '#ff9800';
    return '#ff6b6b';
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'technical':
        return '💻';
      case 'hr':
        return '👔';
      case 'mixed':
        return '🎯';
      default:
        return '📋';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const viewDetails = (sessionId) => {
    navigate('/interview-feedback', { state: { sessionId } });
  };

  const filteredInterviews = interviews
    .filter(interview => filter === 'all' || interview.interview_type === filter)
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.date) - new Date(a.date);
      }
      return b.overall_score - a.overall_score;
    });

  // Statistics
  const stats = {
    total: interviews.length,
    avgScore: interviews.length > 0 
      ? (interviews.reduce((sum, i) => sum + i.overall_score, 0) / interviews.length).toFixed(1)
      : 0,
    highest: interviews.length > 0 
      ? Math.max(...interviews.map(i => i.overall_score)).toFixed(1)
      : 0,
    totalQuestions: interviews.reduce((sum, i) => sum + (i.questions_answered || 0), 0)
  };

  // Progress chart data
  const progressData = interviews
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .map(interview => ({
      date: formatDate(interview.date),
      score: interview.overall_score
    }));

  if (loading) {
    return (
      <div className="history-loading">
        <div className="spinner-large"></div>
        <p>Loading your interview history...</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      {/* Header */}
      <div className="history-header">
        <div className="header-content">
          <h1 className="history-title">
            <span className="title-icon">📜</span>
            Interview History
          </h1>
          <p className="history-subtitle">
            Track your progress and review past performances
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-section">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Interviews</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <div className="stat-value">{stats.avgScore}</div>
            <div className="stat-label">Average Score</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <div className="stat-value">{stats.highest}</div>
            <div className="stat-label">Highest Score</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalQuestions}</div>
            <div className="stat-label">Questions Answered</div>
          </div>
        </div>
      </div>

      {/* Progress Chart */}
      {progressData.length > 1 && (
        <div className="chart-section">
          <h3 className="chart-title">📈 Your Progress Over Time</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={progressData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 10]} />
                <Tooltip 
                  contentStyle={{ background: '#fff', border: '1px solid #ccc' }}
                  formatter={(value) => value.toFixed(1)}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#42e695" 
                  strokeWidth={3}
                  dot={{ r: 6, fill: '#42e695' }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label className="filter-label">Type:</label>
          <select 
            className="filter-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="technical">Technical</option>
            <option value="hr">HR/Behavioral</option>
            <option value="mixed">Mixed</option>
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Sort by:</label>
          <select 
            className="filter-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="date">Date (Newest)</option>
            <option value="score">Score (Highest)</option>
          </select>
        </div>
      </div>

      {/* Interview Cards */}
      {filteredInterviews.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h2>No Interviews Found</h2>
          <p>Start your first mock interview to see it here!</p>
          <button 
            className="start-button"
            onClick={() => navigate('/mock-interview')}
          >
            <span className="button-icon">🚀</span>
            <span>Start Interview</span>
          </button>
        </div>
      ) : (
        <div className="interviews-grid">
          {filteredInterviews.map((interview) => (
            <div key={interview.session_id} className="interview-card">
              <div className="card-header">
                <div className="type-badge">
                  <span className="type-icon">{getTypeIcon(interview.interview_type)}</span>
                  <span className="type-text">{interview.interview_type}</span>
                </div>
                <div 
                  className="score-badge"
                  style={{ backgroundColor: getScoreColor(interview.overall_score) }}
                >
                  {interview.overall_score.toFixed(1)}
                </div>
              </div>

              <div className="card-body">
                <h3 className="job-role">{interview.job_role}</h3>
                
                <div className="interview-details">
                  <div className="detail-item">
                    <span className="detail-icon">📅</span>
                    <span className="detail-text">{formatDate(interview.date)}</span>
                  </div>
                  
                  <div className="detail-item">
                    <span className="detail-icon">⏱️</span>
                    <span className="detail-text">{interview.duration} minutes</span>
                  </div>
                  
                  <div className="detail-item">
                    <span className="detail-icon">💬</span>
                    <span className="detail-text">{interview.questions_answered} questions</span>
                  </div>
                </div>
              </div>

              <div className="card-footer">
                <button 
                  className="view-button"
                  onClick={() => viewDetails(interview.session_id)}
                >
                  View Details →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Action Button */}
      <div className="action-section">
        <button 
          className="new-interview-button"
          onClick={() => navigate('/mock-interview')}
        >
          <span className="button-icon">➕</span>
          <span>Start New Interview</span>
        </button>
      </div>
    </div>
  );
}

export default InterviewHistory;