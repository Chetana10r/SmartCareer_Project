import React, { useState } from 'react';
import axios from 'axios';

const CourseCertRecommender = () => {
  const [resumeText, setResumeText] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [loading, setLoading] = useState(false);
  const [isIT, setIsIT] = useState(true);

  const handleToggle = () => {
    setIsIT(prev => !prev);
    setRecommendation('');
  };

  const handleRecommend = async () => {
    if (!resumeText) return;
    setLoading(true);
    try {
      const endpoint = isIT ? '/recommend_courses_cert_it' : '/recommend_courses_cert_nonit';
      const res = await axios.post(endpoint, { resume: resumeText });
      setRecommendation(res.data.recommendation);
    } catch (err) {
      setRecommendation("Error fetching recommendations.");
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: '700px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '10px' }}>
      <h2>Course + Certification Recommender</h2>

      <button onClick={handleToggle} style={{ margin: '10px 0', padding: '5px 10px' }}>
        Switch to {isIT ? 'Non-IT' : 'IT'}
      </button>

      <textarea
        rows="6"
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
        placeholder="Paste your resume or skills here..."
        style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
      />

      <button onClick={handleRecommend} disabled={loading} style={{ padding: '8px 12px' }}>
        {loading ? 'Loading...' : 'Get Recommendations'}
      </button>

      {recommendation && (
        <div style={{ marginTop: '20px', background: '#e6ffe6', padding: '10px', borderRadius: '8px' }}>
          <strong>Recommended Courses & Certifications:</strong>
          <p>{recommendation}</p>
        </div>
      )}
    </div>
  );
};

export default CourseCertRecommender;
