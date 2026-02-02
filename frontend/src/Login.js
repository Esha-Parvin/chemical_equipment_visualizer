import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from './api';
import './Login.css';

function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  /* Lock body scroll when login page is mounted */
  useEffect(() => {
    document.documentElement.classList.add('login-page-active');
    document.body.classList.add('login-page-active');
    return () => {
      document.documentElement.classList.remove('login-page-active');
      document.body.classList.remove('login-page-active');
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await authService.login(username, password);
      navigate('/dashboard');
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Invalid username or password');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
        <div className="login-header">
          <h1>🧪</h1>
          <h2>Chemical Equipment Visualizer</h2>
          <p>Sign in to access the dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
            />
          </div>

          {error && <p className="login-error">{error}</p>}

          <button 
            type="submit" 
            className="login-btn"
            disabled={isLoading || !username || !password}
          >
            {isLoading ? '⏳ Signing in...' : '🔐 Sign In'}
          </button>
        </form>

        <p className="login-hint">
          Use your Django admin credentials
        </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
