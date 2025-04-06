import React, { useState } from "react";

function Login() {
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const toggleForm = () => {
    setIsSignup(!isSignup);
    setFormData({ name: "", email: "", password: "" });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`${isSignup ? "Signup" : "Login"} successful!`);
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.heading}>{isSignup ? "Create Account" : "Login"}</h2>
        <form onSubmit={handleSubmit} style={styles.form}>
          {isSignup && (
            <input
              style={styles.input}
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Full Name"
              required
            />
          )}
          <input
            style={styles.input}
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email ID"
            required
          />
          <input
            style={styles.input}
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Password"
            required
          />

          <button type="submit" style={styles.button}>
            {isSignup ? "Sign Up" : "Login"}
          </button>

          {!isSignup && (
            <p style={styles.forgot}>
              <a href="/reset-password" className="forgot-password-link">
                Forgot Password?
              </a>
            </p>
          )}
        </form>

        <p style={styles.toggle}>
          {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
          <span onClick={toggleForm} style={styles.switchLink}>
            {isSignup ? "Login" : "Sign Up"}
          </span>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    background: "linear-gradient(to right, #141e30, #243b55)",
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    fontFamily: "Segoe UI, sans-serif",
  },
  card: {
    background: "#fff",
    borderRadius: "1.5rem",
    boxShadow: "0 0 30px rgba(0,0,0,0.2)",
    padding: "3rem 2.5rem",
    width: "100%",
    maxWidth: "400px",
    textAlign: "center",
    marginTop: "80px",
  },
  heading: {
    marginBottom: "1.5rem",
    fontSize: "1.8rem",
    color: "#243b55",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  input: {
    padding: "0.8rem 1rem",
    borderRadius: "0.5rem",
    border: "1px solid #ccc",
    fontSize: "1rem",
  },
  button: {
    padding: "0.8rem",
    backgroundColor: "#243b55",
    color: "white",
    border: "none",
    borderRadius: "0.5rem",
    cursor: "pointer",
    fontWeight: "bold",
    fontSize: "1rem",
    transition: "0.3s",
  },
  forgot: {
    marginTop: "0.5rem",
    fontSize: "0.9rem",
  },
  link: {
    color: "#243b55",
    textDecoration: "none",
    fontWeight: "bold",
  },
  toggle: {
    marginTop: "1.5rem",
    fontSize: "0.95rem",
    color: "#555",
  },
  switchLink: {
    color: "#243b55",
    fontWeight: "bold",
    cursor: "pointer",
    textDecoration: "underline",
  },
};

export default Login;
