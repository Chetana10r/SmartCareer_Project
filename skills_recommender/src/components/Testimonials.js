import React from "react";

function Testimonials() {
  const testimonials = [
    {
      name: "Aarya Deshmukh",
      title: "Software Engineer, TCS",
      quote:
        "SmartCareer helped me identify the exact skills I was missing. It’s like having a personal career coach!",
      rating: 5,
    },
    {
      name: "Rahul Sharma",
      title: "Data Analyst, Infosys",
      quote:
        "The job recommendations and course suggestions are on point! It gave my career the boost I needed.",
      rating: 4,
    },
    {
      name: "Sneha Korde",
      title: "Frontend Developer, Wipro",
      quote:
        "Beautiful interface, accurate predictions. Loved the experience using SmartCareer!",
      rating: 5,
    },
  ];

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>🌟 What Our Users Say</h1>
      <div style={styles.cardRow}>
        {testimonials.map((t, i) => (
          <div key={i} style={styles.card}>
            <div style={styles.quoteMark}>❝</div>
            <p style={styles.quote}>{t.quote}</p>
            <div style={styles.rating}>
              {"⭐".repeat(t.rating)}
              {"☆".repeat(5 - t.rating)}
            </div>
            <h3 style={styles.name}>{t.name}</h3>
            <p style={styles.title}>{t.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: "3rem 2rem",
    background: "linear-gradient(to right, #0f2027, #203a43, #2c5364)",
    color: "white",
    minHeight: "100vh",
    fontFamily: "'Segoe UI', sans-serif",
    textAlign: "center",
  },
  heading: {
    fontSize: "2.0rem",
    marginBottom: "3rem",
    marginTop: "80px",
  },
  cardRow: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "center",
    gap: "1.5rem",
    flexWrap: "nowrap", // ensures they are in a row
    overflowX: "auto", // allows horizontal scrolling if needed
    paddingBottom: "1rem",
  },
  card: {
    background: "white",
    color: "#333",
    borderRadius: "1rem",
    padding: "1.5rem",
    width: "250px",
    minWidth: "250px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
    transition: "transform 0.3s",
    textAlign: "left",
    flexShrink: 0, // prevents shrinking
  },
  quoteMark: {
    fontSize: "2rem",
    color: "#1c92d2",
    marginBottom: "0.5rem",
  },
  quote: {
    fontSize: "0.95rem",
    fontStyle: "italic",
    marginBottom: "1rem",
    lineHeight: "1.6",
  },
  rating: {
    fontSize: "1rem",
    color: "#ffc107",
    marginBottom: "0.5rem",
  },
  name: {
    fontWeight: "bold",
    fontSize: "1.05rem",
    marginBottom: "0.2rem",
  },
  title: {
    fontSize: "0.5rem",
    color: "#666",
  },
};

export default Testimonials;
