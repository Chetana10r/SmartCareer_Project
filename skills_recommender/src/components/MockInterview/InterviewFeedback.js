import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LineChart, Line, BarChart, Bar, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './InterviewFeedback.css';

function InterviewFeedback() {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId, results } = location.state || {};

  const [feedbackData, setFeedbackData] = useState(null);
  const [loading, setLoading] = useState(true);

  // ✅ Wrapped fetchFeedback inside useCallback
  const fetchFeedback = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/interview/get_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      const data = await response.json();
      setFeedbackData(data);
    } catch (error) {
      console.error('Error fetching feedback:', error);
      setFeedbackData({
        overall_score: 7.5,
        confidence_score: 7.5,
        clarity_score: 7.5,
        technical_score: 7.5,
        strengths: ['Good communication', 'Technical knowledge'],
        weaknesses: ['Add more examples'],
        recommendations: [],
        question_scores: [7.5, 8.0, 7.0, 7.5, 8.5]
      });
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) {
      navigate('/mock-interview');
      return;
    }

    if (results) {
      setFeedbackData(results);
      setLoading(false);
    } else {
      fetchFeedback();
    }
  }, [sessionId, navigate, results, fetchFeedback]); // ✅ All dependencies included

  // Helper functions
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
    overall_score = 7.5,
    confidence_score = 7.5,
    clarity_score = 8.0,
    technical_score = 7.0,
    questions_feedback = [],
    strengths = [],
    weaknesses = [],
    recommendations = [],
    soft_skills = {},
    question_scores = []
  } = feedbackData;

  // Chart data
  const skillsData = [
    { skill: 'Technical', score: technical_score },
    { skill: 'Communication', score: clarity_score },
    { skill: 'Confidence', score: confidence_score },
    { skill: 'Problem Solving', score: soft_skills?.problem_solving || 7 }
  ];

  const radarData = [
    { subject: 'Technical Knowledge', score: technical_score, fullMark: 10 },
    { subject: 'Communication', score: clarity_score, fullMark: 10 },
    { subject: 'Confidence', score: confidence_score, fullMark: 10 },
    { subject: 'Clarity', score: clarity_score, fullMark: 10 },
    { subject: 'Problem Solving', score: soft_skills?.problem_solving || 7, fullMark: 10 }
  ];

  const questionScoresData = question_scores?.length > 0
    ? question_scores.map((score, idx) => ({
        question: `Q${idx + 1}`,
        score: score
      }))
    : [
        { question: 'Q1', score: 7.5 },
        { question: 'Q2', score: 8.0 },
        { question: 'Q3', score: 7.0 },
        { question: 'Q4', score: 7.5 },
        { question: 'Q5', score: 8.5 }
      ];

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
          <div className="score-value">{overall_score.toFixed(1)}</div>
          <div className="score-max">/ 10</div>
          <div className="score-label">{getScoreLabel(overall_score)}</div>
        </div>

        <div className="score-details">
          {[
            { icon: '💪', name: 'Confidence', value: confidence_score },
            { icon: '💬', name: 'Communication', value: clarity_score },
            { icon: '🎯', name: 'Technical Skills', value: technical_score }
          ].map((item, index) => (
            <div key={index} className="score-item">
              <span className="score-icon">{item.icon}</span>
              <div className="score-info">
                <span className="score-name">{item.name}</span>
                <span className="score-number">{item.value.toFixed(1)}/10</span>
              </div>
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{
                    width: `${item.value * 10}%`,
                    background: getScoreColor(item.value)
                  }}
                />
              </div>
            </div>
          ))}
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
              <Tooltip
                contentStyle={{ background: '#fff', border: '1px solid #ccc' }}
                formatter={(value) => value.toFixed(1)}
              />
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
              <Radar
                name="Your Score"
                dataKey="score"
                stroke="#667eea"
                fill="#667eea"
                fillOpacity={0.6}
              />
              <Tooltip
                contentStyle={{ background: '#fff', border: '1px solid #ccc' }}
                formatter={(value) => value.toFixed(1)}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Question-wise Chart */}
      {questionScoresData.length > 0 && (
        <div className="chart-card full-width">
          <h3 className="chart-title">📊 Question-wise Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={questionScoresData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="question" />
              <YAxis domain={[0, 10]} />
              <Tooltip
                contentStyle={{ background: '#fff', border: '1px solid #ccc' }}
                formatter={(value) => value.toFixed(1)}
              />
              <Legend />
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
      )}

      {/* Strengths & Weaknesses */}
      <div className="insights-section">
        <div className="insight-card strengths">
          <h3 className="insight-title"><span className="insight-icon">✅</span> Key Strengths</h3>
          <ul className="insight-list">
            {(strengths.length > 0 ? strengths : [
              'Clear communication and articulation',
              'Good technical understanding',
              'Structured approach to problem-solving'
            ]).map((strength, idx) => <li key={idx}>{strength}</li>)}
          </ul>
        </div>

        <div className="insight-card weaknesses">
          <h3 className="insight-title"><span className="insight-icon">⚠️</span> Areas for Improvement</h3>
          <ul className="insight-list">
            {(weaknesses.length > 0 ? weaknesses : [
              'Add more real-world examples',
              'Reduce filler words (um, uh)',
              'Provide more detailed explanations'
            ]).map((weakness, idx) => <li key={idx}>{weakness}</li>)}
          </ul>
        </div>
      </div>

      {/* Recommendations */}
      <div className="recommendations-section">
        <h3 className="section-title"><span className="section-icon">💡</span> Personalized Recommendations</h3>
        <div className="recommendations-grid">
          {(recommendations.length > 0 ? recommendations : [
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
          ]).map((rec, idx) => (
            <div key={idx} className="recommendation-card">
              <div className="rec-icon">{rec.icon}</div>
              <div className="rec-content">
                <h4>{rec.title}</h4>
                <p>{rec.description}</p>
                {rec.link && <a href={rec.link} target="_blank" rel="noopener noreferrer" className="rec-link">Learn More →</a>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-section">
        <button className="primary-button" onClick={() => navigate('/mock-interview')}>
          <span className="button-icon">🔄</span> Take Another Interview
        </button>
        <button className="secondary-button" onClick={() => navigate('/interview-history')}>
          <span className="button-icon">📜</span> View History
        </button>
        <button className="download-button" onClick={() => window.print()}>
          <span className="button-icon">📥</span> Download Report
        </button>
      </div>
    </div>
  );
}

export default InterviewFeedback;
