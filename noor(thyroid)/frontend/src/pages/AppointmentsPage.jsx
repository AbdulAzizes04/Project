import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FiCalendar, FiPlus, FiTrash2, FiCheck, FiX, FiClock } from 'react-icons/fi'
import { appointmentsAPI } from '../services/api'
import toast from 'react-hot-toast'

const STATUS_CONFIG = {
  scheduled:  { badge: 'badge-blue',   label: '📅 Scheduled', icon: FiClock },
  completed:  { badge: 'badge-green',  label: '✅ Completed', icon: FiCheck },
  cancelled:  { badge: 'badge-red',    label: '❌ Cancelled', icon: FiX },
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({
    patient_id: '', patient_name: '', doctor_name: '', appointment_date: '', appointment_time: '', reason: ''
  })

  const fetchAll = async () => {
    const res = await appointmentsAPI.list()
    setAppointments(res.data)
    setLoading(false)
  }

  useEffect(() => { fetchAll() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!form.patient_name || !form.doctor_name || !form.appointment_date) {
      toast.error('Please fill all required fields')
      return
    }
    await appointmentsAPI.create(form)
    toast.success('Appointment booked!')
    setShowForm(false)
    setForm({ patient_id: '', patient_name: '', doctor_name: '', appointment_date: '', appointment_time: '', reason: '' })
    fetchAll()
  }

  const updateStatus = async (id, status) => {
    await appointmentsAPI.updateStatus(id, status)
    fetchAll()
    toast.success('Status updated')
  }

  const deleteApt = async (id) => {
    if (!confirm('Delete this appointment?')) return
    await appointmentsAPI.delete(id)
    fetchAll()
    toast.success('Deleted')
  }

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title">Appointments</h1>
          <p className="section-subtitle">{appointments.length} total appointments</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <FiPlus /> Book Appointment
        </button>
      </div>

      {/* Booking Form */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="card border-2 border-primary-200"
        >
          <h3 className="font-bold text-gray-900 mb-4">📅 New Appointment</h3>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Patient Name *</label>
              <input className="input-field" placeholder="Full name" value={form.patient_name} onChange={e => setForm(f => ({ ...f, patient_name: e.target.value }))} required />
            </div>
            <div>
              <label className="label">Patient ID</label>
              <input className="input-field" placeholder="PAT-XXXX" value={form.patient_id} onChange={e => setForm(f => ({ ...f, patient_id: e.target.value }))} />
            </div>
            <div>
              <label className="label">Doctor Name *</label>
              <input className="input-field" placeholder="Dr. Smith" value={form.doctor_name} onChange={e => setForm(f => ({ ...f, doctor_name: e.target.value }))} required />
            </div>
            <div>
              <label className="label">Appointment Date *</label>
              <input type="date" className="input-field" value={form.appointment_date} onChange={e => setForm(f => ({ ...f, appointment_date: e.target.value }))} required min={new Date().toISOString().split('T')[0]} />
            </div>
            <div>
              <label className="label">Time</label>
              <input type="time" className="input-field" value={form.appointment_time} onChange={e => setForm(f => ({ ...f, appointment_time: e.target.value }))} />
            </div>
            <div>
              <label className="label">Reason</label>
              <input className="input-field" placeholder="Reason for visit" value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))} />
            </div>
            <div className="md:col-span-2 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="btn-ghost">Cancel</button>
              <button type="submit" className="btn-primary">Book Appointment</button>
            </div>
          </form>
        </motion.div>
      )}

      {/* Appointments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {loading ? [...Array(6)].map((_, i) => <div key={i} className="card h-36 shimmer" />) :
         appointments.length === 0 ? (
          <div className="col-span-3 text-center py-16 text-gray-400">
            <FiCalendar className="text-5xl mx-auto mb-3 opacity-20" />
            <p>No appointments scheduled</p>
          </div>
         ) : appointments.map((a, i) => {
          const cfg = STATUS_CONFIG[a.status] || STATUS_CONFIG.scheduled
          return (
            <motion.div
              key={a.id}
              initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.04 }}
              className="card card-hover"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="font-bold text-gray-900">{a.patient_name}</p>
                  <p className="text-xs text-gray-400">{a.patient_id}</p>
                </div>
                <span className={`badge ${cfg.badge}`}>{cfg.label}</span>
              </div>
              <div className="space-y-1.5 text-sm text-gray-600 mb-4">
                <p>👨‍⚕️ {a.doctor_name}</p>
                <p>📅 {a.appointment_date} {a.appointment_time && `at ${a.appointment_time}`}</p>
                {a.reason && <p>📝 {a.reason}</p>}
              </div>
              <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
                {a.status === 'scheduled' && (
                  <>
                    <button onClick={() => updateStatus(a.id, 'completed')} className="flex-1 py-1.5 rounded-lg bg-green-50 text-green-600 text-xs font-semibold hover:bg-green-100 transition-colors">
                      ✅ Complete
                    </button>
                    <button onClick={() => updateStatus(a.id, 'cancelled')} className="flex-1 py-1.5 rounded-lg bg-red-50 text-red-500 text-xs font-semibold hover:bg-red-100 transition-colors">
                      ❌ Cancel
                    </button>
                  </>
                )}
                <button onClick={() => deleteApt(a.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-red-400 ml-auto">
                  <FiTrash2 className="text-sm" />
                </button>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
