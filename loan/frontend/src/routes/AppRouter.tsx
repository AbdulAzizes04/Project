import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import { Spinner } from '@/components/ui';

// Pages
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Prediction from '@/pages/Prediction';
import Companies from '@/pages/Companies';
import CompanyDetails from '@/pages/CompanyDetails';
import NetworkAnalysis from '@/pages/NetworkAnalysis';
import TDAAnalysis from '@/pages/TDAAnalysis';
import Models from '@/pages/Models';
import ModelPerformance from '@/pages/ModelPerformance';
import RiskAnalysis from '@/pages/RiskAnalysis';
import PredictionHistory from '@/pages/PredictionHistory';
import DataManagement from '@/pages/DataManagement';
import Explainability from '@/pages/Explainability';
import Settings from '@/pages/Settings';

// ============================================================
// PROTECTED ROUTE
// ============================================================
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Spinner size="lg" />
          <p className="text-sm text-content-secondary">Loading Maritime Risk Intelligence...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <AppLayout>{children}</AppLayout>;
};

// ============================================================
// ROUTER
// ============================================================
const AppRouter: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public */}
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />}
      />

      {/* Protected */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/prediction" element={<ProtectedRoute><Prediction /></ProtectedRoute>} />
      <Route path="/companies" element={<ProtectedRoute><Companies /></ProtectedRoute>} />
      <Route path="/companies/:id" element={<ProtectedRoute><CompanyDetails /></ProtectedRoute>} />
      <Route path="/network-analysis" element={<ProtectedRoute><NetworkAnalysis /></ProtectedRoute>} />
      <Route path="/tda-analysis" element={<ProtectedRoute><TDAAnalysis /></ProtectedRoute>} />
      <Route path="/models" element={<ProtectedRoute><Models /></ProtectedRoute>} />
      <Route path="/model-performance" element={<ProtectedRoute><ModelPerformance /></ProtectedRoute>} />
      <Route path="/risk-analysis" element={<ProtectedRoute><RiskAnalysis /></ProtectedRoute>} />
      <Route path="/predictions/history" element={<ProtectedRoute><PredictionHistory /></ProtectedRoute>} />
      <Route path="/data" element={<ProtectedRoute><DataManagement /></ProtectedRoute>} />
      <Route path="/explainability" element={<ProtectedRoute><Explainability /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default AppRouter;
