import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './RecruiterNavbar.css';

function RecruiterNavbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path) => {
    return location.pathname === path;
  };

  const handleLogout = () => {
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
    navigate('/role-selection');
  };

  return (
    <nav className="recruiter-navbar">
      <div className="navbar-container">
        {/* Logo/Brand */}
        <div className="navbar-brand">
          <Link to="/recruiter-dashboard" className="brand-link">
            <span className="brand-icon">💼</span>
            <span className="brand-text">SmartCareer</span>
            <span className="brand-badge">Recruiter</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <div className="navbar-menu">
          <Link 
            to="/recruiter-dashboard" 
            className={`nav-link ${isActive('/recruiter-dashboard') ? 'active' : ''}`}
          >
            <span className="nav-icon">🏠</span>
            <span>Dashboard</span>
          </Link>

          <Link 
            to="/post-job" 
            className={`nav-link ${isActive('/post-job') ? 'active' : ''}`}
          >
            <span className="nav-icon">➕</span>
            <span>Post Job</span>
          </Link>

          <Link 
            to="/job-listings" 
            className={`nav-link ${isActive('/job-listings') ? 'active' : ''}`}
          >
            <span className="nav-icon">📊</span>
            <span>All Jobs</span>
          </Link>

          <Link 
            to="/search-candidates" 
            className={`nav-link ${isActive('/search-candidates') ? 'active' : ''}`}
          >
            <span className="nav-icon">🔍</span>
            <span>Search</span>
          </Link>

          <Link 
            to="/resume-matching" 
            className={`nav-link ${isActive('/resume-matching') ? 'active' : ''}`}
          >
            <span className="nav-icon">🎯</span>
            <span>Match</span>
          </Link>

          <Link 
            to="/shortlist-manager" 
            className={`nav-link ${isActive('/shortlist-manager') ? 'active' : ''}`}
          >
            <span className="nav-icon">⭐</span>
            <span>Shortlist</span>
          </Link>
        </div>

        {/* Right Side Actions */}
        <div className="navbar-actions">
          <button className="notification-btn" title="Notifications">
            <span className="notification-icon">🔔</span>
            <span className="notification-badge">3</span>
          </button>

          <div className="user-menu">
            <button className="user-btn">
              <span className="user-avatar">👤</span>
              <span className="user-name">Recruiter</span>
            </button>
            <div className="user-dropdown">
              <Link to="/profile" className="dropdown-item">
                <span>👤</span> Profile
              </Link>
              <Link to="/settings" className="dropdown-item">
                <span>⚙️</span> Settings
              </Link>
              <button onClick={handleLogout} className="dropdown-item logout">
                <span>🚪</span> Logout
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          <span className="hamburger">☰</span>
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="mobile-menu">
          <Link 
            to="/recruiter-dashboard" 
            className={`mobile-nav-link ${isActive('/recruiter-dashboard') ? 'active' : ''}`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <span className="nav-icon">🏠</span>
            <span>Dashboard</span>
          </Link>

          <Link 
            to="/post-job" 
            className={`mobile-nav-link ${isActive('/post-job') ? 'active' : ''}`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <span className="nav-icon">➕</span>
            <span>Post Job</span>
          </Link>

          <Link 
            to="/job-listings" 
            className={`mobile-nav-link ${isActive('/job-listings') ? 'active' : ''}`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <span className="nav-icon">📊</span>
            <span>All Jobs</span>
          </Link>

          <Link 
            to="/search-candidates" 
            className={`mobile-nav-link ${isActive('/search-candidates') ? 'active' : ''}`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <span className="nav-icon">🔍</span>
            <span>Search Candidates</span>
          </Link>

          <Link 
            to="/resume-matching" 
            className={`mobile-nav-link ${isActive('/resume-matching') ? 'active' : ''}`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <span className="nav-icon">🎯</span>
            <span>Resume Matching</span>
          </Link>

          <Link 
            to="/shortlist-manager" 
            className={`mobile-nav-link ${isActive('/shortlist-manager') ? 'active' : ''}`}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <span className="nav-icon">⭐</span>
            <span>Shortlist Manager</span>
          </Link>

          <button 
            onClick={handleLogout} 
            className="mobile-nav-link logout"
          >
            <span className="nav-icon">🚪</span>
            <span>Logout</span>
          </button>
        </div>
      )}
    </nav>
  );
}

export default RecruiterNavbar;