import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // You can use global styles here or import from ResumeRecommender.css if preferred.
import ResumeRecommender from './ResumeRecommender';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ResumeRecommender />
  </React.StrictMode>
);
