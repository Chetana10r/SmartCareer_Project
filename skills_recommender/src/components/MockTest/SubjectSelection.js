import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './MockTest.css';
import { 
  FaPython, FaDatabase, FaBrain, FaChartLine, 
  FaFileExcel, FaCalculator, FaCode 
} from 'react-icons/fa';

const SubjectSelection = () => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const subjectIcons = {
    'Python': <FaPython />,
    'SQL': <FaDatabase />,
    'Machine Learning': <FaBrain />,
    'Deep Learning': <FaChartLine />,
    'Excel': <FaFileExcel />,
    'Aptitude': <FaCalculator />,
    'JavaScript': <FaCode />
  };

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/get_subjects');
      setSubjects(response.data.subjects || []);
    } catch (error) {
      console.error('Error fetching subjects:', error);
      alert('Failed to load subjects.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartTest = () => {
    if (!selectedSubject) {
      alert('Please select a subject first!');
      return;
    }
    if (!selectedDifficulty) {
      alert('Please select difficulty level!');
      return;
    }

    navigate('/mock-test/quiz', {
      state: { subject: selectedSubject, difficulty: selectedDifficulty },
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading subjects...</p>
      </div>
    );
  }

  return (
    <div className="subject-selection-container">
      <div className="subject-header">
        <h1>🎯 Choose Your Test Subject</h1>
        <p>Select a subject and difficulty to begin your mock test</p>
      </div>

      {/* SUBJECT SELECTION */}
      <h3 className="subtitle">Select Subject</h3>
      <div className="subjects-grid">
        {subjects.map((subject, index) => (
          <div
            key={index}
            className={`subject-card ${selectedSubject === subject ? 'selected' : ''}`}
            onClick={() => setSelectedSubject(subject)}
          >
            <div className="subject-icon">
              {subjectIcons[subject] || <FaCode />}
            </div>
            <h3>{subject}</h3>
            <div className="subject-info">
              <span>⏱️ 10 minutes</span>
              <span>📝 10 questions</span>
            </div>
          </div>
        ))}
      </div>

      {/* DIFFICULTY SELECTION */}
      {selectedSubject && (
        <>
          <h3 className="subtitle">Select Difficulty Level</h3>
          <div className="difficulty-buttons">
            {['Easy', 'Medium', 'Hard'].map((level) => (
              <button
                key={level}
                className={`difficulty-btn ${selectedDifficulty === level ? 'active' : ''}`}
                onClick={() => setSelectedDifficulty(level)}
              >
                {level}
              </button>
            ))}
          </div>
        </>
      )}

      {/* Start Test Button */}
      <div className="start-section">
        {selectedSubject && selectedDifficulty && (
          <div className="selection-preview">
            🧩 You selected: <b>{selectedSubject}</b> ({selectedDifficulty} Level)
          </div>
        )}

        <button className="start-btn" onClick={handleStartTest}>
          🚀 Start Test
        </button>
      </div>

      {/* Test Instructions */}
      <div className="test-instructions">
        <h3>📋 Test Instructions</h3>
        <ul>
          <li>✅ 10 questions in 10 minutes</li>
          <li>✅ 1 correct answer per question</li>
          <li>✅ You can review before submitting</li>
          <li>✅ Results shown immediately after test</li>
        </ul>
      </div>
    </div>
  );
};

export default SubjectSelection;
