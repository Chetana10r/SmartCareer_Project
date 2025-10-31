// src/components/MockTest/ResultPage.js
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './MockTest.css';

const ResultPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { result, subject } = location.state || {};

  const [showExplanations, setShowExplanations] = useState({});

  if (!result) {
    return (
      <div className="error-container">
        <h2>No result data available</h2>
        <button onClick={() => navigate('/mock-test')}>Go to Tests</button>
      </div>
    );
  }

  const { score, total, percentage, results, time_taken, passed } = result;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const toggleExplanation = (index) => {
    setShowExplanations(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const getScoreColor = () => {
    if (percentage >= 80) return '#4caf50';
    if (percentage >= 60) return '#ff9800';
    return '#f44336';
  };

  const getScoreMessage = () => {
    if (percentage >= 80) return 'Excellent! Outstanding performance! 🎉';
    if (percentage >= 60) return 'Good job! You passed the test! 👍';
    if (percentage >= 40) return 'Not bad! Keep practicing! 💪';
    return 'Keep learning! Practice more! 📚';
  };

  return (
    <div className="result-container">
      <div className="result-header">
        <div className="result-badge" style={{ borderColor: getScoreColor() }}>
          <div style={{ fontSize: '3rem', color: getScoreColor() }}>🏆</div>
          <h1 style={{ color: getScoreColor() }}>{percentage}%</h1>
          <p>{passed ? 'PASSED' : 'NEEDS IMPROVEMENT'}</p>
        </div>

        <div className="result-summary">
          <h2>{subject} Test Results</h2>
          <p className="result-message">{getScoreMessage()}</p>
          
          <div className="result-stats">
            <div className="stat-item">
              <span className="stat-label">Score</span>
              <span className="stat-value">{score}/{total}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Correct</span>
              <span className="stat-value correct">{score}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Incorrect</span>
              <span className="stat-value incorrect">{total - score}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Time Taken</span>
              <span className="stat-value">{formatTime(time_taken)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="result-actions">
        <button 
          className="action-btn retake-btn"
          onClick={() => navigate('/mock-test/quiz', { state: { subject } })}
        >
          🔄 Retake Test
        </button>
        <button 
          className="action-btn home-btn"
          onClick={() => navigate('/mock-test')}
        >
          🏠 Choose Another Subject
        </button>
        <button 
          className="action-btn history-btn"
          onClick={() => navigate('/mock-test/history')}
        >
          📊 View History
        </button>
      </div>

      <div className="answers-review">
        <h3>Detailed Review</h3>
        
        {results.map((item, index) => (
          <div 
            key={item.question_id} 
            className={`review-card ${item.is_correct ? 'correct' : 'incorrect'}`}
          >
            <div className="review-header">
              <div className="question-number">
                {item.is_correct ? '✅' : '❌'}
                <span>Question {index + 1}</span>
              </div>
              <button 
                className="explanation-toggle"
                onClick={() => toggleExplanation(index)}
              >
                {showExplanations[index] ? '▼' : '▶'} Explanation
              </button>
            </div>

            <div className="question-text">{item.question}</div>

            <div className="options-review">
              {Object.entries(item.options).map(([key, value]) => {
                const isUserAnswer = key === item.user_answer;
                const isCorrectAnswer = key === item.correct_answer;
                
                let className = 'option-review';
                if (isCorrectAnswer) className += ' correct-option';
                if (isUserAnswer && !item.is_correct) className += ' wrong-option';
                
                return (
                  <div key={key} className={className}>
                    <span className="option-key">{key}</span>
                    <span className="option-value">{value}</span>
                    {isCorrectAnswer && <span className="badge correct-badge">✓ Correct</span>}
                    {isUserAnswer && !item.is_correct && <span className="badge wrong-badge">Your Answer</span>}
                  </div>
                );
              })}
            </div>

            {showExplanations[index] && (
              <div className="explanation-box">
                <strong>💡 Explanation:</strong>
                <p>{item.explanation}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="performance-tips">
        <h3>📈 Performance Tips</h3>
        <div className="tips-grid">
          <div className="tip-card">
            <h4>Strengths</h4>
            <p>You correctly answered {score} out of {total} questions</p>
          </div>
          <div className="tip-card">
            <h4>Improvement Areas</h4>
            <p>Review the {total - score} incorrect answers above</p>
          </div>
          <div className="tip-card">
            <h4>Next Steps</h4>
            <p>{percentage >= 60 ? 'Try a different subject!' : 'Practice more and retake this test'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultPage;