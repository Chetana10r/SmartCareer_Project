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
            placeholder="Email"
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

          {!isSignup && (
            <a href="/reset-password" style={styles.forgot}>
              Forgot Password?
            </a>
          )}

          <button type="submit" style={styles.button}>
            {isSignup ? "Sign Up" : "Login"}
          </button>
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
    background: "linear-gradient(to right,rgb(25, 43, 77),rgb(1, 18, 49))",
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    fontFamily: "Segoe UI, sans-serif",
    padding: "1rem",
  },
  card: {
    background: "#fff",
    borderRadius: "1rem",
    padding: "2rem",
    boxShadow: "0 10px 30px rgba(3, 1, 23, 0.31)",
    width: "100%",
    maxWidth: "320px",
    textAlign: "center",
  },
  heading: {
    marginBottom: "1rem",
    fontSize: "1.5rem",
    color: "#1e3c72",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
  },
  input: {
    padding: "0.6rem",
    borderRadius: "0.4rem",
    border: "1px solid #ccc",
    fontSize: "0.95rem",
  },
  button: {
    padding: "0.6rem",
    backgroundColor: "#1e3c72",
    color: "#fff",
    border: "none",
    borderRadius: "0.4rem",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "0.95rem",
    marginTop: "0.5rem",
  },
  forgot: {
    textAlign: "right",
    fontSize: "0.8rem",
    color: "#1e3c72",
    textDecoration: "none",
    marginBottom: "0.5rem",
    display: "block",
  },
  toggle: {
    marginTop: "1rem",
    fontSize: "0.85rem",
    color: "#444",
  },
  switchLink: {
    color: "#1e3c72",
    fontWeight: "600",
    cursor: "pointer",
    textDecoration: "underline",
  },
};

export default Login;
