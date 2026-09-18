import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore, useThemeStore } from './store/store'

// Layout
import Layout from './components/Layout'

// Pages
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PatientFormPage from './pages/PatientFormPage'
import PatientListPage from './pages/PatientListPage'
import PredictionsListPage from './pages/PredictionsListPage'
import PredictionResultPage from './pages/PredictionResultPage'
import AppointmentsPage from './pages/AppointmentsPage'
import ReportsPage from './pages/ReportsPage'
import ChatPage from './pages/ChatPage'
import AdminPage from './pages/AdminPage'

function RequireAuth({ children }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function AppLayout({ children }) {
  return (
    <RequireAuth>
      <Layout>{children}</Layout>
    </RequireAuth>
  )
}

export default function App() {
  const { darkMode } = useThemeStore()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            borderRadius: '12px',
            fontFamily: 'Inter, sans-serif',
            fontSize: '14px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
          },
          success: { iconTheme: { primary: '#16A34A', secondary: 'white' } },
          error: { iconTheme: { primary: '#DC2626', secondary: 'white' } },
        }}
      />

      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<AppLayout><DashboardPage /></AppLayout>} />
        <Route path="/predict" element={<AppLayout><PatientFormPage /></AppLayout>} />
        <Route path="/patients" element={<AppLayout><PatientListPage /></AppLayout>} />
        <Route path="/patients/new" element={<AppLayout><PatientFormPage /></AppLayout>} />
        <Route path="/patients/:patientId" element={<AppLayout><PatientListPage /></AppLayout>} />
        <Route path="/predictions" element={<AppLayout><PredictionsListPage /></AppLayout>} />
        <Route path="/predictions/:id" element={<AppLayout><PredictionResultPage /></AppLayout>} />
        <Route path="/appointments" element={<AppLayout><AppointmentsPage /></AppLayout>} />
        <Route path="/reports" element={<AppLayout><ReportsPage /></AppLayout>} />
        <Route path="/chat" element={<AppLayout><ChatPage /></AppLayout>} />
        <Route path="/admin" element={<AppLayout><AdminPage /></AppLayout>} />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
