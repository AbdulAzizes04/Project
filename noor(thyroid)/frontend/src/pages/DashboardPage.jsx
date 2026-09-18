import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line, Legend,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts'
import {
  FiUsers, FiActivity, FiAlertTriangle, FiFileText,
  FiTrendingUp, FiCalendar, FiArrowRight, FiPlusCircle
} from 'react-icons/fi'
import { adminAPI, predictionsAPI, patientsAPI } from '../services/api'
import { formatDistanceToNow } from 'date-fns'

const COLORS = ['#2563EB', '#FB923C', '#16A34A', '#DC2626']
const CONDITION_COLORS = {
  'Healthy': '#16A34A',
  'Hypothyroidism': '#2563EB',
  'Hyperthyroidism': '#FB923C',
  'Thyroid Nodules': '#DC2626'
}

function StatCard({ icon: Icon, label, value, sub, color, onClick }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      onClick={onClick}
      className={`card cursor-pointer select-none border-l-4 ${color}`}
    >
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-opacity-15 ${color.replace('border-', 'bg-').replace('-500', '-100')}`}>
          <Icon className="text-2xl" />
        </div>
        <div>
          <p className="text-sm text-gray-500 font-medium">{label}</p>
          <p className="text-3xl font-bold font-display text-gray-900">{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        </div>
      </div>
    </motion.div>
  )
}

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState(null)
  const [recentPredictions, setRecentPredictions] = useState([])
  const [modelPerf, setModelPerf] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetch = async () => {
      try {
        const [a, p, m] = await Promise.all([
          adminAPI.analytics(),
          predictionsAPI.list({ limit: 5 }),
          adminAPI.modelPerformance(),
        ])
        setAnalytics(a.data)
        setRecentPredictions(p.data)
        setModelPerf(m.data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  if (loading) return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="card h-28 shimmer" />
      ))}
    </div>
  )

  const conditionData = analytics ? Object.entries(analytics.by_condition || {}).map(([name, value]) => ({ name, value })) : []
  const riskData = [
    { name: 'High Risk', value: analytics?.high_risk || 0, fill: '#DC2626' },
    { name: 'Medium Risk', value: analytics?.medium_risk || 0, fill: '#D97706' },
    { name: 'Low Risk', value: analytics?.low_risk || 0, fill: '#16A34A' },
  ]
  const modelRadarData = modelPerf ? Object.entries(modelPerf).filter(([k]) => k !== 'ensemble').map(([name, m]) => ({
    model: name.toUpperCase(),
    Accuracy: +(m.accuracy * 100).toFixed(1),
    Precision: +(m.precision * 100).toFixed(1),
    F1: +(m.f1 * 100).toFixed(1),
  })) : []

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title">Clinical Dashboard</h1>
          <p className="section-subtitle">Real-time thyroid risk assessment overview</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
          onClick={() => navigate('/predict')}
          className="btn-primary flex items-center gap-2"
        >
          <FiPlusCircle /> New Assessment
        </motion.button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          icon={FiUsers} label="Total Patients" color="border-primary-500"
          value={analytics?.total_patients || 0} sub="Registered"
          onClick={() => navigate('/patients')}
        />
        <StatCard
          icon={FiActivity} label="Total Predictions" color="border-accent-500"
          value={analytics?.total_predictions || 0} sub="AI assessments"
          onClick={() => navigate('/predictions')}
        />
        <StatCard
          icon={FiAlertTriangle} label="High Risk" color="border-red-500"
          value={analytics?.high_risk || 0} sub="Requires attention"
          onClick={() => navigate('/predictions')}
        />
        <StatCard
          icon={FiFileText} label="Today's Reports" color="border-green-500"
          value={analytics?.today || 0} sub="Assessed today"
          onClick={() => navigate('/reports')}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Condition Distribution */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <FiActivity className="text-primary-600" /> Condition Distribution
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={conditionData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}>
                {conditionData.map((entry, i) => (
                  <Cell key={i} fill={CONDITION_COLORS[entry.name] || COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Level */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <FiAlertTriangle className="text-accent-500" /> Risk Distribution
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={riskData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {riskData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Monthly Trend */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <FiTrendingUp className="text-green-500" /> Monthly Trend
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={analytics?.monthly_trend || []} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#2563EB" strokeWidth={2.5} dot={{ fill: '#2563EB', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Model Performance Radar */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-4">Model Performance Radar</h3>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={modelRadarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="model" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[80, 100]} tick={{ fontSize: 10 }} />
              <Radar name="Accuracy" dataKey="Accuracy" stroke="#2563EB" fill="#2563EB" fillOpacity={0.2} />
              <Radar name="F1" dataKey="F1" stroke="#FB923C" fill="#FB923C" fillOpacity={0.2} />
              <Tooltip />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Predictions */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-800">Recent Assessments</h3>
            <button onClick={() => navigate('/predictions')} className="text-sm text-primary-600 hover:underline flex items-center gap-1">
              View All <FiArrowRight />
            </button>
          </div>
          <div className="space-y-2">
            {recentPredictions.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <FiActivity className="text-3xl mx-auto mb-2 opacity-30" />
                <p className="text-sm">No predictions yet</p>
                <button onClick={() => navigate('/predict')} className="btn-primary mt-3 text-sm py-2">
                  Run First Assessment
                </button>
              </div>
            ) : (
              recentPredictions.map(pred => (
                <motion.div
                  key={pred.id}
                  whileHover={{ x: 4 }}
                  onClick={() => navigate(`/predictions/${pred.id}`)}
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-sm">
                    {pred.patient_name[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">{pred.patient_name}</p>
                    <p className="text-xs text-gray-500">{pred.predicted_condition}</p>
                  </div>
                  <div className="text-right">
                    <span className={`badge ${
                      pred.risk_level === 'High' ? 'badge-red' :
                      pred.risk_level === 'Medium' ? 'badge-orange' : 'badge-green'
                    }`}>
                      {pred.risk_level}
                    </span>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {formatDistanceToNow(new Date(pred.created_at), { addSuffix: true })}
                    </p>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Avg Confidence Gauge */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">Average Model Confidence</h3>
            <p className="text-sm text-gray-400">Across all predictions</p>
          </div>
          <div className="text-right">
            <p className="text-4xl font-bold text-primary-600 font-display">
              {analytics?.avg_confidence?.toFixed(1) || '—'}%
            </p>
            <p className="text-sm text-gray-400">avg confidence</p>
          </div>
        </div>
        <div className="mt-4 h-3 bg-gray-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${analytics?.avg_confidence || 0}%` }}
            transition={{ duration: 1, delay: 0.3 }}
            className="h-full bg-gradient-to-r from-primary-500 to-accent-400 rounded-full"
          />
        </div>
      </div>
    </div>
  )
}
