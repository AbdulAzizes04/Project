import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiSearch, FiPlus, FiTrash2, FiEye, FiEdit } from 'react-icons/fi'
import { patientsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'

export default function PatientListPage() {
  const [patients, setPatients] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const fetchPatients = async (q = '') => {
    setLoading(true)
    try {
      const res = await patientsAPI.list({ search: q, limit: 100 })
      setPatients(res.data)
    } catch {
      toast.error('Failed to load patients')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchPatients() }, [])
  useEffect(() => {
    const t = setTimeout(() => fetchPatients(search), 400)
    return () => clearTimeout(t)
  }, [search])

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete patient ${name}?`)) return
    try {
      await patientsAPI.delete(id)
      toast.success('Patient deleted')
      fetchPatients(search)
    } catch {
      toast.error('Failed to delete patient')
    }
  }

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title">Patients</h1>
          <p className="section-subtitle">{patients.length} registered patients</p>
        </div>
        <button onClick={() => navigate('/patients/new')} className="btn-primary flex items-center gap-2">
          <FiPlus /> Add Patient
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name or patient ID..."
          className="input-field pl-11"
        />
      </div>

      {/* Table */}
      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-3">Patient</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">ID</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Age</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Gender</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">BMI</th>
                <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Registered</th>
                <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i}><td colSpan={7} className="px-6 py-4"><div className="h-5 shimmer rounded" /></td></tr>
                ))
              ) : patients.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center">
                    <div className="text-gray-300 text-5xl mb-3">👤</div>
                    <p className="text-gray-400 text-sm">No patients found</p>
                    <button onClick={() => navigate('/patients/new')} className="btn-primary mt-4 text-sm py-2">
                      Add First Patient
                    </button>
                  </td>
                </tr>
              ) : (
                patients.map((p, i) => (
                  <motion.tr
                    key={p.id}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.02 }}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-sm">
                          {p.name[0]}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-800 text-sm">{p.name}</p>
                          <p className="text-xs text-gray-400">{p.email || p.phone || '—'}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 font-mono text-xs text-gray-500">{p.patient_id}</td>
                    <td className="px-4 py-4 text-sm text-gray-700">{p.age} yrs</td>
                    <td className="px-4 py-4 text-sm text-gray-700">
                      <span className={`badge ${p.gender === 'Female' ? 'badge-orange' : 'badge-blue'}`}>{p.gender}</span>
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-700">{p.bmi?.toFixed(1) || '—'}</td>
                    <td className="px-4 py-4 text-xs text-gray-400">
                      {formatDistanceToNow(new Date(p.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => navigate('/predict', { state: { patient: p } })}
                          className="p-2 rounded-lg hover:bg-primary-50 text-primary-600 transition-colors" title="Assess"
                        >
                          <FiActivity className="text-sm" />
                        </button>
                        <button
                          onClick={() => navigate(`/patients/${p.patient_id}`)}
                          className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors" title="View"
                        >
                          <FiEye className="text-sm" />
                        </button>
                        <button
                          onClick={() => handleDelete(p.patient_id, p.name)}
                          className="p-2 rounded-lg hover:bg-red-50 text-red-400 transition-colors" title="Delete"
                        >
                          <FiTrash2 className="text-sm" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
