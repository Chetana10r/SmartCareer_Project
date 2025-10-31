// src/components/MockTest/TestHistory.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './MockTest.css';

const TestHistory = () => {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const userId = localStorage.getItem('user_id') || 'guest';
      const response = await axios.get(`http://localhost:5000/api/test_history/${userId}`);
      setHistory(response.data.history);
      setStats(response.data.stats);
    } catch (error) {
      console.error('Error fetching history:', error);
      alert('Failed to load test history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getScoreColor = (score, total) => {
    const percentage = (score / total) * 100;
    if (percentage >= 80) return '#4caf50';
    if (percentage >= 60) return '#ff9800';
    return '#f44336';
  };

  const viewResult = async (attemptId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/test_result/${attemptId}`);
      navigate('/mock-test/result', { 
        state: { 
          result: {
            score: response.data.score,
            total: response.data.total_questions,
            percentage: (response.data.score / response.data.total_questions) * 100,
            results: response.data.answers,
            time_taken: response.data.time_taken,
            passed: (response.data.score / response.data.total_questions) >= 0.6
          },
          subject: response.data.subject
        } 
      });
    } catch (error) {
      console.error('Error loading result:', error);
      alert('Failed to load result details');
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading your history...</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h1>📜 Test History</h1>
        <button onClick={() => navigate('/mock-test')} className="back-btn">
          ← Back to Tests
        </button>
      </div>

      {stats && (
        <div className="stats-summary">
          <div className="stat-card">
            <div style={{ fontSize: '2.5rem', color: '#2196f3' }}>🏆</div>
            <div>
              <h3>{stats.total_tests}</h3>
              <p>Total Tests</p>
            </div>
          </div>
          <div className="stat-card">
            <div style={{ fontSize: '2.5rem', color: '#4caf50' }}>📊</div>
            <div>
              <h3>{stats.average_score.toFixed(1)}%</h3>
              <p>Average Score</p>
            </div>
          </div>
          <div className="stat-card">
            <div style={{ fontSize: '2.5rem', color: '#ff9800' }}>📚</div>
            <div>
              <h3>{stats.subjects_attempted.length}</h3>
              <p>Subjects Attempted</p>
            </div>
          </div>
        </div>
      )}

      {history.length === 0 ? (
        <div className="no-history">
          <p>No test history found. Take your first test!</p>
          <button onClick={() => navigate('/mock-test')} className="start-test-btn">
            Start a Test
          </button>
        </div>
      ) : (
        <div className="history-list">
          <h2>Recent Tests</h2>
          {history.map((attempt) => {
            const percentage = (attempt.score / attempt.total_questions) * 100;
            return (
              <div key={attempt.attempt_id} className="history-item">
                <div className="history-left">
                  <h3>{attempt.subject}</h3>
                  <div className="history-meta">
                    <span>📅 {formatDate(attempt.timestamp)}</span>
                    <span>⏱️ {formatTime(attempt.time_taken)}</span>
                  </div>
                </div>
                
                <div className="history-right">
                  <div 
                    className="score-badge"
                    style={{ 
                      backgroundColor: getScoreColor(attempt.score, attempt.total_questions) 
                    }}
                  >
                    {percentage.toFixed(0)}%
                  </div>
                  <span className="score-text">
                    {attempt.score}/{attempt.total_questions}
                  </span>
                  <button 
                    onClick={() => viewResult(attempt.attempt_id)}
                    className="view-btn"
                  >
                    View Details
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default TestHistory;