// App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes, NavLink } from 'react-router-dom';
import SkillPredictor from './components/SkillPredictor';
import JobRoleRecommender from './components/JobRoleRecommender';
import CourseCertRecommender from './components/CourseCertRecommender';
import './App.css';

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-200 text-gray-800">
        <header className="shadow p-4 bg-white flex justify-between items-center">
          <h1 className="text-2xl font-bold">Resume Recommender</h1>
          <nav className="space-x-4">
            <NavLink to="/skills" className={({ isActive }) => isActive ? 'text-blue-600 font-semibold' : ''}>Skills</NavLink>
            <NavLink to="/roles" className={({ isActive }) => isActive ? 'text-blue-600 font-semibold' : ''}>Job Roles</NavLink>
            <NavLink to="/courses" className={({ isActive }) => isActive ? 'text-blue-600 font-semibold' : ''}>Courses</NavLink>
          </nav>
        </header>
        <main className="p-6">
          <Routes>
            <Route path="/skills" element={<SkillPredictor />} />
            <Route path="/roles" element={<JobRoleRecommender />} />
            <Route path="/courses" element={<CourseCertRecommender />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
