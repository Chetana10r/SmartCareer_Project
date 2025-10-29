import React, { useState } from "react";
import axios from "axios";
import "./ResumeOptimizer.css";

const ResumeOptimizer = () => {
  const [mode, setMode] = useState("optimize"); // 'optimize' or 'create'
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [atsScore, setAtsScore] = useState(null);

  // Form data for creating resume from scratch
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    location: "",
    linkedin: "",
    github: "",
    summary: "",
    skills: {
      programming: "",
      ml_ds: "",
      libraries: "",
      databases: "",
      platforms: "",
    },
    education: [
      {
        institution: "",
        degree: "",
        field: "",
        cgpa: "",
        duration: "",
        location: "",
      },
    ],
    experience: [
      {
        company: "",
        title: "",
        location: "",
        duration: "",
        responsibilities: [""],
      },
    ],
    projects: [
      {
        name: "",
        technologies: "",
        description: [""],
      },
    ],
    certifications: [""],
    achievements: [""],
  });

  // File upload handler
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setResumeFile(file);
      setErrorMessage("");
      setAtsScore(null);
    } else {
      setErrorMessage("Please upload a valid PDF file");
      setResumeFile(null);
    }
  };

  // Form input handlers
  const handlePersonalInfoChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSkillsChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      skills: { ...prev.skills, [field]: value },
    }));
  };

  const handleArrayFieldChange = (section, index, field, value) => {
    setFormData((prev) => {
      const updated = [...prev[section]];
      updated[index][field] = value;
      return { ...prev, [section]: updated };
    });
  };

  const handleSubArrayChange = (section, index, subField, subIndex, value) => {
    setFormData((prev) => {
      const updated = [...prev[section]];
      updated[index][subField][subIndex] = value;
      return { ...prev, [section]: updated };
    });
  };

  const addArrayItem = (section, template) => {
    setFormData((prev) => ({
      ...prev,
      [section]: [...prev[section], template],
    }));
  };

  const removeArrayItem = (section, index) => {
    setFormData((prev) => ({
      ...prev,
      [section]: prev[section].filter((_, i) => i !== index),
    }));
  };

  const addSubArrayItem = (section, index, subField) => {
    setFormData((prev) => {
      const updated = [...prev[section]];
      updated[index][subField].push("");
      return { ...prev, [section]: updated };
    });
  };

  const removeSubArrayItem = (section, index, subField, subIndex) => {
    setFormData((prev) => {
      const updated = [...prev[section]];
      updated[index][subField] = updated[index][subField].filter(
        (_, i) => i !== subIndex
      );
      return { ...prev, [section]: updated };
    });
  };

  // Check ATS Score
  const handleCheckATS = async () => {
    if (!resumeFile) {
      setErrorMessage("Please upload a resume file");
      return;
    }
    if (!jobDescription.trim()) {
      setErrorMessage("Please enter the job description to check ATS score");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const formDataToSend = new FormData();
      formDataToSend.append("resume", resumeFile);
      formDataToSend.append("job_description", jobDescription);

      const response = await axios.post(
        "http://127.0.0.1:5000/check_ats_score",
        formDataToSend
      );
      setAtsScore(response.data);
      setSuccessMessage("✅ ATS Score calculated successfully!");
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (error) {
      setErrorMessage(
        "❌ Error checking ATS score: " +
          (error.response?.data?.error || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  // Optimize existing resume
  const handleOptimizeResume = async () => {
    if (!resumeFile) {
      setErrorMessage("Please upload a resume file");
      return;
    }
    if (!jobDescription.trim()) {
      setErrorMessage("Please enter the job description");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    setUploadProgress(0);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append("resume", resumeFile);
      formDataToSend.append("job_description", jobDescription);

      const response = await axios.post(
        "http://127.0.0.1:5000/optimize_resume",
        formDataToSend,
        {
          responseType: "blob",
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setUploadProgress(percentCompleted);
          },
        }
      );

      downloadPDF(response.data, "optimized_resume.pdf");
      setSuccessMessage("✅ Resume optimized successfully!");
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (error) {
      setErrorMessage(
        "❌ Error optimizing resume: " +
          (error.response?.data?.error || error.message)
      );
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  // Create new resume
  const handleCreateResume = async () => {
    if (!formData.name || !formData.email) {
      setErrorMessage("Please fill in at least Name and Email");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/create_resume",
        {
          ...formData,
          job_description: jobDescription,
        },
        {
          responseType: "blob",
        }
      );

      downloadPDF(response.data, "generated_resume.pdf");
      setSuccessMessage("✅ Resume created successfully!");
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (error) {
      setErrorMessage(
        "❌ Error creating resume: " +
          (error.response?.data?.error || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  // Download PDF helper
  const downloadPDF = (blob, filename) => {
    const url = window.URL.createObjectURL(
      new Blob([blob], { type: "application/pdf" })
    );
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="optimizer-container">
      {/* Header */}
      <div className="header-section styled-header">
        <div className="header-content">
          <h1 className="main-title">
            <span role="img" aria-label="target" className="title-icon">
              🎯
            </span>
            AI Resume Builder & Optimizer
          </h1>
          <p className="subtitle">
            Create ATS-friendly resumes or optimize existing ones for your dream
            job
          </p>
        </div>
      </div>

      {/* Messages */}
      {successMessage && (
        <div className="alert alert-success">{successMessage}</div>
      )}
      {errorMessage && <div className="alert alert-error">{errorMessage}</div>}

      {/* Mode Selector */}
      <div className="mode-selector">
        <button
          onClick={() => {
            setMode("optimize");
            setAtsScore(null);
          }}
          className={`mode-button ${mode === "optimize" ? "active" : ""}`}
          style={{
            background:
              mode === "optimize"
                ? "linear-gradient(90deg, #7442ff 0%, #6fd6ff 100%)"
                : "linear-gradient(90deg, #bcbcbc 0%, #f7f7f7 100%)",
            color: mode === "optimize" ? "#fff" : "#222",
            boxShadow:
              mode === "optimize" ? "0 3px 16px rgba(116,66,255,0.3)" : "",
            fontWeight: "600",
            borderRadius: "30px",
            marginRight: "1em",
            transition: "all 0.25s linear",
          }}
        >
          📄 Optimize Resume
        </button>

        <button
          onClick={() => {
            setMode("create");
            setAtsScore(null);
          }}
          className={`mode-button ${mode === "create" ? "active" : ""}`}
          style={{
            background:
              mode === "create"
                ? "linear-gradient(90deg, #42e695 0%, #3bb2b8 100%)"
                : "linear-gradient(90deg, #bcbcbc 0%, #f7f7f7 100%)",
            color: mode === "create" ? "#fff" : "#222",
            boxShadow:
              mode === "create" ? "0 3px 16px rgba(66,230,149,0.26)" : "",
            fontWeight: "600",
            borderRadius: "30px",
            marginLeft: "1em",
            transition: "all 0.25s linear",
          }}
        >
          ✨ Create New Resume
        </button>
      </div>

      <div className="content-wrapper">
        {mode === "optimize" ? (
          <>
            {/* Optimize Mode */}
            <div className="card">
              <div className="card-header">
                <span className="step-number">1</span>
                <h2 className="card-title">Upload Your Resume</h2>
              </div>
              <div className="card-body">
                <div className="upload-area">
                  <input
                    type="file"
                    id="resume-upload"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="file-input"
                  />
                  <label htmlFor="resume-upload" className="upload-label">
                    <div className="upload-icon">📄</div>
                    <p className="upload-text">
                      {resumeFile ? (
                        <>
                          <span className="file-name">{resumeFile.name}</span>
                          <span className="file-size">
                            {" "}
                            ({(resumeFile.size / 1024).toFixed(2)} KB)
                          </span>
                        </>
                      ) : (
                        "Click to upload or drag and drop"
                      )}
                    </p>
                    <p className="upload-hint">PDF files only (Max 5MB)</p>
                  </label>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <span className="step-number">2</span>
                <h2 className="card-title">Job Description</h2>
              </div>
              <div className="card-body">
                <textarea
                  rows={10}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the complete job description here...&#10;&#10;Include:&#10;• Job requirements&#10;• Required skills&#10;• Responsibilities&#10;• Qualifications"
                  className="textarea"
                />
                <div className="char-count">
                  {jobDescription.length} characters
                </div>
              </div>
            </div>

            {/* ATS Score Display */}
            {atsScore && (
              <div className="card ats-score-card">
                <div className="card-header">
                  <span className="step-number">📊</span>
                  <h2 className="card-title">ATS Compatibility Score</h2>
                </div>
                <div className="card-body">
                  <div className="score-display">
                    <div className="score-circle">
                      <span className="score-value">{atsScore.ats_score}</span>
                      <span className="score-label">/ 100</span>
                    </div>
                    <div className="score-breakdown">
                      <div className="score-item">
                        <span className="score-item-label">Keyword Match:</span>
                        <span className="score-item-value">
                          {atsScore.keyword_match_score}%
                        </span>
                      </div>
                      <div className="score-item">
                        <span className="score-item-label">Format Score:</span>
                        <span className="score-item-value">
                          {atsScore.format_score}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {atsScore.matched_skills &&
                    atsScore.matched_skills.length > 0 && (
                      <div className="skills-section">
                        <h3>✅ Matched Skills:</h3>
                        <div className="skills-tags">
                          {atsScore.matched_skills.map((skill, idx) => (
                            <span key={idx} className="skill-tag matched">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                  {atsScore.missing_keywords &&
                    atsScore.missing_keywords.length > 0 && (
                      <div className="skills-section">
                        <h3>❌ Missing Keywords:</h3>
                        <div className="skills-tags">
                          {atsScore.missing_keywords.map((keyword, idx) => (
                            <span key={idx} className="skill-tag missing">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                  {atsScore.suggestions && (
                    <div className="suggestions-section">
                      <h3>💡 Suggestions:</h3>
                      <ul>
                        {atsScore.suggestions.map((suggestion, idx) => (
                          <li key={idx}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Progress Bar */}
            {loading && uploadProgress > 0 && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="progress-text">{uploadProgress}% Uploaded</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="action-section centered-action">
              <div className="button-group">
                <button
                  onClick={handleCheckATS}
                  disabled={loading || !resumeFile || !jobDescription.trim()}
                  className="secondary-button creative-button"
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      <span>⏳ Checking...</span>
                    </>
                  ) : (
                    <>
                      <span className="button-icon">📊</span>
                      <span>Check ATS Score</span>
                    </>
                  )}
                </button>

                <button
                  onClick={handleOptimizeResume}
                  disabled={loading || !resumeFile || !jobDescription.trim()}
                  className="optimize-button creative-button"
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      <span>Optimizing...</span>
                    </>
                  ) : (
                    <>
                      <span className="button-icon">✨</span>
                      <span>Optimize Resume</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Create Mode */}
            <div className="card">
              <div className="card-header">
                <span className="step-number">1</span>
                <h2 className="card-title">Personal Information</h2>
              </div>
              <div className="card-body">
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">
                      <span className="label-icon">👤</span>
                      Full Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) =>
                        handlePersonalInfoChange("name", e.target.value)
                      }
                      placeholder="John Doe"
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      <span className="label-icon">📧</span>
                      Email *
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) =>
                        handlePersonalInfoChange("email", e.target.value)
                      }
                      placeholder="john.doe@example.com"
                      className="form-input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      <span className="label-icon">📱</span>
                      Phone
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) =>
                        handlePersonalInfoChange("phone", e.target.value)
                      }
                      placeholder="+91-1234567890"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      <span className="label-icon">📍</span>
                      Location
                    </label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) =>
                        handlePersonalInfoChange("location", e.target.value)
                      }
                      placeholder="City, Country"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      <span className="label-icon">💼</span>
                      LinkedIn
                    </label>
                    <input
                      type="url"
                      value={formData.linkedin}
                      onChange={(e) =>
                        handlePersonalInfoChange("linkedin", e.target.value)
                      }
                      placeholder="linkedin.com/in/username"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      <span className="label-icon">💻</span>
                      GitHub
                    </label>
                    <input
                      type="url"
                      value={formData.github}
                      onChange={(e) =>
                        handlePersonalInfoChange("github", e.target.value)
                      }
                      placeholder="github.com/username"
                      className="form-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <span className="step-number">2</span>
                <h2 className="card-title">Job Description (Optional)</h2>
              </div>
              <div className="card-body">
                <textarea
                  rows={6}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste job description to tailor your resume automatically..."
                  className="textarea"
                />
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <span className="step-number">3</span>
                <h2 className="card-title">Professional Summary</h2>
              </div>
              <div className="card-body">
                <textarea
                  rows={4}
                  value={formData.summary}
                  onChange={(e) =>
                    handlePersonalInfoChange("summary", e.target.value)
                  }
                  placeholder="Write a brief professional summary (2-3 sentences)..."
                  className="textarea"
                />
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <span className="step-number">4</span>
                <h2 className="card-title">Technical Skills</h2>
              </div>
              <div className="card-body">
                <div className="form-grid-single">
                  <div className="form-group">
                    <label className="form-label">
                      Programming & Languages
                    </label>
                    <input
                      type="text"
                      value={formData.skills.programming}
                      onChange={(e) =>
                        handleSkillsChange("programming", e.target.value)
                      }
                      placeholder="Python, Java, SQL, C++"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      Machine Learning & Data Science
                    </label>
                    <input
                      type="text"
                      value={formData.skills.ml_ds}
                      onChange={(e) =>
                        handleSkillsChange("ml_ds", e.target.value)
                      }
                      placeholder="Machine Learning, NLP, Deep Learning"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Libraries & Frameworks</label>
                    <input
                      type="text"
                      value={formData.skills.libraries}
                      onChange={(e) =>
                        handleSkillsChange("libraries", e.target.value)
                      }
                      placeholder="TensorFlow, Pandas, React, Flask"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Databases & Tools</label>
                    <input
                      type="text"
                      value={formData.skills.databases}
                      onChange={(e) =>
                        handleSkillsChange("databases", e.target.value)
                      }
                      placeholder="MySQL, MongoDB, Git, Docker"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      Platforms & Operating Systems
                    </label>
                    <input
                      type="text"
                      value={formData.skills.platforms}
                      onChange={(e) =>
                        handleSkillsChange("platforms", e.target.value)
                      }
                      placeholder="Windows, Linux, AWS, Azure"
                      className="form-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Education Section */}
            <div className="card">
              <div className="card-header">
                <span className="step-number">5</span>
                <h2 className="card-title">Education</h2>
                <button
                  onClick={() =>
                    addArrayItem("education", {
                      institution: "",
                      degree: "",
                      field: "",
                      cgpa: "",
                      duration: "",
                      location: "",
                    })
                  }
                  className="add-button"
                >
                  + Add Education
                </button>
              </div>
              <div className="card-body">
                {formData.education.map((edu, index) => (
                  <div key={index} className="array-item">
                    <div className="array-item-header">
                      <h3>Education #{index + 1}</h3>
                      {formData.education.length > 1 && (
                        <button
                          onClick={() => removeArrayItem("education", index)}
                          className="remove-button"
                        >
                          ✕ Remove
                        </button>
                      )}
                    </div>
                    <div className="form-grid">
                      <div className="form-group">
                        <label className="form-label">Institution</label>
                        <input
                          type="text"
                          value={edu.institution}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "education",
                              index,
                              "institution",
                              e.target.value
                            )
                          }
                          placeholder="University Name"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Degree</label>
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "education",
                              index,
                              "degree",
                              e.target.value
                            )
                          }
                          placeholder="B.Sc., M.Sc., B.Tech"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Field of Study</label>
                        <input
                          type="text"
                          value={edu.field}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "education",
                              index,
                              "field",
                              e.target.value
                            )
                          }
                          placeholder="Computer Science"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">CGPA/Percentage</label>
                        <input
                          type="text"
                          value={edu.cgpa}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "education",
                              index,
                              "cgpa",
                              e.target.value
                            )
                          }
                          placeholder="9.5 or 95%"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Duration</label>
                        <input
                          type="text"
                          value={edu.duration}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "education",
                              index,
                              "duration",
                              e.target.value
                            )
                          }
                          placeholder="Jul 2020 – Jun 2024"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Location</label>
                        <input
                          type="text"
                          value={edu.location}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "education",
                              index,
                              "location",
                              e.target.value
                            )
                          }
                          placeholder="City, Country"
                          className="form-input"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Projects Section */}
            <div className="card">
              <div className="card-header">
                <span className="step-number">6</span>
                <h2 className="card-title">Projects</h2>
                <button
                  onClick={() =>
                    addArrayItem("projects", {
                      name: "",
                      technologies: "",
                      description: [""],
                    })
                  }
                  className="add-button"
                >
                  + Add Project
                </button>
              </div>
              <div className="card-body">
                {formData.projects.map((project, index) => (
                  <div key={index} className="array-item">
                    <div className="array-item-header">
                      <h3>Project #{index + 1}</h3>
                      {formData.projects.length > 1 && (
                        <button
                          onClick={() => removeArrayItem("projects", index)}
                          className="remove-button"
                        >
                          ✕ Remove
                        </button>
                      )}
                    </div>
                    <div className="form-grid-single">
                      <div className="form-group">
                        <label className="form-label">Project Name</label>
                        <input
                          type="text"
                          value={project.name}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "projects",
                              index,
                              "name",
                              e.target.value
                            )
                          }
                          placeholder="AI Chatbot System"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Technologies Used</label>
                        <input
                          type="text"
                          value={project.technologies}
                          onChange={(e) =>
                            handleArrayFieldChange(
                              "projects",
                              index,
                              "technologies",
                              e.target.value
                            )
                          }
                          placeholder="Python, Flask, TensorFlow"
                          className="form-input"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Description Points</label>
                        {project.description.map((desc, descIndex) => (
                          <div key={descIndex} className="sub-array-item">
                            <textarea
                              rows={2}
                              value={desc}
                              onChange={(e) =>
                                handleSubArrayChange(
                                  "projects",
                                  index,
                                  "description",
                                  descIndex,
                                  e.target.value
                                )
                              }
                              placeholder="Describe your achievement or contribution..."
                              className="form-input"
                            />
                            <div className="sub-array-buttons">
                              {project.description.length > 1 && (
                                <button
                                  onClick={() =>
                                    removeSubArrayItem(
                                      "projects",
                                      index,
                                      "description",
                                      descIndex
                                    )
                                  }
                                  className="remove-button-small"
                                >
                                  ✕
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                        <button
                          onClick={() =>
                            addSubArrayItem("projects", index, "description")
                          }
                          className="add-button-small"
                        >
                          + Add Description Point
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Certifications Section */}
            <div className="card">
              <div className="card-header">
                <span className="step-number">7</span>
                <h2 className="card-title">Certifications (Optional)</h2>
              </div>
              <div className="card-body">
                {formData.certifications.map((cert, index) => (
                  <div key={index} className="inline-array-item">
                    <input
                      type="text"
                      value={cert}
                      onChange={(e) => {
                        const updated = [...formData.certifications];
                        updated[index] = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          certifications: updated,
                        }));
                      }}
                      placeholder="e.g., AWS Certified Developer (2024)"
                      className="form-input"
                    />
                    {formData.certifications.length > 1 && (
                      <button
                        onClick={() => removeArrayItem("certifications", index)}
                        className="remove-button-small"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={() => addArrayItem("certifications", "")}
                  className="add-button-small"
                >
                  + Add Certification
                </button>
              </div>
            </div>

            {/* Achievements Section */}
            <div className="card">
              <div className="card-header">
                <span className="step-number">8</span>
                <h2 className="card-title">Achievements (Optional)</h2>
              </div>
              <div className="card-body">
                {formData.achievements.map((achievement, index) => (
                  <div key={index} className="inline-array-item">
                    <input
                      type="text"
                      value={achievement}
                      onChange={(e) => {
                        const updated = [...formData.achievements];
                        updated[index] = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          achievements: updated,
                        }));
                      }}
                      placeholder="e.g., First Place in Hackathon 2024"
                      className="form-input"
                    />
                    {formData.achievements.length > 1 && (
                      <button
                        onClick={() => removeArrayItem("achievements", index)}
                        className="remove-button-small"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={() => addArrayItem("achievements", "")}
                  className="add-button-small"
                >
                  + Add Achievement
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <div className="action-section centered-action">
              <button
                onClick={handleCreateResume}
                disabled={loading || !formData.name || !formData.email}
                className="create-resume-button"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    <span>Creating Resume...</span>
                  </>
                ) : (
                  <>
                    <span className="button-icon">✨</span>
                    <span>Create Resume</span>
                  </>
                )}
              </button>
            </div>
          </>
        )}

        {/* Features List */}
        <div className="features-list">
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <span>AI-Powered Analysis</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <span>Job-Tailored Content</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚡</span>
            <span>ATS-Friendly Format</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeOptimizer;
