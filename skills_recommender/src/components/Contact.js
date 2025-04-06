import React, { useRef, useState } from "react";
import emailjs from "@emailjs/browser";

function Contact() {
  const formRef = useRef();
  const [done, setDone] = useState(false);

  const sendEmail = (e) => {
    e.preventDefault();

    emailjs
      .sendForm(
        "your_service_id", // replace
        "your_template_id", // replace
        formRef.current,
        "your_public_key" // replace
      )
      .then(
        (result) => {
          console.log(result.text);
          setDone(true);
          formRef.current.reset();
        },
        (error) => {
          console.log(error.text);
        }
      );
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>📬 Get in Touch</h1>
      <p style={styles.subheading}>
        Have a question or feedback? We'd love to hear from you.
      </p>

      <form ref={formRef} onSubmit={sendEmail} style={styles.form}>
        <input
          name="user_name"
          type="text"
          placeholder="Your Name"
          style={styles.input}
          required
        />
        <input
          name="user_email"
          type="email"
          placeholder="Your Email"
          style={styles.input}
          required
        />
        <textarea
          name="message"
          placeholder="Your Message"
          rows="4"
          style={styles.textarea}
          required
        />
        <button type="submit" style={styles.button}>
          Send Message 🚀
        </button>
        {done && (
          <p style={{ color: "green", marginTop: "1rem" }}>
            Message sent successfully!
          </p>
        )}
      </form>

      <div style={styles.socials}>
        <a
          href="https://linkedin.com"
          target="_blank"
          rel="noreferrer"
          style={styles.icon}
        >
          🔗 LinkedIn
        </a>
        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          style={styles.icon}
        >
          💻 GitHub
        </a>
        <a href="mailto:someone@example.com" style={styles.icon}>
          📧 Email
        </a>
      </div>

      <iframe
        title="map"
        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3782.1554517117687!2d73.84294897407498!3d18.562849768349553!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bc2c06f24509c7f%3A0x82f0872097a88013!2sFergusson%20College!5e0!3m2!1sen!2sin!4v1684075587773!5m2!1sen!2sin"
        width="100%"
        height="300"
        style={styles.map}
        allowFullScreen=""
        loading="lazy"
      ></iframe>
    </div>
  );
}

const styles = {
  container: {
    padding: "3rem 2rem",
    minHeight: "100vh",
    fontFamily: "'Segoe UI', sans-serif",
    background: "linear-gradient(to right, #1c92d2, #f2fcfe)",
    color: "#333",
    textAlign: "center",
  },
  heading: {
    fontSize: "2.8rem",
    marginBottom: "0.5rem",
  },
  subheading: {
    fontSize: "1.1rem",
    marginBottom: "2rem",
    maxWidth: "600px",
    margin: "auto",
  },
  form: {
    background: "#fff",
    padding: "2rem",
    borderRadius: "1rem",
    boxShadow: "0 0 20px rgba(0,0,0,0.1)",
    maxWidth: "500px",
    margin: "2rem auto", // 🟢 Add margin-top here
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },

  input: {
    padding: "0.8rem",
    borderRadius: "0.7rem",
    border: "1px solid #ccc",
    fontSize: "1rem",
  },
  textarea: {
    padding: "1rem",
    borderRadius: "0.7rem",
    border: "1px solid #ccc",
    fontSize: "1rem",
    resize: "vertical",
  },
  button: {
    padding: "0.8rem",
    background: "#1c92d2",
    color: "white",
    fontSize: "1rem",
    border: "none",
    borderRadius: "0.7rem",
    cursor: "pointer",
  },
  socials: {
    marginTop: "2rem",
    display: "flex",
    justifyContent: "center",
    gap: "2rem",
    flexWrap: "wrap",
  },
  icon: {
    fontSize: "1.2rem",
    color: "#1c92d2",
    textDecoration: "none",
    fontWeight: "bold",
  },
  map: {
    marginTop: "2rem",
    borderRadius: "1rem",
    border: "none",
    boxShadow: "0 0 15px rgba(0,0,0,0.1)",
  },
};

export default Contact;
