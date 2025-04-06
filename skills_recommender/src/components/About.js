import React from "react";
import aboutImg from "../assets/about.jpg";

function About() {
  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>About SmartCareer</h1>
      <p style={styles.subheading}>
        Empowering your career with AI-driven insights and personalized
        recommendations.
      </p>

      <div style={styles.contentBox}>
        <img src={aboutImg} alt="Career Growth" style={styles.image} />

        <div style={styles.textSection}>
          <h2 style={styles.sectionTitle}>Why SmartCareer?</h2>
          <ul style={styles.list}>
            <li>🔍 Detects your career domain from resume</li>
            <li>🎯 Suggests missing skills & certifications</li>
            <li>💼 Matches you with real-time job opportunities</li>
            <li>📚 Recommends tailored courses to grow faster</li>
          </ul>
          <p style={styles.quote}>
            "Your resume speaks, we listen — and guide your future."
          </p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    background: "linear-gradient(to right, #0f2027, #203a43, #2c5364)",
    color: "white",
    minHeight: "100vh",
    padding: "3rem 2rem",
    fontFamily: "'Segoe UI', sans-serif",
    textAlign: "center",
  },
  heading: {
    fontSize: "2.5rem",
    marginBottom: "0.5rem",
    animation: "fadeInDown 1s ease",
  },
  subheading: {
    fontSize: "1.2rem",
    marginBottom: "2rem",
    color: "#ccc",
  },
  contentBox: {
    display: "flex",
    flexDirection: "row",
    background: "#ffffff10",
    borderRadius: "1.5rem",
    padding: "2rem",
    maxWidth: "1000px",
    margin: "auto",
    boxShadow: "0 0 20px rgba(255,255,255,0.1)",
    gap: "2rem",
    flexWrap: "wrap",
    justifyContent: "center",
    alignItems: "center",
  },
  image: {
    width: "320px",
    borderRadius: "1rem",
    boxShadow: "0 0 15px rgba(0,0,0,0.4)",
  },
  textSection: {
    maxWidth: "500px",
    textAlign: "left",
  },
  sectionTitle: {
    fontSize: "1.8rem",
    marginBottom: "1rem",
    color: "#00e0ff",
  },
  list: {
    listStyle: "none",
    paddingLeft: 0,
    fontSize: "1.1rem",
    lineHeight: "1.8",
  },
  quote: {
    marginTop: "1.5rem",
    fontStyle: "italic",
    color: "#ccc",
  },
};

export default About;
