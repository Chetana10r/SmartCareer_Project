import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Analytics.css';

function Analytics() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_analytics', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const json = await response.json();
      setData(json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="an-loading">
      <div className="an-spinner"></div>
      <p>Loading analytics...</p>
    </div>
  );

  if (!data) return <div className="an-loading"><p>No data available</p></div>;

  const { overview, jobs_by_type, top_skills, monthly_applications, candidate_locations, status_breakdown } = data;

  // Simple bar chart renderer
  const BarChart = ({ items, colorFn }) => {
    const max = Math.max(...items.map(i => i.value));
    return (
      <div className="an-bar-chart">
        {items.map((item, idx) => (
          <div key={idx} className="an-bar-row">
            <span className="an-bar-label">{item.label}</span>
            <div className="an-bar-track">
              <div
                className="an-bar-fill"
                style={{
                  width: `${(item.value / max) * 100}%`,
                  background: colorFn ? colorFn(idx) : '#3498db'
                }}
              ></div>
            </div>
            <span className="an-bar-value">{item.value}</span>
          </div>
        ))}
      </div>
    );
  };

  const COLORS = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e'];

  return (
    <div className="an-container">
      {/* Header */}
      <div className="an-header">
        <button className="an-back-btn" onClick={() => navigate('/recruiter-dashboard')}>
          ← Back to Dashboard
        </button>
        <div>
          <h1 className="an-title">📈 Hiring Analytics</h1>
          <p className="an-subtitle">Complete overview of your recruitment activity</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="an-kpi-grid">
        <div className="an-kpi-card" style={{ borderTop: '4px solid #3498db' }}>
          <div className="an-kpi-icon">📋</div>
          <div className="an-kpi-value">{overview.total_jobs}</div>
          <div className="an-kpi-label">Total Jobs Posted</div>
        </div>
        <div className="an-kpi-card" style={{ borderTop: '4px solid #2ecc71' }}>
          <div className="an-kpi-icon">✅</div>
          <div className="an-kpi-value">{overview.active_jobs}</div>
          <div className="an-kpi-label">Active Jobs</div>
        </div>
        <div className="an-kpi-card" style={{ borderTop: '4px solid #e74c3c' }}>
          <div className="an-kpi-icon">📬</div>
          <div className="an-kpi-value">{overview.total_applications}</div>
          <div className="an-kpi-label">Total Applications</div>
        </div>
        <div className="an-kpi-card" style={{ borderTop: '4px solid #f39c12' }}>
          <div className="an-kpi-icon">⭐</div>
          <div className="an-kpi-value">{overview.total_shortlisted}</div>
          <div className="an-kpi-label">Shortlisted</div>
        </div>
        <div className="an-kpi-card" style={{ borderTop: '4px solid #9b59b6' }}>
          <div className="an-kpi-icon">🎯</div>
          <div className="an-kpi-value">{overview.total_interviewed}</div>
          <div className="an-kpi-label">Interviewed</div>
        </div>
        <div className="an-kpi-card" style={{ borderTop: '4px solid #1abc9c' }}>
          <div className="an-kpi-icon">✅</div>
          <div className="an-kpi-value">{overview.total_hired}</div>
          <div className="an-kpi-label">Hired</div>
        </div>
        <div className="an-kpi-card" style={{ borderTop: '4px solid #e67e22' }}>
          <div className="an-kpi-icon">📊</div>
          <div className="an-kpi-value">{overview.avg_applications_per_job}</div>
          <div className="an-kpi-label">Avg. Applications/Job</div>
        </div>
        <div className="an-kpi-card" style={{ borderTop: '4px solid #34495e' }}>
          <div className="an-kpi-icon">🏆</div>
          <div className="an-kpi-value">{overview.hire_rate}%</div>
          <div className="an-kpi-label">Hire Rate</div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="an-charts-row">
        {/* Monthly Applications */}
        <div className="an-chart-card an-wide">
          <h2 className="an-chart-title">📅 Monthly Application Trends</h2>
          <div className="an-line-chart">
            {monthly_applications.map((m, i) => (
              <div key={i} className="an-month-col">
                <div
                  className="an-month-bar"
                  style={{ height: `${(m.applications / Math.max(...monthly_applications.map(x => x.applications))) * 160}px` }}
                  title={`${m.applications} applications`}
                ></div>
                <div className="an-month-label">{m.month}</div>
                <div className="an-month-val">{m.applications}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Candidate Status Breakdown */}
        <div className="an-chart-card">
          <h2 className="an-chart-title">🔄 Candidate Pipeline</h2>
          <div className="an-pipeline">
            {status_breakdown.map((s, i) => (
              <div key={i} className="an-pipeline-row">
                <div className="an-pipeline-info">
                  <span className="an-pipeline-dot" style={{ background: COLORS[i] }}></span>
                  <span className="an-pipeline-label">{s.status}</span>
                </div>
                <div className="an-pipeline-bar-wrap">
                  <div
                    className="an-pipeline-bar"
                    style={{
                      width: `${(s.count / Math.max(...status_breakdown.map(x => x.count))) * 100}%`,
                      background: COLORS[i]
                    }}
                  ></div>
                </div>
                <span className="an-pipeline-count">{s.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="an-charts-row">
        {/* Top Skills */}
        <div className="an-chart-card">
          <h2 className="an-chart-title">🎯 Most In-Demand Skills</h2>
          <BarChart
            items={top_skills.map(s => ({ label: s.skill, value: s.count }))}
            colorFn={(i) => COLORS[i % COLORS.length]}
          />
        </div>

        {/* Jobs by Type */}
        <div className="an-chart-card">
          <h2 className="an-chart-title">💼 Jobs by Type</h2>
          <div className="an-donut-wrap">
            {jobs_by_type.map((t, i) => {
              const total = jobs_by_type.reduce((s, x) => s + x.count, 0);
              const pct = Math.round((t.count / total) * 100);
              return (
                <div key={i} className="an-donut-item">
                  <div className="an-donut-circle" style={{ background: COLORS[i % COLORS.length] }}>
                    {pct}%
                  </div>
                  <div className="an-donut-label">{t.type}</div>
                  <div className="an-donut-count">{t.count} jobs</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Candidate Locations */}
        <div className="an-chart-card">
          <h2 className="an-chart-title">📍 Candidate Locations</h2>
          <BarChart
            items={candidate_locations.map(l => ({ label: l.city, value: l.count }))}
            colorFn={(i) => COLORS[(i + 3) % COLORS.length]}
          />
        </div>
      </div>

      {/* Top Performing Jobs Table */}
      <div className="an-table-card">
        <h2 className="an-chart-title">🏆 Top Performing Job Postings</h2>
        <div className="an-table-wrap">
          <table className="an-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Job Title</th>
                <th>Company</th>
                <th>Applications</th>
                <th>Status</th>
                <th>Posted</th>
              </tr>
            </thead>
            <tbody>
              {data.top_jobs.map((job, i) => (
                <tr key={i}>
                  <td>{i + 1}</td>
                  <td><strong>{job.title}</strong></td>
                  <td>{job.company}</td>
                  <td>
                    <span className="an-app-badge">{job.applications}</span>
                  </td>
                  <td>
                    <span className={`an-job-status ${job.status}`}>{job.status}</span>
                  </td>
                  <td>{job.postedDate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Insights */}
      <div className="an-insights">
        <h2 className="an-chart-title">💡 Key Insights</h2>
        <div className="an-insights-grid">
          {data.insights.map((insight, i) => (
            <div key={i} className="an-insight-card">
              <span className="an-insight-icon">{insight.icon}</span>
              <p className="an-insight-text">{insight.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Analytics;
