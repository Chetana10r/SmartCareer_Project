
// ============================================
// Home.js - Advanced Animated Version
// ============================================

import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  FaRocket, FaMagic, FaFileAlt, FaStar, 
  FaBrain, FaChartLine, FaGraduationCap, 
  FaCheckCircle, FaArrowRight 
} from "react-icons/fa";
import "./Home.css";

// Floating Particles Component
const ParticleBackground = () => {
  return (
    <div className="particles-container">
      {[...Array(60)].map((_, i) => (
        <div
          key={i}
          className="particle"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${4 + Math.random() * 6}s`,
            width: `${2 + Math.random() * 4}px`,
            height: `${2 + Math.random() * 4}px`
          }}
        />
      ))}
    </div>
  );
};

function Home() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 30 - 15,
        y: (e.clientY / window.innerHeight) * 30 - 15
      });
    };

    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const features = [
    {
      icon: <FaBrain />,
      title: 'AI Career Analysis',
      description: 'Advanced machine learning algorithms analyze your skills and suggest optimal career paths tailored to your profile.',
      color: '#00e0ff',
      delay: '0s'
    },
    {
      icon: <FaFileAlt />,
      title: 'Resume Optimization',
      description: 'Transform your resume with AI-powered insights. Get real-time suggestions to make your application stand out.',
      color: '#ff6b6b',
      delay: '0.1s'
    },
    {
      icon: <FaChartLine />,
      title: 'Growth Tracking',
      description: 'Monitor your progress with detailed analytics and personalized recommendations for continuous improvement.',
      color: '#ffd93d',
      delay: '0.2s'
    },
    {
      icon: <FaGraduationCap />,
      title: 'Learning Paths',
      description: 'Access curated learning resources designed to help you master in-demand skills in your field.',
      color: '#6bcf7f',
      delay: '0.3s'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Software Engineer',
      company: 'Tech Corp',
      text: 'SmartCareer helped me identify my strengths and land my dream job. The AI insights were incredibly accurate!',
      rating: 5,
      avatar: 'S'
    },
    {
      name: 'Michael Chen',
      role: 'Product Manager',
      company: 'StartUp Inc',
      text: 'The resume optimizer transformed my CV. I got 3x more interview calls within a week of using it.',
      rating: 5,
      avatar: 'M'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Data Scientist',
      company: 'AI Solutions',
      text: 'Best career platform I\'ve used. The personalized learning paths accelerated my skill development tremendously.',
      rating: 5,
      avatar: 'E'
    }
  ];

  return (
    <div className="home-wrapper">
      {/* Hero Section */}
      <section className="hero-section">
        <ParticleBackground />
        
        {/* Animated Gradient Orbs */}
        <div 
          className="gradient-orb orb-1" 
          style={{ 
            transform: `translate(${mousePosition.x * 0.5}px, ${mousePosition.y * 0.5}px)` 
          }}
        />
        <div 
          className="gradient-orb orb-2" 
          style={{ 
            transform: `translate(${-mousePosition.x * 0.3}px, ${-mousePosition.y * 0.3}px)` 
          }}
        />
        <div 
          className="gradient-orb orb-3" 
          style={{ 
            transform: `translate(${mousePosition.x * 0.4}px, ${-mousePosition.y * 0.4}px)` 
          }}
        />
        
        <div className="hero-content">
          {/* Badge */}
          <div className="hero-badge">
            <FaStar className="badge-icon" />
            <span>AI-Powered Career Platform</span>
            <div className="badge-pulse"></div>
          </div>
          
          {/* Main Title */}
          <h1 className="hero-title">
            <span className="title-line">Transform Your Career</span>
            <span className="title-line gradient-text">With AI Intelligence</span>
          </h1>
          
          {/* Description */}
          <p className="hero-description">
            Discover your perfect career path with cutting-edge AI technology.
            Get personalized insights, optimize your resume, and unlock your full potential.
          </p>
          
          {/* CTA Buttons */}
          <div className="hero-buttons">
            <Link to="/domain-check" className="cta-btn primary">
              <FaMagic className="btn-icon" />
              <span>Start Your Journey</span>
              <div className="btn-glow"></div>
            </Link>
            <Link to="/resume-optimizer" className="cta-btn secondary">
              <FaFileAlt className="btn-icon" />
              <span>Resume Optimizer</span>
              <div className="btn-glow"></div>
            </Link>
          </div>

          {/* Stats Counter */}
          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">50K+</div>
              <div className="stat-label">Career Paths Analyzed</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">95%</div>
              <div className="stat-label">Success Rate</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">24/7</div>
              <div className="stat-label">AI Support</div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="scroll-indicator">
          <div className="mouse-wrapper">
            <div className="mouse">
              <div className="wheel"></div>
            </div>
          </div>
          <span className="scroll-text">Scroll to explore</span>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <div className="section-badge">
            <FaCheckCircle />
            <span>Features</span>
          </div>
          <h2 className="section-title">Powerful Tools for Your Success</h2>
          <p className="section-subtitle">Everything you need to accelerate your career growth</p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="feature-card"
              style={{ 
                '--accent-color': feature.color,
                '--animation-delay': feature.delay
              }}
            >
              <div className="feature-icon-wrapper">
                <div className="feature-icon">{feature.icon}</div>
                <div className="feature-icon-bg"></div>
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <button className="feature-btn">
                <span>Learn More</span>
                <FaArrowRight className="btn-arrow" />
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="section-header">
          <div className="section-badge">
            <FaStar />
            <span>Testimonials</span>
          </div>
          <h2 className="section-title">Loved by Professionals Worldwide</h2>
          <p className="section-subtitle">Join thousands of satisfied users who transformed their careers</p>
        </div>

        <div className="testimonials-grid">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="testimonial-card">
              <div className="testimonial-header">
                <div className="testimonial-stars">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <FaStar key={i} className="star-icon" />
                  ))}
                </div>
                <div className="quote-icon">"</div>
              </div>
              
              <p className="testimonial-text">{testimonial.text}</p>
              
              <div className="testimonial-author">
                <div className="author-avatar">
                  <span>{testimonial.avatar}</span>
                  <div className="avatar-ring"></div>
                </div>
                <div className="author-info">
                  <div className="author-name">{testimonial.name}</div>
                  <div className="author-role">{testimonial.role} at {testimonial.company}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <div className="cta-icon">
            <FaRocket />
          </div>
          <h2 className="cta-title">Ready to Transform Your Career?</h2>
          <p className="cta-description">Join thousands of professionals who are already using SmartCareer to achieve their dreams</p>
          <Link to="/domain-check" className="cta-btn-large">
            <span>Get Started Now</span>
            <FaArrowRight className="btn-icon" />
            <div className="btn-glow"></div>
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;