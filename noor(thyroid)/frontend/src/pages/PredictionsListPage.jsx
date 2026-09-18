import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiTrash2, FiEye, FiDownload, FiActivity, FiFilter } from 'react-icons/fi'
import { predictionsAPI, reportsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'

const CONDITION_BADGE = {
  'Healthy':         'badge-green',
  'Hypothyroidism':  'badge-blue',
  'Hyperthyroidism': 'badge-orange',
  'Thyroid Nodules': 'badge-red',
}

export default function PredictionsListPage() {
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [riskFilter, setRiskFilter] = useState('All')
  const navigate = useNavigate()

  useEffect(() => {
    predictionsAPI.list({ limit: 100 })
      .then(r => setPredictions(r.data))
      .catch(() => toast.error('Failed to load predictions'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = riskFilter === 'All' ? predictions : predictions.filter(p => p.risk_level === riskFilter)

  const handleDelete = async (id) => {
    if (!confirm('Delete this prediction?')) return
    await predictionsAPI.delete(id)
    setPredictions(p => p.filter(x => x.id !== id))
    toast.success('Prediction deleted')
  }

  const handleGenerateReport = async (predId) => {
    try {
      const res = await reportsAPI.generate(predId)
      window.open(`/reports/${res.data.filename}`, '_blank')
      toast.success('Report generated!')
    } catch {
      toast.error('Failed to generate report')
    }
  }

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="section-title">Prediction History</h1>
          <p className="section-subtitle">{predictions.length} total assessments</p>
        </div>
        <div className="flex items-center gap-3">
          <a href="/api/admin/export/predictions" className="btn-outline flex items-center gap-2 text-sm py-2">
            <FiDownload /> Export CSV
          </a>
          <button onClick={() => navigate('/predict')} className="btn-primary flex items-center gap-2">
            <FiActivity /> New Assessment
          </button>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2">
        <FiFilter className="text-gray-400" />
        {['All', 'High', 'Medium', 'Low'].map(f => (
          <button key={f} onClick={() => setRiskFilter(f)}
            className={`px-4 py-1.5 rounded-xl text-sm font-semibold transition-all ${
              riskFilter === f ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >{f}</button>
        ))}
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                {['Patient', 'ID', 'Condition', 'Confidence', 'Risk', 'Date', 'Actions'].map(h => (
                  <th key={h} className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-5 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {loading ? [...Array(5)].map((_, i) => (
                <tr key={i}><td colSpan={7} className="px-5 py-4"><div className="h-5 shimmer rounded" /></td></tr>
              )) : filtered.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-12 text-gray-400">No predictions found</td></tr>
              ) : filtered.map((p, i) => (
                <motion.tr key={p.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.02 }}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => navigate(`/predictions/${p.id}`)}
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-xs">
                        {p.patient_name?.[0]}
                      </div>
                      <span className="font-semibold text-gray-800 text-sm">{p.patient_name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3 font-mono text-xs text-gray-500">{p.patient_id}</td>
                  <td className="px-5 py-3">
                    <span className={`badge ${CONDITION_BADGE[p.predicted_condition] || 'badge-blue'}`}>
                      {p.predicted_condition}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-primary-500 rounded-full" style={{ width: `${p.confidence}%` }} />
                      </div>
                      <span className="text-xs font-semibold text-gray-700">{p.confidence?.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <span className={`badge ${p.risk_level === 'High' ? 'badge-red' : p.risk_level === 'Medium' ? 'badge-yellow' : 'badge-green'}`}>
                      {p.risk_level}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-xs text-gray-400">
                    {p.created_at ? formatDistanceToNow(new Date(p.created_at), { addSuffix: true }) : '—'}
                  </td>
                  <td className="px-5 py-3" onClick={e => e.stopPropagation()}>
                    <div className="flex items-center gap-1">
                      <button onClick={() => navigate(`/predictions/${p.id}`)} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500"><FiEye className="text-sm" /></button>
                      <button onClick={() => handleGenerateReport(p.id)} className="p-1.5 rounded-lg hover:bg-blue-50 text-primary-500"><FiDownload className="text-sm" /></button>
                      <button onClick={() => handleDelete(p.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-red-400"><FiTrash2 className="text-sm" /></button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
