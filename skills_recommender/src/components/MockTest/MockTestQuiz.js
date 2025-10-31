import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Time from './Time';
import './MockTest.css';

const MockTestQuiz = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { subject } = location.state || {};

  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLimit, setTimeLimit] = useState(600); // 10 minutes
  const [loading, setLoading] = useState(true);
  const [showReview, setShowReview] = useState(false);

  // Load questions
  useEffect(() => {
    if (!subject) {
      navigate('/mock-test');
      return;
    }
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/get_questions', {
        subject
      });

      if (response.data.error) throw new Error(response.data.error);

      setQuestions(response.data.questions);
      setTimeLimit(response.data.time_limit || 600);
    } catch (error) {
      console.error('Error fetching questions:', error);
      alert('Failed to load questions. Please try again.');
      navigate('/mock-test');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, option) => {
    // Ensure consistent string key usage
    setAnswers(prev => ({
      ...prev,
      [String(questionId)]: option
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    const confirmedSubmit = window.confirm(
      `You have answered ${Object.keys(answers).length} out of ${questions.length} questions. Submit test?`
    );
    if (!confirmedSubmit) return;

    const timeTaken = 600 - timeLimit;

    try {
      const response = await axios.post('http://localhost:5000/api/submit_test', {
        user_id: localStorage.getItem('user_id') || 'guest',
        subject,
        answers,
        time_taken: timeTaken
      });

      if (response.data.error) throw new Error(response.data.error);

      navigate('/mock-test/result', {
        state: {
          result: response.data,
          subject
        }
      });
    } catch (error) {
      console.error('Error submitting test:', error);
      alert('Failed to submit test. Please try again.');
    }
  };

  const handleTimeUp = () => {
    alert('⏰ Time is up! Submitting your test...');
    handleSubmit();
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading questions...</p>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="error-container">
        <h2>No questions available for {subject}</h2>
        <button onClick={() => navigate('/mock-test')}>Go Back</button>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const isAnswered = answers[String(currentQ.id)];

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <div className="quiz-info">
          <h2>{subject} Test</h2>
          <span className="question-counter">
            Question {currentQuestion + 1} of {questions.length}
          </span>
        </div>
        <Time
          timeLimit={timeLimit}
          onTimeUp={handleTimeUp}
          setTimeLimit={setTimeLimit}
        />
      </div>

      <div className="question-card">
        <div className="question-header">
          {currentQ.difficulty && (
            <span className="difficulty-badge">{currentQ.difficulty}</span>
          )}
          <h3>
            Q{currentQuestion + 1}. {currentQ.question}
          </h3>
        </div>

        <div className="options-container">
          {currentQ.options &&
            Object.entries(currentQ.options).map(([key, value]) => (
              <div
                key={key}
                className={`option ${
                  answers[String(currentQ.id)] === key ? 'selected' : ''
                }`}
                onClick={() => handleAnswerSelect(currentQ.id, key)}
              >
                <div className="option-label">{key}</div>
                <div className="option-text">{value}</div>
              </div>
            ))}
        </div>
      </div>

      <div className="navigation-buttons">
        <button
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
          className="nav-btn prev-btn"
        >
          ← Previous
        </button>

        <button onClick={() => setShowReview(true)} className="nav-btn review-btn">
          Review Answers
        </button>

        {currentQuestion === questions.length - 1 ? (
          <button onClick={handleSubmit} className="nav-btn submit-btn">
            Submit Test
          </button>
        ) : (
          <button onClick={handleNext} className="nav-btn next-btn">
            Next →
          </button>
        )}
      </div>

      <div className="question-navigator">
        {questions.map((q, index) => (
          <div
            key={q.id}
            className={`nav-circle ${
              answers[String(q.id)] ? 'answered' : ''
            } ${index === currentQuestion ? 'active' : ''}`}
            onClick={() => setCurrentQuestion(index)}
          >
            {index + 1}
          </div>
        ))}
      </div>

      {showReview && (
        <div className="review-modal">
          <div className="review-content">
            <h3>Answer Review</h3>
            <div className="review-summary">
              <p>Answered: {Object.keys(answers).length}/{questions.length}</p>
              <p>Unanswered: {questions.length - Object.keys(answers).length}</p>
            </div>
            <div className="review-grid">
              {questions.map((q, index) => (
                <div
                  key={q.id}
                  className={`review-item ${
                    answers[String(q.id)] ? 'answered' : 'unanswered'
                  }`}
                  onClick={() => {
                    setCurrentQuestion(index);
                    setShowReview(false);
                  }}
                >
                  <span>Q{index + 1}</span>
                  {answers[String(q.id)] && (
                    <span className="answer-badge">{answers[String(q.id)]}</span>
                  )}
                </div>
              ))}
            </div>
            <button onClick={() => setShowReview(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MockTestQuiz;
