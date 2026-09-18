import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FiDownload, FiFileText } from 'react-icons/fi'
import { reportsAPI } from '../services/api'
import { formatDistanceToNow } from 'date-fns'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    reportsAPI.list().then(r => setReports(r.data)).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">Reports</h1>
        <p className="section-subtitle">{reports.length} generated PDF reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {loading ? [...Array(6)].map((_, i) => <div key={i} className="card h-28 shimmer" />) :
         reports.length === 0 ? (
          <div className="col-span-3 text-center py-16 text-gray-400">
            <FiFileText className="text-5xl mx-auto mb-3 opacity-20" />
            <p>No reports generated yet</p>
            <p className="text-xs mt-1">Generate a report from a prediction result</p>
          </div>
         ) : reports.map((r, i) => (
          <motion.div key={r.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
            className="card card-hover flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
              <FiFileText className="text-red-500 text-xl" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-800 text-sm truncate">{r.patient_name}</p>
              <p className="text-xs text-gray-400">{r.patient_id}</p>
              <p className="text-xs text-gray-400 mt-0.5">
                {formatDistanceToNow(new Date(r.created_at), { addSuffix: true })}
              </p>
            </div>
            <a href={`/reports/${r.filename}`} download
              className="p-2 rounded-xl bg-primary-50 text-primary-600 hover:bg-primary-100 transition-colors">
              <FiDownload />
            </a>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
