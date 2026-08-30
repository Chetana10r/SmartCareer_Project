import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  const tools = [
    { icon: "📄", label: "Analyze Resume",   desc: "AI domain & skill detection",    to: "/domain-check",      color: "#3b82f6" },
    { icon: "✨", label: "Optimize Resume",   desc: "ATS scoring & improvements",     to: "/resume-optimizer",  color: "#8b5cf6" },
    { icon: "🎤", label: "Mock Interview",    desc: "AI-powered practice sessions",   to: "/mock-interview",    color: "#10b981" },
    { icon: "📝", label: "Mock Test",         desc: "Subject-wise quiz assessment",   to: "/mock-test",         color: "#f59e0b" },
    { icon: "💼", label: "Job Openings",      desc: "Live matched job listings",      to: "/domain-check",      color: "#ef4444" },
    { icon: "🎓", label: "Courses & Certs",   desc: "Personalized learning paths",    to: "/domain-check",      color: "#06b6d4" },
  ];

  const stats = [
    { value: "10K+", label: "Resumes Analyzed" },
    { value: "95%",  label: "Accuracy Rate" },
    { value: "500+", label: "Job Matches Daily" },
    { value: "Free", label: "Always" },
  ];

  return (
    <div className="home-dashboard">
      {/* Left Sidebar */}
      <aside className="home-sidebar">
        <div className="sidebar-brand">
          <span className="brand-logo">⚡</span>
          <span className="brand-name">SmartCareer</span>
        </div>

        <div className="sidebar-hero">
          <h1 className="sidebar-headline">Accelerate Your Career with AI</h1>
          <p className="sidebar-sub">
            Upload your resume and get instant AI-powered career analysis, skill predictions, and job recommendations.
          </p>
          <Link to="/domain-check" className="sidebar-cta">
            🚀 Get Started Free
          </Link>
        </div>

        <div className="sidebar-stats">
          {stats.map((s, i) => (
            <div key={i} className="sidebar-stat">
              <div className="stat-val">{s.value}</div>
              <div className="stat-lbl">{s.label}</div>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <Link to="/role-selection" className="recruiter-link">🏢 Recruiter Portal →</Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="home-main">
        <div className="home-topbar">
          <div>
            <h2 className="topbar-title">Career Dashboard</h2>
            <p className="topbar-sub">Choose a tool to get started</p>
          </div>
          <div className="topbar-actions">
            <Link to="/mock-interview" className="topbar-btn outline">🎤 Practice Interview</Link>
            <Link to="/domain-check"   className="topbar-btn primary">📄 Analyze Resume</Link>
          </div>
        </div>

        <div className="tools-grid">
          {tools.map((tool, i) => (
            <Link key={i} to={tool.to} className="tool-card" style={{ "--card-color": tool.color }}>
              <div className="tool-icon-wrap">
                <span className="tool-icon">{tool.icon}</span>
              </div>
              <div className="tool-info">
                <div className="tool-label">{tool.label}</div>
                <div className="tool-desc">{tool.desc}</div>
              </div>
              <span className="tool-arrow">→</span>
            </Link>
          ))}
        </div>

        <div className="how-section">
          <h3 className="how-title">How It Works</h3>
          <div className="how-steps">
            {[
              { num: "1", step: "Upload Resume",  detail: "PDF format supported" },
              { num: "2", step: "AI Analysis",    detail: "Domain & skill detection" },
              { num: "3", step: "Get Insights",   detail: "Role & course suggestions" },
              { num: "4", step: "Apply & Grow",   detail: "Jobs & certifications" },
            ].map((s, i, arr) => (
              <React.Fragment key={i}>
                <div className="how-step">
                  <div className="how-num">{s.num}</div>
                  <div className="how-info">
                    <div className="how-step-title">{s.step}</div>
                    <div className="how-step-detail">{s.detail}</div>
                  </div>
                </div>
                {i < arr.length - 1 && <div className="how-connector" />}
              </React.Fragment>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default Home;
