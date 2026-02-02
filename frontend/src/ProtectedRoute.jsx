import { Navigate } from 'react-router-dom';

/**
 * ProtectedRoute Component
 * 
 * Checks if user is authenticated by verifying access_token in localStorage.
 * - If token exists → renders children (protected content)
 * - If token missing → redirects to /login
 */
function ProtectedRoute({ children }) {
  const isAuthenticated = !!localStorage.getItem('access_token');

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
