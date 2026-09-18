import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import {
  FiUsers, FiShield, FiDatabase, FiBarChart2, FiTrash2,
  FiDownload, FiPlus, FiUpload, FiAward
} from 'react-icons/fi'
import { adminAPI } from '../services/api'
import { useAuthStore } from '../store/store'
import toast from 'react-hot-toast'

const MODEL_COLORS = ['#2563EB', '#FB923C', '#16A34A', '#7C3AED', '#DC2626', '#0891B2']

function MetricCard({ label, value, color }) {
  return (
    <div className="text-center">
      <div className={`text-2xl font-bold font-display ${color}`}>{(value * 100).toFixed(1)}%</div>
      <div className="text-xs text-gray-500 mt-0.5">{label}</div>
    </div>
  )
}

export default function AdminPage() {
  const [tab, setTab] = useState('analytics')
  const [analytics, setAnalytics] = useState(null)
  const [modelPerf, setModelPerf] = useState(null)
  const [users, setUsers] = useState([])
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '', full_name: '', role: 'doctor' })
  const [showNewUser, setShowNewUser] = useState(false)
  const { user } = useAuthStore()

  useEffect(() => {
    adminAPI.analytics().then(r => setAnalytics(r.data)).catch(() => {})
    adminAPI.modelPerformance().then(r => setModelPerf(r.data)).catch(() => {})
    adminAPI.users().then(r => setUsers(r.data)).catch(() => {})
  }, [])

  const handleDeleteUser = async (id) => {
    if (!confirm('Delete this user?')) return
    await adminAPI.deleteUser(id)
    setUsers(u => u.filter(x => x.id !== id))
    toast.success('User deleted')
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    try {
      const res = await adminAPI.createUser(newUser)
      setUsers(u => [...u, res.data])
      setShowNewUser(false)
      setNewUser({ username: '', email: '', password: '', full_name: '', role: 'doctor' })
      toast.success('User created')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create user')
    }
  }

  const handleDatasetUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    try {
      const res = await adminAPI.uploadDataset(fd)
      toast.success(`Dataset uploaded: ${res.data.rows} rows`)
    } catch {
      toast.error('Upload failed')
    }
  }

  const tabs = [
    { id: 'analytics', label: 'Analytics', icon: FiBarChart2 },
    { id: 'models', label: 'Model Performance', icon: FiAward },
    { id: 'users', label: 'User Management', icon: FiUsers },
    { id: 'dataset', label: 'Dataset', icon: FiDatabase },
  ]

  const conditionBarData = analytics ? Object.entries(analytics.by_condition || {}).map(([name, count]) => ({ name, count })) : []
  const modelBarData = modelPerf ? Object.entries(modelPerf).map(([name, m]) => ({
    name: name.toUpperCase(), accuracy: +(m.accuracy * 100).toFixed(1), f1: +(m.f1 * 100).toFixed(1)
  })) : []

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">Admin Panel</h1>
        <p className="section-subtitle">System administration and analytics</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-100 pb-0">
        {tabs.map(t => {
          const Icon = t.icon
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors -mb-px ${
                tab === t.id ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon /> {t.label}
            </button>
          )
        })}
      </div>

      {/* Analytics Tab */}
      {tab === 'analytics' && (
        <div className="space-y-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Patients',    value: analytics?.total_patients || 0,    icon: FiUsers,    color: 'text-primary-600' },
              { label: 'Total Predictions', value: analytics?.total_predictions || 0, icon: FiBarChart2, color: 'text-accent-500' },
              { label: 'High Risk Cases',   value: analytics?.high_risk || 0,         icon: FiShield,   color: 'text-red-500' },
              { label: 'Avg Confidence',    value: `${analytics?.avg_confidence?.toFixed(1) || 0}%`, icon: FiAward, color: 'text-green-600' },
            ].map(s => (
              <div key={s.label} className="card text-center">
                <s.icon className={`text-2xl mx-auto mb-2 ${s.color}`} />
                <div className="text-3xl font-bold font-display text-gray-900">{s.value}</div>
                <div className="text-xs text-gray-500 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
          <div className="card">
            <h3 className="font-bold text-gray-900 mb-4">Predictions by Condition</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={conditionBarData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {conditionBarData.map((_, i) => <Cell key={i} fill={MODEL_COLORS[i % MODEL_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Model Performance Tab */}
      {tab === 'models' && (
        <div className="space-y-5">
          <div className="card">
            <h3 className="font-bold text-gray-900 mb-4">Model Accuracy & F1 Comparison</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={modelBarData} margin={{ left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[80, 100]} tick={{ fontSize: 11 }} />
                <Tooltip formatter={v => `${v}%`} />
                <Bar dataKey="accuracy" name="Accuracy %" fill="#2563EB" radius={[4, 4, 0, 0]} />
                <Bar dataKey="f1" name="F1 Score %" fill="#FB923C" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {modelPerf && Object.entries(modelPerf).map(([name, m]) => (
              <div key={name} className="card">
                <h4 className="font-bold text-gray-900 mb-4 uppercase">{name === 'ensemble' ? '🏆 Ensemble' : name.toUpperCase()}</h4>
                <div className="grid grid-cols-2 gap-3">
                  <MetricCard label="Accuracy"  value={m.accuracy}  color="text-primary-600" />
                  <MetricCard label="Precision" value={m.precision} color="text-accent-500" />
                  <MetricCard label="Recall"    value={m.recall}    color="text-green-600" />
                  <MetricCard label="F1 Score"  value={m.f1}        color="text-purple-600" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Users Tab */}
      {tab === 'users' && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <button onClick={() => setShowNewUser(!showNewUser)} className="btn-primary flex items-center gap-2">
              <FiPlus /> Add User
            </button>
          </div>
          {showNewUser && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="card border-2 border-primary-200">
              <h3 className="font-bold text-gray-900 mb-4">Create New User</h3>
              <form onSubmit={handleCreateUser} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { key: 'username', label: 'Username *', type: 'text' },
                  { key: 'email', label: 'Email *', type: 'email' },
                  { key: 'full_name', label: 'Full Name', type: 'text' },
                  { key: 'password', label: 'Password *', type: 'password' },
                ].map(f => (
                  <div key={f.key}>
                    <label className="label">{f.label}</label>
                    <input type={f.type} className="input-field" value={newUser[f.key]} onChange={e => setNewUser(u => ({ ...u, [f.key]: e.target.value }))} required={f.label.includes('*')} />
                  </div>
                ))}
                <div>
                  <label className="label">Role</label>
                  <select className="input-field" value={newUser.role} onChange={e => setNewUser(u => ({ ...u, role: e.target.value }))}>
                    <option value="doctor">Doctor</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div className="md:col-span-2 flex gap-3 justify-end">
                  <button type="button" onClick={() => setShowNewUser(false)} className="btn-ghost">Cancel</button>
                  <button type="submit" className="btn-primary">Create User</button>
                </div>
              </form>
            </motion.div>
          )}
          <div className="card p-0 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  {['Name', 'Username', 'Email', 'Role', 'Status', ''].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-5 py-3">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {users.map(u => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="px-5 py-3 font-semibold text-gray-800 text-sm">{u.full_name || '—'}</td>
                    <td className="px-5 py-3 text-sm text-gray-600">{u.username}</td>
                    <td className="px-5 py-3 text-sm text-gray-600">{u.email}</td>
                    <td className="px-5 py-3"><span className={`badge ${u.role === 'admin' ? 'badge-orange' : 'badge-blue'}`}>{u.role}</span></td>
                    <td className="px-5 py-3"><span className={`badge ${u.is_active ? 'badge-green' : 'badge-red'}`}>{u.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td className="px-5 py-3">
                      {u.username !== 'admin' && (
                        <button onClick={() => handleDeleteUser(u.id)} className="p-1.5 rounded hover:bg-red-50 text-red-400"><FiTrash2 className="text-sm" /></button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Dataset Tab */}
      {tab === 'dataset' && (
        <div className="space-y-5">
          <div className="card text-center py-10 border-2 border-dashed border-gray-200">
            <FiDatabase className="text-5xl text-gray-300 mx-auto mb-3" />
            <h3 className="font-bold text-gray-800 mb-2">Upload Training Dataset</h3>
            <p className="text-sm text-gray-400 mb-4">Upload a CSV file to replace or augment the training dataset</p>
            <label className="btn-primary cursor-pointer inline-flex items-center gap-2">
              <FiUpload /> Select CSV File
              <input type="file" accept=".csv" className="hidden" onChange={handleDatasetUpload} />
            </label>
          </div>
          <div className="card">
            <h3 className="font-bold text-gray-900 mb-3">Export Data</h3>
            <div className="flex gap-3">
              <a href="/api/admin/export/predictions" className="btn-outline flex items-center gap-2 text-sm">
                <FiDownload /> Export Predictions CSV
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
