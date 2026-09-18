import React, { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend
} from 'recharts'
import { FiDownload, FiArrowLeft, FiCalendar, FiUser, FiActivity, FiAlertTriangle, FiCheck, FiInfo } from 'react-icons/fi'
import { predictionsAPI, reportsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'

const CONDITION_COLORS = {
  'Healthy': '#16A34A',
  'Hypothyroidism': '#2563EB',
  'Hyperthyroidism': '#FB923C',
  'Thyroid Nodules': '#DC2626'
}

const RISK_CONFIG = {
  High:   { class: 'bg-red-50 border-red-200 text-red-700',    dot: 'bg-red-500',    label: '⚠️ High Risk' },
  Medium: { class: 'bg-yellow-50 border-yellow-200 text-yellow-700', dot: 'bg-yellow-400', label: '⚡ Medium Risk' },
  Low:    { class: 'bg-green-50 border-green-200 text-green-700',  dot: 'bg-green-500',  label: '✅ Low Risk' },
}

function ModelConfidenceBar({ label, value, color }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs font-semibold text-gray-600 w-12 flex-shrink-0">{label}</span>
      <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      <span className="text-xs font-bold text-gray-700 w-12 text-right">{value?.toFixed(1)}%</span>
    </div>
  )
}

export default function PredictionResultPage() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [result, setResult] = useState(location.state?.result || null)
  const [loading, setLoading] = useState(!result)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [reportUrl, setReportUrl] = useState('')

  useEffect(() => {
    if (!result && id) {
      predictionsAPI.get(id).then(r => setResult(r.data)).catch(() => toast.error('Failed to load prediction')).finally(() => setLoading(false))
    }
  }, [id])

  const handleGenerateReport = async () => {
    setGeneratingReport(true)
    try {
      const res = await reportsAPI.generate(result.id)
      setReportUrl(`/reports/${res.data.filename}`)
      toast.success('PDF report generated!')
    } catch {
      toast.error('Failed to generate report')
    } finally {
      setGeneratingReport(false)
    }
  }

  if (loading) return <div className="text-center py-20"><div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto" /></div>
  if (!result) return <div className="text-center py-20 text-gray-400">Prediction not found</div>

  const shap = result.shap_values || {}
  const shapData = Object.entries(shap).sort(([, a], [, b]) => b - a).slice(0, 10).map(([name, value]) => ({ name, value: +(value * 100).toFixed(2) }))
  const limeData = (result.lime_explanation || []).slice(0, 10)
  const mc = result.model_confidences || {}
  const condColor = CONDITION_COLORS[result.predicted_condition] || '#6B7280'
  const riskCfg = RISK_CONFIG[result.risk_level] || RISK_CONFIG.Low

  const modelRadar = [
    { model: 'RF', value: mc.rf || 0 },
    { model: 'XGB', value: mc.xgb || 0 },
    { model: 'LGBM', value: mc.lgbm || 0 },
    { model: 'SVM', value: mc.svm || 0 },
    { model: 'ANN', value: mc.ann || 0 },
  ]

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      {/* Back + Download */}
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="btn-ghost flex items-center gap-2">
          <FiArrowLeft /> Back
        </button>
        <div className="flex items-center gap-3">
          {reportUrl && (
            <a href={reportUrl} download className="btn-outline flex items-center gap-2 py-2">
              <FiDownload /> Download PDF
            </a>
          )}
          <button
            onClick={handleGenerateReport}
            disabled={generatingReport}
            className="btn-primary flex items-center gap-2"
          >
            {generatingReport ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</>
            ) : (
              <><FiDownload /> Generate PDF Report</>
            )}
          </button>
        </div>
      </div>

      {/* Result Hero */}
      <div className="card overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          {/* Condition Badge */}
          <div
            className="w-full md:w-auto flex flex-col items-center justify-center rounded-2xl p-6 min-w-[180px]"
            style={{ backgroundColor: `${condColor}15`, border: `2px solid ${condColor}30` }}
          >
            <div className="w-16 h-16 rounded-full flex items-center justify-center mb-3 text-3xl" style={{ backgroundColor: `${condColor}20` }}>
              {result.predicted_condition === 'Healthy' ? '✅' :
               result.predicted_condition === 'Hypothyroidism' ? '🔵' :
               result.predicted_condition === 'Hyperthyroidism' ? '🟠' : '🔴'}
            </div>
            <h2 className="text-xl font-bold font-display text-center" style={{ color: condColor }}>
              {result.predicted_condition}
            </h2>
            <div className="mt-2">
              <div className="text-3xl font-bold text-gray-900 text-center">{result.confidence?.toFixed(1)}%</div>
              <p className="text-xs text-gray-500 text-center">Confidence</p>
            </div>
          </div>

          <div className="flex-1 space-y-4">
            <div>
              <h1 className="text-2xl font-bold font-display text-gray-900">{result.patient_name}</h1>
              <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                <span className="flex items-center gap-1"><FiUser /> {result.input_data?.age}y, {result.input_data?.gender}</span>
                <span className="flex items-center gap-1"><FiCalendar />
                  {result.created_at ? formatDistanceToNow(new Date(result.created_at), { addSuffix: true }) : ''}
                </span>
                <span className="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">{result.patient_id}</span>
              </div>
            </div>

            {/* Risk badge */}
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl border-2 text-sm font-bold ${riskCfg.class}`}>
              <span className={`w-2.5 h-2.5 rounded-full animate-pulse ${riskCfg.dot}`} />
              {riskCfg.label}
            </div>

            {/* Model confidence bars */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Model Confidences</p>
              <ModelConfidenceBar label="RF"   value={mc.rf}   color="#2563EB" />
              <ModelConfidenceBar label="XGB"  value={mc.xgb}  color="#FB923C" />
              <ModelConfidenceBar label="LGBM" value={mc.lgbm} color="#16A34A" />
              <ModelConfidenceBar label="SVM"  value={mc.svm}  color="#7C3AED" />
              <ModelConfidenceBar label="ANN"  value={mc.ann}  color="#DC2626" />
            </div>
          </div>
        </div>
      </div>

      {/* AI Explanation */}
      <div className="card border-l-4 border-primary-500">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0">
            <FiInfo className="text-primary-600 text-lg" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 mb-2">🤖 AI Clinical Explanation</h3>
            <p className="text-gray-700 leading-relaxed text-sm">{result.natural_language_explanation}</p>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* SHAP Feature Importance */}
        <div className="card">
          <h3 className="font-bold text-gray-900 mb-4">📊 SHAP Feature Importance</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={shapData} layout="vertical" margin={{ left: 80, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10 }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={80} />
              <Tooltip formatter={v => `${v.toFixed(3)}`} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {shapData.map((_, i) => <Cell key={i} fill={i < 3 ? '#2563EB' : i < 6 ? '#FB923C' : '#E5E7EB'} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* LIME Explanation */}
        <div className="card">
          <h3 className="font-bold text-gray-900 mb-4">🔍 LIME Local Explanation</h3>
          <div className="space-y-2 max-h-[280px] overflow-y-auto">
            {limeData.map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${item.impact === 'positive' ? 'bg-green-500' : 'bg-red-400'}`} />
                <span className="text-xs text-gray-600 flex-1 truncate">{item.feature}</span>
                <div className={`text-xs font-bold ${item.impact === 'positive' ? 'text-green-600' : 'text-red-500'}`}>
                  {item.impact === 'positive' ? '+' : ''}{item.weight?.toFixed(3)}
                </div>
                <div className="w-20 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${item.impact === 'positive' ? 'bg-green-400' : 'bg-red-400'}`}
                    style={{ width: `${Math.min(Math.abs(item.weight) * 500, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-3">🟢 Positive = increases prediction | 🔴 Negative = decreases prediction</p>
        </div>
      </div>

      {/* Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {[
          { title: '💊 Treatment Suggestions', items: result.treatment_suggestions, color: 'blue' },
          { title: '🌿 Lifestyle Advice', items: result.lifestyle_advice, color: 'green' },
          { title: '🥗 Diet Recommendations', items: result.diet_recommendations, color: 'orange' },
          { title: '🏃 Exercise Recommendations', items: result.exercise_recommendations, color: 'purple' },
        ].map(({ title, items, color }) => (
          <div key={title} className="card">
            <h3 className="font-bold text-gray-900 mb-3">{title}</h3>
            <ul className="space-y-2">
              {(items || []).map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <FiCheck className={`mt-0.5 flex-shrink-0 text-${color === 'orange' ? 'accent' : color}-500`} />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Follow-up & Referral */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="card border-l-4 border-accent-400">
          <h3 className="font-bold text-gray-900 mb-2">📅 Follow-up Recommendation</h3>
          <p className="text-sm text-gray-700">{result.followup_recommendation}</p>
        </div>
        <div className="card border-l-4 border-purple-400">
          <h3 className="font-bold text-gray-900 mb-2">🏥 Referral Suggestion</h3>
          <p className="text-sm text-gray-700">{result.referral_suggestion}</p>
        </div>
      </div>

      {/* Book Appointment */}
      <div className="card bg-gradient-to-r from-primary-50 to-accent-50 border-primary-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-gray-900">Schedule a Follow-up Appointment</h3>
            <p className="text-sm text-gray-500">Book with a specialist based on the referral above</p>
          </div>
          <button onClick={() => navigate('/appointments')} className="btn-primary flex items-center gap-2">
            <FiCalendar /> Book Appointment
          </button>
        </div>
      </div>
    </div>
  )
}
