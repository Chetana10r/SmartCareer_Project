import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './JobApplicants.css';

function JobApplicants() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const [jobsRes, applicantsRes] = await Promise.all([
        fetch('http://127.0.0.1:5000/get_recruiter_jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ recruiter_id: localStorage.getItem('userId') || 'recruiter_1' })
        }),
        fetch('http://127.0.0.1:5000/get_job_applicants', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ job_id: parseInt(id) })
        })
      ]);

      const jobsData = await jobsRes.json();
      const appsData = await applicantsRes.json();

      const found = (jobsData.jobs || []).find(j => String(j.id) === String(id));
      setJob(found || null);
      setApplicants(appsData.applicants || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleShortlist = async (candidateId, candidateName) => {
    try {
      await fetch('http://127.0.0.1:5000/shortlist_candidate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidateId,
          job_title: job?.title || '',
          recruiter_id: localStorage.getItem('userId') || 'recruiter_1'
        })
      });
      setApplicants(prev =>
        prev.map(a => a.id === candidateId ? { ...a, status: 'shortlisted' } : a)
      );
      alert(`${candidateName} has been shortlisted!`);
    } catch (err) {
      alert('Shortlisted!');
    }
  };

  const getMatchColor = (score) => {
    if (score >= 85) return '#27ae60';
    if (score >= 70) return '#f39c12';
    return '#e74c3c';
  };

  const getStatusBadge = (status) => {
    const map = {
      applied:     { bg: '#eaf4fb', color: '#2980b9', label: 'Applied' },
      shortlisted: { bg: '#eafaf1', color: '#27ae60', label: 'Shortlisted' },
      reviewed:    { bg: '#fef9e7', color: '#f39c12', label: 'Reviewed' },
      rejected:    { bg: '#fdecea', color: '#e74c3c', label: 'Rejected' },
    };
    return map[status] || map.applied;
  };

  const filtered = filterStatus === 'all'
    ? applicants
    : applicants.filter(a => a.status === filterStatus);

  if (loading) return (
    <div className="ja-loading">
      <div className="ja-spinner"></div>
      <p>Loading applicants...</p>
    </div>
  );

  return (
    <div className="ja-container">
      {/* Header */}
      <div className="ja-header">
        <button className="ja-back-btn" onClick={() => navigate('/job-listings')}>
          ← Back to Job Listings
        </button>
        {job && (
          <div className="ja-job-info">
            <h1 className="ja-title">👥 Applicants — {job.title}</h1>
            <p className="ja-subtitle">{job.company} · {job.location} · {applicants.length} total applicants</p>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="ja-stats">
        {['all', 'applied', 'shortlisted', 'reviewed', 'rejected'].map(s => (
          <div
            key={s}
            className={`ja-stat-chip ${filterStatus === s ? 'active' : ''}`}
            onClick={() => setFilterStatus(s)}
          >
            <span className="ja-stat-num">
              {s === 'all' ? applicants.length : applicants.filter(a => a.status === s).length}
            </span>
            <span className="ja-stat-label">{s.charAt(0).toUpperCase() + s.slice(1)}</span>
          </div>
        ))}
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div className="ja-empty">
          <div>📭</div>
          <h3>No applicants in this category</h3>
        </div>
      ) : (
        <div className="ja-list">
          {filtered.map(applicant => {
            const badge = getStatusBadge(applicant.status);
            return (
              <div key={applicant.id} className="ja-card">
                <div className="ja-card-left">
                  <div className="ja-avatar">{applicant.name.charAt(0)}</div>
                  <div className="ja-info">
                    <h3 className="ja-name">{applicant.name}</h3>
                    <div className="ja-details">
                      <span>📧 {applicant.email}</span>
                      <span>📱 {applicant.phone}</span>
                      <span>📍 {applicant.location}</span>
                      <span>💼 {applicant.experience} exp.</span>
                    </div>
                    <div className="ja-edu">🎓 {applicant.education}</div>
                    <div className="ja-skills">
                      {applicant.skills.slice(0, 4).map((s, i) => (
                        <span key={i} className="ja-skill">{s}</span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="ja-card-right">
                  <div
                    className="ja-match"
                    style={{ borderColor: getMatchColor(applicant.match_score), color: getMatchColor(applicant.match_score) }}
                  >
                    {applicant.match_score}%<br />
                    <small>Match</small>
                  </div>
                  <span
                    className="ja-status"
                    style={{ background: badge.bg, color: badge.color }}
                  >
                    {badge.label}
                  </span>
                  <div className="ja-actions">
                    {applicant.status !== 'shortlisted' && (
                      <button
                        className="ja-btn-shortlist"
                        onClick={() => handleShortlist(applicant.id, applicant.name)}
                      >
                        ⭐ Shortlist
                      </button>
                    )}
                    <button
                      className="ja-btn-contact"
                      onClick={() => alert(`Contact: ${applicant.email}`)}
                    >
                      ✉️ Contact
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default JobApplicants;
