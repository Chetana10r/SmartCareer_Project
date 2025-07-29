import React, { useState } from 'react';
import axios from 'axios';

const ResumeOptimizer = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState({
    fullName: '',
    email: '',
    phone: '',
    location: '',
    linkedin: '',
    github: '',
    website: '',
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAdditionalInfo((prev) => ({ ...prev, [name]: value }));
  };

  const handleOptimize = async () => {
    if (!resumeFile) {
      alert('Please upload a resume file');
      return;
    }
    if (!jobDescription.trim()) {
      alert('Please enter the job description');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('job_description', jobDescription);
      formData.append('additional_info', JSON.stringify(additionalInfo));

      const response = await axios.post('http://127.0.0.1:5000/optimize_resume', formData, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'optimized_resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('There was an error optimizing the resume.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#1a1a1a', color: '#fff', minHeight: '100vh', padding: 20, fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ color: '#0a74da', textAlign: 'center', marginBottom: 16 }}>🚀 Resume Optimizer</h2>
      <div style={{ marginBottom: 24, padding: 16, backgroundColor: '#292929', borderRadius: 8 }}>
        <h3>1. Upload Your Resume (PDF only)</h3>
        <input type="file" accept=".pdf" onChange={(e) => setResumeFile(e.target.files[0])} style={{ marginTop: 8, color: '#bbb' }} />
      </div>
      <div style={{ marginBottom: 24, padding: 16, backgroundColor: '#292929', borderRadius: 8 }}>
        <h3>2. Enter Job Description</h3>
        <textarea rows={6} value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} placeholder="Paste the job description here..." style={{ width: '100%', padding: 10, backgroundColor: '#2a2a2a', color: '#fff', border: '1px solid #444', borderRadius: 4, fontSize: 16, fontFamily: 'inherit' }} />
      </div>
      <div style={{ marginBottom: 24, padding: 16, backgroundColor: '#292929', borderRadius: 8 }}>
        <h3>3. Personal Information (Optional)</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
          {[
            { label: 'Full Name', name: 'fullName', type: 'text' },
            { label: 'Email', name: 'email', type: 'email' },
            { label: 'Phone', name: 'phone', type: 'tel' },
            { label: 'Location', name: 'location', type: 'text' },
            { label: 'LinkedIn URL', name: 'linkedin', type: 'url' },
            { label: 'GitHub URL', name: 'github', type: 'url' },
            { label: 'Personal Website', name: 'website', type: 'url' },
          ].map(({ label, name, type }) => (
            <div key={name} style={{ flex: '1 1 200px' }}>
              <label htmlFor={name} style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>{label}</label>
              <input type={type} id={name} name={name} value={additionalInfo[name]} onChange={handleInputChange} placeholder={label} style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #555', backgroundColor: '#1a1a1a', color: '#fff' }} />
            </div>
          ))}
        </div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <button onClick={handleOptimize} disabled={loading || !resumeFile || !jobDescription.trim()} style={{ padding: '12px 24px', fontSize: '1.1rem', fontWeight: 'bold', color: '#fff', backgroundColor: loading ? '#555' : '#0a74da', border: 'none', borderRadius: 6, cursor: loading ? 'not-allowed' : 'pointer', transition: 'background-color 0.3s ease' }} aria-busy={loading}>
          {loading ? 'Optimizing...' : '✨ Optimize Resume'}
        </button>
      </div>
    </div>
  );
};

export default ResumeOptimizer;
