import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { TopHeader } from './components/TopHeader';
import { ProtectedRoute } from './components/ProtectedRoute';

// Pages
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { CitizenDashboard } from './pages/CitizenDashboard';
import { ChatbotGrievancePage } from './pages/ChatbotGrievancePage';
import { TrackComplaintPage } from './pages/TrackComplaintPage';
import { ComplaintDetailPage } from './pages/ComplaintDetailPage';
import { AdminDashboard } from './pages/AdminDashboard';
import { AdminComplaints } from './pages/AdminComplaints';
import { AdminDepartments } from './pages/AdminDepartments';
import { AdminUsers } from './pages/AdminUsers';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AIModelEvaluationPage } from './pages/AIModelEvaluationPage';
import { StaffDashboard } from './pages/StaffDashboard';

export function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <AuthProvider>
      <Router>
        <div className="ambient-glow" />
        <div className="app-layout">
          {/* Left Sidebar navigation containing all features */}
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

          <div className="app-main-wrapper">
            {/* Executive Top Header */}
            <TopHeader onToggleSidebar={() => setSidebarOpen(prev => !prev)} />

            {/* Main Content Area */}
            <main className="app-content-area">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Landing />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/track" element={<TrackComplaintPage />} />
                <Route path="/complaints/:id" element={<ComplaintDetailPage />} />

                {/* Citizen Routes */}
                <Route
                  path="/citizen"
                  element={
                    <ProtectedRoute allowedRoles={['citizen']}>
                      <CitizenDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/chat"
                  element={
                    <ProtectedRoute allowedRoles={['citizen', 'admin', 'staff']}>
                      <ChatbotGrievancePage />
                    </ProtectedRoute>
                  }
                />

                {/* Admin Routes */}
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/complaints"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminComplaints />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/departments"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminDepartments />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/users"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminUsers />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/analytics"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AnalyticsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/models"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AIModelEvaluationPage />
                    </ProtectedRoute>
                  }
                />

                {/* Staff Routes */}
                <Route
                  path="/staff"
                  element={
                    <ProtectedRoute allowedRoles={['staff']}>
                      <StaffDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
