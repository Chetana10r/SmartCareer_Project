import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { FaRocket, FaBars, FaTimes } from "react-icons/fa";
import "./Navbar.css";

function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <FaRocket className="brand-icon" />
          <span className="brand-text">SmartCareer</span>
          <div className="brand-glow"></div>
        </Link>

        <ul className={`navbar-links ${isMobileMenuOpen ? 'mobile-active' : ''}`}>
          <li><Link to="/" onClick={() => setIsMobileMenuOpen(false)}>Home</Link></li>
          <li><Link to="/about" onClick={() => setIsMobileMenuOpen(false)}>About</Link></li>
          <li><Link to="/testimonials" onClick={() => setIsMobileMenuOpen(false)}>Testimonials</Link></li>
          <li><Link to="/contact" onClick={() => setIsMobileMenuOpen(false)}>Contact</Link></li>
          <li><Link to="/mock-interview" onClick={() => setIsMobileMenuOpen(false)}>Mock Interview</Link></li>
          <li><Link to="/mock-test" onClick={() => setIsMobileMenuOpen(false)}>Mock Test</Link></li>
        </ul>

        <div className="navbar-actions">
          <Link to="/login" className="login-btn">
            <span>Login</span>
            <div className="btn-shine"></div>
          </Link>
          <button 
            className="mobile-menu-btn" 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <FaTimes /> : <FaBars />}
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;