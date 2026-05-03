import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import UnifiedInputPage from './pages/UnifiedInputPage';
import ResultPage from './pages/ResultPage';
import SuggestionsPage from './pages/SuggestionsPage';
import HistoryPage from './pages/HistoryPage';
import AuthPage from './pages/AuthPage';
import AuthCallback from './pages/AuthCallback';
import ProfileResultPage from './pages/ProfileResultPage';
import TipsPage from './pages/TipsPage';
import DateCalculatorPage from './pages/DateCalculatorPage';


import { AuthProvider, useAuth } from './AuthContext';
import { useLocation, Navigate } from 'react-router-dom';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  if (loading) return null; // Wait for auth state to resolve before redirecting
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" state={{ from: location }} replace />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route path="/analyze" element={<ProtectedRoute><UnifiedInputPage /></ProtectedRoute>} />
            <Route path="/result" element={<ProtectedRoute><ResultPage /></ProtectedRoute>} />
            <Route path="/suggestions" element={<ProtectedRoute><SuggestionsPage /></ProtectedRoute>} />
            <Route path="/history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
            <Route path="/profile-result" element={<ProtectedRoute><ProfileResultPage /></ProtectedRoute>} />
            <Route path="/tips" element={<ProtectedRoute><TipsPage /></ProtectedRoute>} />
            <Route path="/date-calculator" element={<ProtectedRoute><DateCalculatorPage /></ProtectedRoute>} />


          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
