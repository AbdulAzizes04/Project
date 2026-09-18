import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiLock, FiUser, FiEye, FiEyeOff, FiActivity } from 'react-icons/fi'
import { MdOutlineHealthAndSafety } from 'react-icons/md'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/store'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.username || !form.password) {
      toast.error('Please enter username and password')
      return
    }
    setLoading(true)
    try {
      const res = await authAPI.login(form)
      login(res.data.user, res.data.access_token)
      toast.success(`Welcome back, ${res.data.user.full_name || res.data.user.username}!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = () => {
    setForm({ username: 'admin', password: 'admin123' })
    toast('Demo credentials filled!', { icon: '💡' })
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-800 via-primary-700 to-primary-600 relative overflow-hidden flex-col justify-between p-12">
        {/* Decorative circles */}
        <div className="absolute top-[-100px] right-[-100px] w-96 h-96 rounded-full bg-white/5" />
        <div className="absolute bottom-[-80px] left-[-80px] w-80 h-80 rounded-full bg-white/5" />
        <div className="absolute top-1/2 left-1/3 w-48 h-48 rounded-full bg-accent-400/20" />

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-16">
            <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center">
              <MdOutlineHealthAndSafety className="text-white text-2xl" />
            </div>
            <div>
              <h1 className="text-white text-2xl font-bold font-display">ThyroAI</h1>
              <p className="text-white/60 text-sm">Medical Intelligence Platform</p>
            </div>
          </div>

          <h2 className="text-white text-4xl font-bold font-display leading-tight mb-6">
            Patient-Specific<br />Thyroid Risk<br />Assessment
          </h2>
          <p className="text-white/70 text-lg leading-relaxed max-w-sm">
            AI-powered prediction using ensemble machine learning with explainable AI insights for clinical decision support.
          </p>
        </div>

        {/* Feature bullets */}
        <div className="relative z-10 space-y-3">
          {[
            '🤖 5-Model Ensemble ML (RF + XGBoost + LightGBM + SVM + ANN)',
            '🔍 SHAP & LIME Explainable AI',
            '📊 Real-time Analytics Dashboard',
            '📄 Automated PDF Medical Reports',
          ].map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              className="flex items-center gap-3 text-white/80 text-sm"
            >
              <span>{item}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          {/* Mobile logo */}
          <div className="flex items-center gap-3 mb-8 lg:hidden">
            <div className="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center">
              <MdOutlineHealthAndSafety className="text-white text-xl" />
            </div>
            <div>
              <h1 className="text-primary-700 font-bold font-display text-xl">ThyroAI</h1>
              <p className="text-gray-400 text-xs">Medical Intelligence Platform</p>
            </div>
          </div>

          <h2 className="text-3xl font-bold font-display text-gray-900 mb-2">Welcome back</h2>
          <p className="text-gray-500 mb-8">Sign in to your clinical dashboard</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="label">Username</label>
              <div className="relative">
                <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={form.username}
                  onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                  placeholder="Enter your username"
                  className="input-field pl-11"
                  autoComplete="username"
                />
              </div>
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type={showPass ? 'text' : 'password'}
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  placeholder="Enter your password"
                  className="input-field pl-11 pr-11"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(v => !v)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPass ? <FiEyeOff /> : <FiEye />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3 text-base flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <FiActivity />
                  Sign In to ThyroAI
                </>
              )}
            </button>
          </form>

          <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100">
            <p className="text-sm text-blue-700 font-medium mb-2">🔑 Demo Credentials</p>
            <div className="flex items-center justify-between">
              <div className="text-xs text-blue-600">
                <span className="font-mono">admin / admin123</span>
              </div>
              <button onClick={fillDemo} className="text-xs text-primary-600 font-semibold hover:underline">
                Fill Demo
              </button>
            </div>
          </div>

          <p className="text-center text-sm text-gray-400 mt-6">
            © 2024 ThyroAI — Patient-Specific Thyroid Risk Assessment
          </p>
        </motion.div>
      </div>
    </div>
  )
}
