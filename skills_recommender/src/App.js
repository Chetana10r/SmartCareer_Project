// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate, useParams } from "react-router-dom";

import Navbar           from "./components/Navbar";
import Home             from "./components/Home";
import DomainCheck      from "./components/DomainCheck";
import SkillPrediction  from "./components/SkillPrediction";
import PredictionResult from "./components/PredictionResult";
import About            from "./components/About";
import Footer           from "./components/Footer";
import Testimonials     from "./components/Testimonials";
import Contact          from "./components/Contact";
import ResumeOptimizer  from "./components/ResumeOptimizer";

import InterviewSetup    from "./components/MockInterview/InterviewSetup";
import InterviewSession  from "./components/MockInterview/InterviewSession";
import InterviewFeedback from "./components/MockInterview/InterviewFeedback";
import InterviewHistory  from "./components/MockInterview/InterviewHistory";

import SubjectSelection from "./components/MockTest/SubjectSelection";
import MockTestQuiz     from "./components/MockTest/MockTestQuiz";
import ResultPage       from "./components/MockTest/ResultPage";
import TestHistory      from "./components/MockTest/TestHistory";

import RoleSelection      from "./components/Auth/RoleSelection";
import Login              from "./components/Auth/Login";
import RecruiterNavbar    from "./components/Recruiter/RecruiterNavbar";
import RecruiterDashboard from "./components/Recruiter/RecruiterDashboard";
import JobPosting         from "./components/Recruiter/JobPosting";
import JobListings        from "./components/Recruiter/JobListings";
import CandidateSearch    from "./components/Recruiter/CandidateSearch";
import ResumeMatching     from "./components/Recruiter/ResumeMatching";
import ShortlistManager   from "./components/Recruiter/ShortlistManager";

import "./App.css";

// ── Inline Job Detail page (no separate file needed) ──────────────────────
function JobDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetch("http://127.0.0.1:5000/get_recruiter_jobs", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recruiter_id: "recruiter_1" })
    })
      .then(r => r.json())
      .then(d => { setJob((d.jobs || []).find(j => String(j.id) === String(id)) || null); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  const s = { page: { minHeight: "calc(100vh - 65px)", background: "#f1f5f9", padding: "2rem", fontFamily: "Segoe UI,system-ui,sans-serif" }, card: { background: "white", borderRadius: 16, padding: "2rem", maxWidth: 860, margin: "0 auto", boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }, back: { background: "white", border: "2px solid #3498db", color: "#3498db", padding: "0.6rem 1.2rem", borderRadius: 8, cursor: "pointer", fontWeight: 600, marginBottom: "1.5rem" }, tag: { display: "inline-block", background: "#ebf5fb", color: "#2980b9", padding: "0.3rem 0.8rem", borderRadius: 20, fontSize: "0.82rem", fontWeight: 600, margin: "0.25rem" } };

  if (loading) return <div style={{ ...s.page, display: "flex", alignItems: "center", justifyContent: "center" }}><p>Loading...</p></div>;
  if (!job)    return <div style={{ ...s.page, display: "flex", alignItems: "center", justifyContent: "center" }}><div style={s.card}><h2>Job not found</h2><button style={s.back} onClick={() => navigate("/recruiter-dashboard")}>← Back</button></div></div>;

  return (
    <div style={s.page}>
      <div style={s.card}>
        <button style={s.back} onClick={() => navigate("/recruiter-dashboard")}>← Back to Dashboard</button>
        <h1 style={{ color: "#2c3e50", marginBottom: "0.3rem" }}>{job.title}</h1>
        <p style={{ color: "#7f8c8d", marginBottom: "1.5rem" }}>{job.company} · {job.location}</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(180px,1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
          {[["💼 Type", job.type], ["📊 Level", job.experience], ["💰 Salary", "₹" + job.salary], ["📬 Applications", job.applications], ["📅 Posted", job.postedDate], ["⏰ Deadline", job.deadline]].map(([k, v]) => (
            <div key={k} style={{ background: "#f8f9fa", borderRadius: 10, padding: "0.8rem" }}>
              <div style={{ fontSize: "0.72rem", color: "#95a5a6", textTransform: "uppercase" }}>{k}</div>
              <div style={{ fontWeight: 700, color: "#2c3e50", marginTop: "0.2rem" }}>{v}</div>
            </div>
          ))}
        </div>
        <h3 style={{ marginBottom: "0.5rem" }}>🎯 Required Skills</h3>
        <div style={{ marginBottom: "1.5rem" }}>{(job.skills || []).map((sk, i) => <span key={i} style={s.tag}>{sk}</span>)}</div>
        <h3 style={{ marginBottom: "0.5rem" }}>📄 Description</h3>
        <p style={{ color: "#555", lineHeight: 1.7, marginBottom: "1.5rem" }}>{job.description}</p>
        <h3 style={{ marginBottom: "0.5rem" }}>📌 Requirements</h3>
        {(job.requirements || "").split("\n").filter(r => r.trim()).map((r, i) => (
          <div key={i} style={{ display: "flex", gap: "0.6rem", marginBottom: "0.4rem" }}>
            <span style={{ color: "#27ae60", fontWeight: 700 }}>✓</span>
            <span style={{ color: "#555" }}>{r.replace(/^[-•]\s*/, "")}</span>
          </div>
        ))}
        <div style={{ marginTop: "2rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <button style={{ ...s.back, background: "#3498db", color: "white" }} onClick={() => navigate("/search-candidates")}>🔍 Search Candidates</button>
          <button style={s.back} onClick={() => navigate("/job-listings")}>📊 All Jobs</button>
        </div>
      </div>
    </div>
  );
}

// ── Inline Analytics page ─────────────────────────────────────────────────
function AnalyticsPage() {
  const navigate = useNavigate();
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetch("http://127.0.0.1:5000/get_analytics").then(r => r.json()).then(setData).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const s = { page: { minHeight: "calc(100vh - 65px)", background: "#f1f5f9", padding: "2rem", fontFamily: "Segoe UI,system-ui,sans-serif" }, back: { background: "white", border: "2px solid #3498db", color: "#3498db", padding: "0.6rem 1.2rem", borderRadius: 8, cursor: "pointer", fontWeight: 600 }, kpiGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(160px,1fr))", gap: "1rem", margin: "1.5rem 0" }, kpi: (color) => ({ background: "white", borderRadius: 14, padding: "1.2rem", textAlign: "center", borderTop: `4px solid ${color}`, boxShadow: "0 4px 16px rgba(0,0,0,0.07)" }), section: { background: "white", borderRadius: 14, padding: "1.5rem", marginBottom: "1rem", boxShadow: "0 4px 16px rgba(0,0,0,0.07)" } };

  const kpis = data ? [
    ["📋", "Total Jobs",        data.overview.total_jobs,         "#3498db"],
    ["✅", "Active Jobs",       data.overview.active_jobs,        "#2ecc71"],
    ["📬", "Total Applications",data.overview.total_applications, "#e74c3c"],
    ["⭐", "Shortlisted",       data.overview.total_shortlisted,  "#f39c12"],
    ["🎯", "Interviewed",       data.overview.total_interviewed,  "#9b59b6"],
    ["🏆", "Hired",             data.overview.total_hired,        "#1abc9c"],
    ["📊", "Avg Apps/Job",      data.overview.avg_applications_per_job, "#e67e22"],
    ["💡", "Hire Rate",         data.overview.hire_rate + "%",    "#34495e"],
  ] : [];

  if (loading) return <div style={{ ...s.page, display: "flex", alignItems: "center", justifyContent: "center" }}><p>Loading analytics...</p></div>;

  return (
    <div style={s.page}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <button style={{ ...s.back, marginBottom: "1.5rem" }} onClick={() => navigate("/recruiter-dashboard")}>← Back to Dashboard</button>
        <h1 style={{ color: "#2c3e50", marginBottom: "0.3rem" }}>📈 Hiring Analytics</h1>
        <p style={{ color: "#7f8c8d", marginBottom: 0 }}>Complete overview of your recruitment activity</p>

        {data && <>
          {/* KPIs */}
          <div style={s.kpiGrid}>
            {kpis.map(([icon, label, val, color]) => (
              <div key={label} style={s.kpi(color)}>
                <div style={{ fontSize: "1.5rem" }}>{icon}</div>
                <div style={{ fontSize: "1.8rem", fontWeight: 800, color: "#2c3e50" }}>{val}</div>
                <div style={{ fontSize: "0.75rem", color: "#95a5a6", marginTop: "0.2rem" }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Top Jobs */}
          <div style={s.section}>
            <h3 style={{ marginBottom: "1rem" }}>🏆 Top Job Postings by Applications</h3>
            {(data.top_jobs || []).map((job, i) => {
              const max = Math.max(...(data.top_jobs || []).map(j => j.applications));
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "0.8rem" }}>
                  <div style={{ minWidth: 160, fontSize: "0.85rem", fontWeight: 600, color: "#2c3e50" }}>{job.title}</div>
                  <div style={{ flex: 1, background: "#f0f0f0", borderRadius: 6, height: 20, overflow: "hidden" }}>
                    <div style={{ height: "100%", background: "#3498db", borderRadius: 6, width: `${(job.applications / max) * 100}%` }} />
                  </div>
                  <div style={{ minWidth: 40, fontWeight: 700, color: "#2c3e50", fontSize: "0.85rem" }}>{job.applications}</div>
                </div>
              );
            })}
          </div>

          {/* Pipeline + Skills */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div style={s.section}>
              <h3 style={{ marginBottom: "1rem" }}>🔄 Candidate Pipeline</h3>
              {(data.status_breakdown || []).map((s2, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: "1px solid #f0f0f0" }}>
                  <span style={{ color: "#555", fontSize: "0.87rem" }}>{s2.status}</span>
                  <span style={{ fontWeight: 700, color: "#2c3e50" }}>{s2.count}</span>
                </div>
              ))}
            </div>
            <div style={s.section}>
              <h3 style={{ marginBottom: "1rem" }}>🎯 Top Skills in Demand</h3>
              {(data.top_skills || []).slice(0, 6).map((sk, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: "1px solid #f0f0f0" }}>
                  <span style={{ color: "#555", fontSize: "0.87rem" }}>{sk.skill}</span>
                  <span style={{ fontWeight: 700, color: "#2c3e50" }}>{sk.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Insights */}
          <div style={s.section}>
            <h3 style={{ marginBottom: "1rem" }}>💡 Key Insights</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(260px,1fr))", gap: "0.8rem" }}>
              {(data.insights || []).map((ins, i) => (
                <div key={i} style={{ background: "#f8f9fa", borderRadius: 10, padding: "1rem", display: "flex", gap: "0.7rem" }}>
                  <span style={{ fontSize: "1.3rem" }}>{ins.icon}</span>
                  <p style={{ fontSize: "0.83rem", color: "#555", margin: 0, lineHeight: 1.5 }}>{ins.text}</p>
                </div>
              ))}
            </div>
          </div>
        </>}
      </div>
    </div>
  );
}

// ── Layout ────────────────────────────────────────────────────────────────
const RECRUITER_PATHS = [
  "/recruiter-dashboard", "/post-job", "/job-listings", "/job/",
  "/search-candidates", "/resume-matching", "/shortlist-manager",
  "/analytics", "/edit-job/",
];

function LayoutWrapper({ children }) {
  const location = useLocation();
  const isRecruiterPage = RECRUITER_PATHS.some(p => location.pathname.startsWith(p));
  const isAuthPage = location.pathname === "/role-selection" || location.pathname === "/login";

  return (
    <div className="app-container">
      {isRecruiterPage && <RecruiterNavbar />}
      {!isRecruiterPage && !isAuthPage && <Navbar />}
      <div className={`content-wrap${isRecruiterPage ? " recruiter-content" : ""}`}>
        {children}
      </div>
      {!isRecruiterPage && !isAuthPage && <Footer />}
    </div>
  );
}

function App() {
  return (
    <Router>
      <LayoutWrapper>
        <Routes>
          <Route path="/role-selection"      element={<RoleSelection />} />
          <Route path="/login"               element={<Login />} />

          <Route path="/"                    element={<Home />} />
          <Route path="/domain-check"        element={<DomainCheck />} />
          <Route path="/skill-predict"       element={<SkillPrediction />} />
          <Route path="/result"              element={<PredictionResult />} />
          <Route path="/about"               element={<About />} />
          <Route path="/testimonials"        element={<Testimonials />} />
          <Route path="/contact"             element={<Contact />} />
          <Route path="/resume-optimizer"    element={<ResumeOptimizer />} />

          <Route path="/mock-interview"      element={<InterviewSetup />} />
          <Route path="/interview-session"   element={<InterviewSession />} />
          <Route path="/interview-feedback"  element={<InterviewFeedback />} />
          <Route path="/interview-history"   element={<InterviewHistory />} />

          <Route path="/mock-test"           element={<SubjectSelection />} />
          <Route path="/mock-test/quiz"      element={<MockTestQuiz />} />
          <Route path="/mock-test/result"    element={<ResultPage />} />
          <Route path="/mock-test/history"   element={<TestHistory />} />

          <Route path="/recruiter-dashboard" element={<RecruiterDashboard />} />
          <Route path="/post-job"            element={<JobPosting />} />
          <Route path="/job-listings"        element={<JobListings />} />
          <Route path="/job/:id"             element={<JobDetailPage />} />
          <Route path="/search-candidates"   element={<CandidateSearch />} />
          <Route path="/resume-matching"     element={<ResumeMatching />} />
          <Route path="/shortlist-manager"   element={<ShortlistManager />} />
          <Route path="/analytics"           element={<AnalyticsPage />} />
        </Routes>
      </LayoutWrapper>
    </Router>
  );
}

export default App;
