import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from './api';
import './Login.css';

function Login() {
  const navigate = useNavigate();
  
  /* Mode toggle: false = login, true = signup */
  const [isSignUp, setIsSignUp] = useState(false);
  
  /* Form fields */
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  /* UI state */
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
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

  /* Reset form when switching modes */
  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      if (isSignUp) {
        /* Registration */
        if (password !== confirmPassword) {
          setError('Passwords do not match');
          setIsLoading(false);
          return;
        }
        if (password.length < 8) {
          setError('Password must be at least 8 characters');
          setIsLoading(false);
          return;
        }
        const result = await authService.register(username, password, confirmPassword, email);
        setSuccess(result.message);
        /* Auto-switch to login after 2 seconds */
        setTimeout(() => {
          setIsSignUp(false);
          setPassword('');
          setConfirmPassword('');
          setSuccess('');
        }, 2000);
      } else {
        /* Login */
        await authService.login(username, password);
        navigate('/dashboard');
      }
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Invalid username or password. Don\'t have an account? Sign up first!');
      } else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(isSignUp ? 'Registration failed. Please try again.' : 'Login failed. Please try again.');
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
          <p>{isSignUp ? 'Create your account' : 'Sign in to access the dashboard'}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={isSignUp ? "Choose a username (min 3 chars)" : "Enter your username"}
              required
              autoComplete="username"
              minLength={3}
            />
          </div>

          {isSignUp && (
            <div className="form-group">
              <label htmlFor="email">Email <span className="optional">(optional)</span></label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                autoComplete="email"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isSignUp ? "Create password (min 8 chars)" : "Enter your password"}
              required
              autoComplete={isSignUp ? "new-password" : "current-password"}
              minLength={isSignUp ? 8 : undefined}
            />
          </div>

          {isSignUp && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your password"
                required
                autoComplete="new-password"
              />
            </div>
          )}

          {error && <p className="login-error">{error}</p>}
          {success && <p className="login-success">{success}</p>}

          <button 
            type="submit" 
            className="login-btn"
            disabled={isLoading || !username || !password || (isSignUp && !confirmPassword)}
          >
            {isLoading 
              ? (isSignUp ? '⏳ Creating account...' : '⏳ Signing in...') 
              : (isSignUp ? '📝 Sign Up' : '🔐 Sign In')}
          </button>
        </form>

        <p className="login-toggle">
          {isSignUp ? 'Already have an account?' : "Don't have an account?"}
          <button type="button" className="toggle-btn" onClick={toggleMode}>
            {isSignUp ? 'Sign In' : 'Sign Up'}
          </button>
        </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
