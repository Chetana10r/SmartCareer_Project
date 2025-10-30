import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './InterviewFeedback.css';

function InterviewFeedback() {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId, results } = location.state || {};

  const [feedbackData, setFeedbackData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) {
      navigate('/mock-interview');
      return;
    }

    // If results passed from session, use them
    if (results) {
      setFeedbackData(results);
      setLoading(false);
    } else {
      // Otherwise fetch from backend
      fetchFeedback();
    }
  }, [sessionId]);

  const fetchFeedback = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      const data = await response.json();
      setFeedbackData(data);
    } catch (error) {
      console.error('Error fetching feedback:', error);
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

  const getScoreLabel = (score) => {
    if (score >= 8) return 'Excellent';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Average';
    return 'Needs Improvement';
  };

  if (loading) {
    return (
      <div className="feedback-loading">
        <div className="spinner-large"></div>
        <p>Generating your detailed feedback report...</p>
      </div>
    );
  }

  if (!feedbackData) {
    return (
      <div className="feedback-error">
        <h2>Unable to load feedback</h2>
        <button onClick={() => navigate('/mock-interview')}>
          Start New Interview
        </button>
      </div>
    );
  }

  const {
    overall_score,
    confidence_score,
    clarity_score,
    technical_score,
    questions_feedback,
    strengths,
    weaknesses,
    recommendations,
    soft_skills,
    question_scores
  } = feedbackData;

  // Chart data
  const skillsData = [
    { skill: 'Technical', score: technical_score || 7 },
    { skill: 'Communication', score: clarity_score || 8 },
    { skill: 'Confidence', score: confidence_score || 7.5 },
    { skill: 'Problem Solving', score: soft_skills?.problem_solving || 7 }
  ];

  const radarData = [
    { subject: 'Technical Knowledge', score: technical_score || 7, fullMark: 10 },
    { subject: 'Communication', score: clarity_score || 8, fullMark: 10 },
    { subject: 'Confidence', score: confidence_score || 7.5, fullMark: 10 },
    { subject: 'Clarity', score: clarity_score || 8, fullMark: 10 },
    { subject: 'Problem Solving', score: soft_skills?.problem_solving || 7, fullMark: 10 }
  ];

  const questionScoresData = question_scores?.map((score, idx) => ({
    question: `Q${idx + 1}`,
    score: score
  })) || [];

  return (
    <div className="feedback-container">
      {/* Header */}
      <div className="feedback-header">
        <div className="header-content">
          <h1 className="feedback-title">
            <span className="title-icon">📊</span>
            Interview Performance Report
          </h1>
          <p className="feedback-subtitle">
            Detailed analysis of your interview performance
          </p>
        </div>
      </div>

      {/* Overall Score */}
      <div className="score-showcase">
        <div className="score-circle-large" style={{ borderColor: getScoreColor(overall_score) }}>
          <div className="score-value">{overall_score?.toFixed(1) || '7.5'}</div>
          <div className="score-max">/ 10</div>
          <div className="score-label">{getScoreLabel(overall_score)}</div>
        </div>
        
        <div className="score-details">
          <div className="score-item">
            <span className="score-icon">💪</span>
            <div className="score-info">
              <span className="score-name">Confidence</span>
              <span className="score-number">{confidence_score?.toFixed(1) || '7.5'}/10</span>
            </div>
            <div className="score-bar">
              <div 
                className="score-bar-fill" 
                style={{ 
                  width: `${(confidence_score || 7.5) * 10}%`,
                  background: getScoreColor(confidence_score || 7.5)
                }}
              />
            </div>
          </div>

          <div className="score-item">
            <span className="score-icon">💬</span>
            <div className="score-info">
              <span className="score-name">Communication</span>
              <span className="score-number">{clarity_score?.toFixed(1) || '8.0'}/10</span>
            </div>
            <div className="score-bar">
              <div 
                className="score-bar-fill" 
                style={{ 
                  width: `${(clarity_score || 8) * 10}%`,
                  background: getScoreColor(clarity_score || 8)
                }}
              />
            </div>
          </div>

          <div className="score-item">
            <span className="score-icon">🎯</span>
            <div className="score-info">
              <span className="score-name">Technical Skills</span>
              <span className="score-number">{technical_score?.toFixed(1) || '7.0'}/10</span>
            </div>
            <div className="score-bar">
              <div 
                className="score-bar-fill" 
                style={{ 
                  width: `${(technical_score || 7) * 10}%`,
                  background: getScoreColor(technical_score || 7)
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-card">
          <h3 className="chart-title">📈 Skills Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={skillsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Bar dataKey="score" fill="#42e695" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">🎯 Performance Radar</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" />
              <PolarRadiusAxis domain={[0, 10]} />
              <Radar name="Your Score" dataKey="score" stroke="#667eea" fill="#667eea" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {questionScoresData.length > 0 && (
        <div className="chart-card full-width">
          <h3 className="chart-title">📊 Question-wise Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={questionScoresData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="question" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#42e695" strokeWidth={3} dot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      <div className="insights-section">
        <div className="insight-card strengths">
          <h3 className="insight-title">
            <span className="insight-icon">✅</span>
            Key Strengths
          </h3>
          <ul className="insight-list">
            {strengths?.map((strength, idx) => (
              <li key={idx}>{strength}</li>
            )) || [
              'Clear communication and articulation',
              'Good technical understanding',
              'Structured approach to problem-solving'
            ]}
          </ul>
        </div>

        <div className="insight-card weaknesses">
          <h3 className="insight-title">
            <span className="insight-icon">⚠️</span>
            Areas for Improvement
          </h3>
          <ul className="insight-list">
            {weaknesses?.map((weakness, idx) => (
              <li key={idx}>{weakness}</li>
            )) || [
              'Add more real-world examples',
              'Reduce filler words (um, uh)',
              'Provide more detailed explanations'
            ]}
          </ul>
        </div>
      </div>

      {/* Question-wise Feedback */}
      {questions_feedback && questions_feedback.length > 0 && (
        <div className="questions-feedback-section">
          <h3 className="section-title">
            <span className="section-icon">💬</span>
            Detailed Question Analysis
          </h3>
          {questions_feedback.map((qf, idx) => (
            <div key={idx} className="question-feedback-card">
              <div className="question-header">
                <span className="question-number">Question {idx + 1}</span>
                <span 
                  className="question-score"
                  style={{ color: getScoreColor(qf.score) }}
                >
                  {qf.score?.toFixed(1)}/10
                </span>
              </div>
              <div className="question-text">{qf.question}</div>
              <div className="answer-section">
                <strong>Your Answer:</strong>
                <p>{qf.answer || 'No answer recorded'}</p>
              </div>
              <div className="feedback-section">
                <strong>💡 Feedback:</strong>
                <p>{qf.feedback}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Recommendations */}
      <div className="recommendations-section">
        <h3 className="section-title">
          <span className="section-icon">💡</span>
          Personalized Recommendations
        </h3>
        <div className="recommendations-grid">
          {recommendations?.map((rec, idx) => (
            <div key={idx} className="recommendation-card">
              <div className="rec-icon">{rec.icon || '📚'}</div>
              <div className="rec-content">
                <h4>{rec.title}</h4>
                <p>{rec.description}</p>
                {rec.link && (
                  <a href={rec.link} target="_blank" rel="noopener noreferrer" className="rec-link">
                    Learn More →
                  </a>
                )}
              </div>
            </div>
          )) || [
            {
              icon: '📚',
              title: 'Practice STAR Method',
              description: 'Structure your answers using Situation, Task, Action, Result framework',
              link: 'https://www.themuse.com/advice/star-interview-method'
            },
            {
              icon: '🎯',
              title: 'Technical Deep Dive',
              description: 'Strengthen your understanding of core technical concepts',
              link: 'https://www.geeksforgeeks.org'
            },
            {
              icon: '💬',
              title: 'Communication Skills',
              description: 'Work on clarity and reduce filler words in your responses',
              link: 'https://www.coursera.org/learn/communication-skills'
            }
          ].map((rec, idx) => (
            <div key={idx} className="recommendation-card">
              <div className="rec-icon">{rec.icon}</div>
              <div className="rec-content">
                <h4>{rec.title}</h4>
                <p>{rec.description}</p>
                <a href={rec.link} target="_blank" rel="noopener noreferrer" className="rec-link">
                  Learn More →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-section">
        <button 
          className="primary-button"
          onClick={() => navigate('/mock-interview')}
        >
          <span className="button-icon">🔄</span>
          <span>Take Another Interview</span>
        </button>
        
        <button 
          className="secondary-button"
          onClick={() => navigate('/interview-history')}
        >
          <span className="button-icon">📜</span>
          <span>View History</span>
        </button>

        <button 
          className="download-button"
          onClick={() => window.print()}
        >
          <span className="button-icon">📥</span>
          <span>Download Report</span>
        </button>
      </div>
    </div>
  );
}

export default InterviewFeedback;