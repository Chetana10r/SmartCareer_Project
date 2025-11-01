import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./Home.css";

const ParticleBackground = () => {
  return (
    <div className="particles-container">
      {[...Array(30)].map((_, i) => (
        <div
          key={i}
          className="particle"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 5}s`
          }}
        />
      ))}
    </div>
  );
};

function Home() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 15 - 7.5,
        y: (e.clientY / window.innerHeight) * 15 - 7.5
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const features = [
    {
      icon: "🧠",
      title: 'AI Career Analysis',
      description: 'Get intelligent career recommendations based on your skills and experience using machine learning.',
    },
    {
      icon: "📄",
      title: 'Resume Optimizer',
      description: 'Upload your resume and receive instant ATS score checking with optimization suggestions.',
    },
    {
      icon: "💼",
      title: 'Job Matching',
      description: 'Find relevant job opportunities that match your profile with real-time job market data.',
    },
    {
      icon: "🎓",
      title: 'Skill Development',
      description: 'Receive personalized course and certification recommendations for your career growth.',
    }
  ];

  return (
    <div className="home-wrapper">
      {/* Hero Section */}
      <section className="hero-section">
        <ParticleBackground />
        
        <div 
          className="gradient-orb orb-1" 
          style={{ 
            transform: `translate(${mousePosition.x * 0.3}px, ${mousePosition.y * 0.3}px)` 
          }}
        />
        <div 
          className="gradient-orb orb-2" 
          style={{ 
            transform: `translate(${-mousePosition.x * 0.2}px, ${-mousePosition.y * 0.2}px)` 
          }}
        />
        
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-icon">✓</span>
            <span>AI-Powered Career Platform</span>
          </div>
          
          <h1 className="hero-title">
            <span className="title-line">Transform Your Career Journey</span>
            <span className="title-line gradient-text">With Smart AI Technology</span>
          </h1>
          
          <p className="hero-description">
            Leverage cutting-edge artificial intelligence to analyze your resume, 
            discover optimal career paths, and access personalized job recommendations.
          </p>
          
          <div className="hero-buttons">
            <Link to="/domain-check" className="cta-btn primary">
              <span className="btn-icon">✨</span>
              <span>Analyze Resume</span>
            </Link>
            <Link to="/resume-optimizer" className="cta-btn secondary">
              <span className="btn-icon">📄</span>
              <span>Optimize Resume</span>
            </Link>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">AI-Powered</div>
              <div className="stat-label">Career Analysis</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">Real-Time</div>
              <div className="stat-label">Job Matching</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">Instant</div>
              <div className="stat-label">ATS Scoring</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <div className="section-badge">
            <span>💡</span>
            <span>Key Features</span>
          </div>
          <h2 className="section-title">Everything You Need to Succeed</h2>
          <p className="section-subtitle">
            Comprehensive tools designed to accelerate your career growth
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon-wrapper">
                <div className="feature-icon">
                  <span className="icon-emoji">{feature.icon}</span>
                </div>
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-header">
          <div className="section-badge">
            <span>⚡</span>
            <span>Simple Process</span>
          </div>
          <h2 className="section-title">How SmartCareer Works</h2>
          <p className="section-subtitle">Get started in three easy steps</p>
        </div>

        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3 className="step-title">Upload Resume</h3>
            <p className="step-description">
              Upload your existing resume in PDF format for instant AI analysis
            </p>
          </div>
          
          <div className="step-card">
            <div className="step-number">2</div>
            <h3 className="step-title">Get Insights</h3>
            <p className="step-description">
              Receive detailed analysis including domain detection and skill assessment
            </p>
          </div>
          
          <div className="step-card">
            <div className="step-number">3</div>
            <h3 className="step-title">Take Action</h3>
            <p className="step-description">
              Apply optimizations, find jobs, and enhance your professional profile
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <div className="cta-icon">🚀</div>
          <h2 className="cta-title">Ready to Advance Your Career?</h2>
          <p className="cta-description">
            Start using SmartCareer today and unlock personalized insights 
            to help you achieve your professional goals.
          </p>
          <Link to="/domain-check" className="cta-btn-large">
            <span>Get Started Now</span>
            <span className="btn-icon">→</span>
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;