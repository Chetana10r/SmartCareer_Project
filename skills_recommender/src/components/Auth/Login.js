import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    // Basic validation
    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    // In a real app, you'd verify credentials with your backend here
    // Example: axios.post('/api/auth/login', { email, password })

    // Retrieve role from localStorage (set in RoleSelection.js)
    const userRole = localStorage.getItem("userRole");

    if (userRole === "recruiter") {
      navigate("/recruiter-dashboard");
    } else if (userRole === "candidate") {
      navigate("/");
    } else {
      setError("Please select a role first");
      navigate("/role-selection");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="login-title">SmartCareer Login</h1>
        <p className="login-subtitle">Welcome back! Please log in to continue</p>

        {error && <p className="error-msg">{error}</p>}

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" className="login-btn">
            Login
          </button>
        </form>

        <div className="role-reminder">
          <p>
            Not sure of your role?{" "}
            <span
              className="select-role-link"
              onClick={() => navigate("/role-selection")}
            >
              Choose here
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
