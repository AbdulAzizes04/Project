import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import {
  FiUser, FiActivity, FiDroplet, FiHeart, FiUpload,
  FiChevronRight, FiChevronLeft, FiCheck, FiMic, FiMicOff,
  FiAlertCircle, FiFileText
} from 'react-icons/fi'
import { predictionsAPI, ocrAPI } from '../services/api'
import toast from 'react-hot-toast'

const STEPS = [
  { id: 1, label: 'Patient Info',   icon: FiUser },
  { id: 2, label: 'Symptoms',       icon: FiActivity },
  { id: 3, label: 'Hormones',       icon: FiDroplet },
  { id: 4, label: 'Blood Tests',    icon: FiHeart },
  { id: 5, label: 'Medical History',icon: FiAlertCircle },
  { id: 6, label: 'Upload Reports', icon: FiUpload },
]

const SYMPTOMS = [
  { key: 'fatigue',               label: 'Fatigue' },
  { key: 'weight_gain',           label: 'Weight Gain' },
  { key: 'weight_loss',           label: 'Weight Loss' },
  { key: 'hair_loss',             label: 'Hair Loss' },
  { key: 'constipation',          label: 'Constipation' },
  { key: 'anxiety',               label: 'Anxiety' },
  { key: 'depression',            label: 'Depression' },
  { key: 'sweating',              label: 'Sweating' },
  { key: 'neck_swelling',         label: 'Neck Swelling' },
  { key: 'voice_changes',         label: 'Voice Changes' },
  { key: 'cold_intolerance',      label: 'Cold Intolerance' },
  { key: 'heat_intolerance',      label: 'Heat Intolerance' },
  { key: 'difficulty_swallowing', label: 'Difficulty Swallowing' },
  { key: 'sleep_disturbance',     label: 'Sleep Disturbance' },
]

const HISTORY_FIELDS = [
  { key: 'diabetes',       label: 'Diabetes' },
  { key: 'hypertension',   label: 'Hypertension' },
  { key: 'family_history', label: 'Family History of Thyroid Disease' },
  { key: 'smoking',        label: 'Smoking' },
  { key: 'alcohol',        label: 'Alcohol Consumption' },
]

const defaultForm = {
  name: '', age: '', gender: 'Female', weight: '', height: '', bmi: '',
  blood_pressure: '', pulse_rate: '',
  fatigue: 0, weight_gain: 0, weight_loss: 0, hair_loss: 0, constipation: 0,
  anxiety: 0, depression: 0, sweating: 0, neck_swelling: 0, voice_changes: 0,
  cold_intolerance: 0, heat_intolerance: 0, difficulty_swallowing: 0, sleep_disturbance: 0,
  tsh: '', t3: '', t4: '', ft3: '', ft4: '',
  hemoglobin: '', wbc: '', rbc: '', platelets: '', vitamin_d: '', calcium: '',
  diabetes: 0, hypertension: 0, family_history: 0, smoking: 0, alcohol: 0,
  doctor_notes: '',
}

function ToggleButton({ value, onChange, label }) {
  return (
    <button
      type="button"
      onClick={() => onChange(value === 1 ? 0 : 1)}
      className={`
        flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 text-sm font-semibold transition-all duration-150
        ${value === 1
          ? 'bg-primary-600 border-primary-600 text-white shadow-sm'
          : 'border-gray-200 text-gray-600 hover:border-primary-300 hover:bg-primary-50'
        }
      `}
    >
      {value === 1 && <FiCheck className="text-xs" />}
      {label}
    </button>
  )
}

function FormField({ label, hint, children }) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
      {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
    </div>
  )
}

export default function PatientFormPage() {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState(defaultForm)
  const [loading, setLoading] = useState(false)
  const [ocrLoading, setOcrLoading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [listening, setListening] = useState(false)
  const navigate = useNavigate()

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))

  const computeBMI = () => {
    const w = parseFloat(form.weight), h = parseFloat(form.height)
    if (w && h) set('bmi', (w / ((h / 100) ** 2)).toFixed(2))
  }

  const onDrop = useCallback(async (files) => {
    setUploadedFiles(prev => [...prev, ...files])
    if (files[0]) {
      setOcrLoading(true)
      const fd = new FormData()
      fd.append('file', files[0])
      try {
        const res = await ocrAPI.extract(fd)
        const extracted = res.data.extracted_values
        if (Object.keys(extracted).length > 0) {
          setForm(f => ({ ...f, ...Object.fromEntries(Object.entries(extracted).map(([k, v]) => [k, String(v)])) }))
          toast.success(`Extracted ${res.data.fields_found} values from report!`)
        } else {
          toast('No values extracted. Please enter manually.', { icon: '📋' })
        }
      } catch {
        toast.error('OCR extraction failed. Enter values manually.')
      } finally {
        setOcrLoading(false)
      }
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, multiple: true, accept: { 'application/pdf': [], 'image/*': [] } })

  const startVoice = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice input not supported in this browser')
      return
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.continuous = false
    setListening(true)
    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript
      set('name', text)
      toast.success(`Heard: "${text}"`)
    }
    recognition.onend = () => setListening(false)
    recognition.start()
  }

  const handleSubmit = async () => {
    if (!form.name || !form.age) {
      toast.error('Patient name and age are required')
      setStep(1)
      return
    }
    setLoading(true)
    try {
      const payload = {
        ...form,
        age: parseInt(form.age) || 30,
        weight: parseFloat(form.weight) || 70,
        height: parseFloat(form.height) || 170,
        bmi: parseFloat(form.bmi) || 24.2,
        pulse_rate: parseInt(form.pulse_rate) || 72,
        tsh: parseFloat(form.tsh) || 2.5,
        t3: parseFloat(form.t3) || 1.2,
        t4: parseFloat(form.t4) || 100,
        ft3: parseFloat(form.ft3) || 3.5,
        ft4: parseFloat(form.ft4) || 1.2,
        hemoglobin: parseFloat(form.hemoglobin) || 13.5,
        wbc: parseFloat(form.wbc) || 7.0,
        rbc: parseFloat(form.rbc) || 4.5,
        platelets: parseFloat(form.platelets) || 250,
        vitamin_d: parseFloat(form.vitamin_d) || 30,
        calcium: parseFloat(form.calcium) || 9.5,
      }
      const res = await predictionsAPI.predict(payload)
      toast.success('Assessment complete!')
      navigate(`/predictions/${res.data.id}`, { state: { result: res.data } })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const renderStep = () => {
    switch (step) {
      case 1: return (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="Patient Full Name *">
              <div className="relative">
                <input type="text" value={form.name} onChange={e => set('name', e.target.value)} placeholder="Enter full name" className="input-field pr-11" />
                <button type="button" onClick={startVoice} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-gray-100">
                  {listening ? <FiMic className="text-red-500 animate-pulse" /> : <FiMicOff className="text-gray-400" />}
                </button>
              </div>
            </FormField>
            <FormField label="Age *">
              <input type="number" value={form.age} onChange={e => set('age', e.target.value)} placeholder="Age in years" className="input-field" min={1} max={120} />
            </FormField>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FormField label="Gender">
              <select value={form.gender} onChange={e => set('gender', e.target.value)} className="input-field">
                <option>Female</option>
                <option>Male</option>
                <option>Other</option>
              </select>
            </FormField>
            <FormField label="Weight (kg)">
              <input type="number" value={form.weight} onChange={e => { set('weight', e.target.value); setTimeout(computeBMI, 100) }} placeholder="e.g. 65" className="input-field" step="0.1" />
            </FormField>
            <FormField label="Height (cm)">
              <input type="number" value={form.height} onChange={e => { set('height', e.target.value); setTimeout(computeBMI, 100) }} placeholder="e.g. 165" className="input-field" />
            </FormField>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FormField label="BMI" hint="Auto-calculated from weight & height">
              <input type="number" value={form.bmi} onChange={e => set('bmi', e.target.value)} placeholder="e.g. 23.5" className="input-field bg-gray-50" step="0.01" readOnly />
            </FormField>
            <FormField label="Blood Pressure" hint="e.g. 120/80">
              <input type="text" value={form.blood_pressure} onChange={e => set('blood_pressure', e.target.value)} placeholder="120/80" className="input-field" />
            </FormField>
            <FormField label="Pulse Rate (bpm)">
              <input type="number" value={form.pulse_rate} onChange={e => set('pulse_rate', e.target.value)} placeholder="e.g. 72" className="input-field" />
            </FormField>
          </div>
          <FormField label="Doctor Notes (optional)">
            <textarea value={form.doctor_notes} onChange={e => set('doctor_notes', e.target.value)} placeholder="Any additional clinical notes..." className="input-field" rows={3} />
          </FormField>
        </div>
      )
      case 2: return (
        <div>
          <p className="text-sm text-gray-500 mb-4">Select all symptoms the patient is experiencing:</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {SYMPTOMS.map(s => (
              <ToggleButton key={s.key} label={s.label} value={form[s.key]} onChange={v => set(s.key, v)} />
            ))}
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100">
            <p className="text-xs text-blue-700">
              <strong>Selected: </strong>
              {SYMPTOMS.filter(s => form[s.key] === 1).map(s => s.label).join(', ') || 'None'}
            </p>
          </div>
        </div>
      )
      case 3: return (
        <div className="space-y-4">
          <div className="p-4 bg-accent-50 border border-accent-100 rounded-xl mb-2">
            <p className="text-xs text-accent-700 font-medium">📊 Normal Reference Ranges: TSH: 0.4–4.5 mIU/L | T3: 0.8–2.0 nmol/L | T4: 60–120 nmol/L | FT3: 2.3–6.3 pmol/L | FT4: 0.7–1.8 ng/dL</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { key: 'tsh',  label: 'TSH (mIU/L)',   hint: 'Normal: 0.4–4.5',  placeholder: '2.5' },
              { key: 't3',   label: 'T3 (nmol/L)',   hint: 'Normal: 0.8–2.0',  placeholder: '1.2' },
              { key: 't4',   label: 'T4 (nmol/L)',   hint: 'Normal: 60–120',   placeholder: '100' },
              { key: 'ft3',  label: 'FT3 (pmol/L)',  hint: 'Normal: 2.3–6.3',  placeholder: '3.5' },
              { key: 'ft4',  label: 'FT4 (ng/dL)',   hint: 'Normal: 0.7–1.8',  placeholder: '1.2' },
            ].map(f => (
              <FormField key={f.key} label={f.label} hint={f.hint}>
                <input type="number" step="0.01" value={form[f.key]} onChange={e => set(f.key, e.target.value)} placeholder={f.placeholder} className="input-field" />
              </FormField>
            ))}
          </div>
        </div>
      )
      case 4: return (
        <div className="space-y-4">
          <div className="p-4 bg-green-50 border border-green-100 rounded-xl mb-2">
            <p className="text-xs text-green-700 font-medium">🔬 Normal Ranges: Hb: 12–17 g/dL | WBC: 4–11 ×10³/μL | RBC: 3.5–6 ×10⁶/μL | Platelets: 150–400 ×10³/μL | Vit D: 30–80 ng/mL | Calcium: 8.5–10.5 mg/dL</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { key: 'hemoglobin', label: 'Hemoglobin (g/dL)', placeholder: '13.5' },
              { key: 'wbc',        label: 'WBC (×10³/μL)',      placeholder: '7.0'  },
              { key: 'rbc',        label: 'RBC (×10⁶/μL)',      placeholder: '4.5'  },
              { key: 'platelets',  label: 'Platelets (×10³/μL)',placeholder: '250'  },
              { key: 'vitamin_d',  label: 'Vitamin D (ng/mL)',  placeholder: '30'   },
              { key: 'calcium',    label: 'Calcium (mg/dL)',    placeholder: '9.5'  },
            ].map(f => (
              <FormField key={f.key} label={f.label}>
                <input type="number" step="0.1" value={form[f.key]} onChange={e => set(f.key, e.target.value)} placeholder={f.placeholder} className="input-field" />
              </FormField>
            ))}
          </div>
        </div>
      )
      case 5: return (
        <div>
          <p className="text-sm text-gray-500 mb-4">Select all applicable medical history items:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {HISTORY_FIELDS.map(f => (
              <ToggleButton key={f.key} label={f.label} value={form[f.key]} onChange={v => set(f.key, v)} />
            ))}
          </div>
        </div>
      )
      case 6: return (
        <div className="space-y-5">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200
              ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'}
            `}
          >
            <input {...getInputProps()} />
            <FiUpload className="text-4xl text-gray-300 mx-auto mb-3" />
            <p className="font-semibold text-gray-600">Drag & drop medical reports here</p>
            <p className="text-sm text-gray-400 mt-1">or click to browse — PDF, PNG, JPG, TIFF</p>
            <p className="text-xs text-primary-600 mt-2 font-medium">✨ OCR will automatically extract values</p>
          </div>

          {ocrLoading && (
            <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-xl border border-blue-100">
              <div className="w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-blue-700 font-medium">Extracting values from report...</p>
            </div>
          )}

          {uploadedFiles.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-semibold text-gray-700">Uploaded Files:</p>
              {uploadedFiles.map((f, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                  <FiFileText className="text-primary-500" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-700 truncate">{f.name}</p>
                    <p className="text-xs text-gray-400">{(f.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <span className="badge badge-green">Uploaded</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )
      default: return null
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Steps */}
      <div className="flex items-center mb-8 overflow-x-auto pb-2">
        {STEPS.map((s, i) => {
          const Icon = s.icon
          const done = step > s.id
          const active = step === s.id
          return (
            <React.Fragment key={s.id}>
              <button
                onClick={() => done ? setStep(s.id) : null}
                className={`flex flex-col items-center min-w-[80px] ${done ? 'cursor-pointer' : 'cursor-default'}`}
              >
                <div className={`
                  w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all
                  ${done ? 'bg-green-500 text-white' : active ? 'bg-primary-600 text-white ring-4 ring-primary-100' : 'bg-gray-100 text-gray-400'}
                `}>
                  {done ? <FiCheck /> : <Icon />}
                </div>
                <p className={`text-xs mt-1.5 font-medium text-center leading-tight ${active ? 'text-primary-700' : done ? 'text-green-600' : 'text-gray-400'}`}>
                  {s.label}
                </p>
              </button>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-2 mt-[-14px] transition-colors ${done ? 'bg-green-400' : 'bg-gray-200'}`} />
              )}
            </React.Fragment>
          )
        })}
      </div>

      {/* Card */}
      <div className="card">
        <div className="mb-6">
          <h2 className="text-xl font-bold font-display text-gray-900">
            Step {step}: {STEPS[step - 1].label}
          </h2>
          <p className="text-sm text-gray-400">Fill in the patient's information accurately for best prediction results.</p>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {renderStep()}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-100">
          <button
            onClick={() => setStep(s => Math.max(1, s - 1))}
            disabled={step === 1}
            className="btn-outline flex items-center gap-2 disabled:opacity-30"
          >
            <FiChevronLeft /> Previous
          </button>

          <span className="text-sm text-gray-400">Step {step} of {STEPS.length}</span>

          {step < STEPS.length ? (
            <button onClick={() => setStep(s => Math.min(STEPS.length, s + 1))} className="btn-primary flex items-center gap-2">
              Next <FiChevronRight />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="btn-primary flex items-center gap-2 px-8"
            >
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Running AI Analysis...</>
              ) : (
                <><FiActivity /> Run Assessment</>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
