import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiSend, FiMessageSquare, FiTrash2, FiMic } from 'react-icons/fi'
import { MdOutlineHealthAndSafety } from 'react-icons/md'

const SYSTEM_RESPONSES = {
  'tsh': 'TSH (Thyroid-Stimulating Hormone) is produced by the pituitary gland. Normal range: 0.4–4.5 mIU/L. High TSH suggests hypothyroidism; low TSH suggests hyperthyroidism.',
  'hypothyroidism': 'Hypothyroidism occurs when the thyroid gland doesn\'t produce enough thyroid hormones. Symptoms include fatigue, weight gain, cold intolerance, constipation, and depression. Treated with Levothyroxine.',
  'hyperthyroidism': 'Hyperthyroidism is overproduction of thyroid hormones. Symptoms include weight loss, anxiety, heat intolerance, sweating, and rapid heartbeat. Treatment includes anti-thyroid medications or radioiodine therapy.',
  'thyroid nodules': 'Thyroid nodules are lumps in the thyroid gland. Most are benign, but FNA biopsy is recommended for nodules >1cm. Symptoms include neck swelling and difficulty swallowing.',
  'shap': 'SHAP (SHapley Additive exPlanations) is an explainable AI technique that shows how much each feature contributes to a specific prediction. Higher SHAP values = stronger influence on the result.',
  'lime': 'LIME (Local Interpretable Model-agnostic Explanations) explains individual predictions by approximating the model locally with a simpler, interpretable model.',
  'diet': 'For thyroid health: Ensure adequate iodine (iodized salt), selenium (Brazil nuts, tuna), zinc, and Vitamin D. Avoid excess raw goitrogenic foods (broccoli, cabbage, soy) for hypothyroidism.',
  'exercise': 'For thyroid patients: Low-impact aerobic exercise (walking, swimming) is generally safe. For hypothyroidism: 30 min walking 5x/week. For hyperthyroidism: Avoid strenuous activity until controlled.',
  'bmi': 'BMI (Body Mass Index) = Weight(kg) / Height(m)². Normal: 18.5–24.9 | Overweight: 25–29.9 | Obese: ≥30. BMI can be affected by thyroid disorders — hypothyroidism often causes weight gain.',
  'ft4': 'Free T4 (FT4) is the unbound, active form of thyroxine. Normal: 0.7–1.8 ng/dL. Low FT4 with high TSH = Hypothyroidism. High FT4 with low TSH = Hyperthyroidism.',
}

const QUICK_QUESTIONS = [
  'What is TSH?',
  'What is hypothyroidism?',
  'What is hyperthyroidism?',
  'Tell me about thyroid nodules',
  'How does SHAP work?',
  'What diet is good for thyroid?',
]

function getResponse(input) {
  const lower = input.toLowerCase()
  for (const [key, response] of Object.entries(SYSTEM_RESPONSES)) {
    if (lower.includes(key)) return response
  }
  if (lower.includes('hello') || lower.includes('hi')) return 'Hello! I\'m ThyroAI Assistant. I can answer questions about thyroid conditions, hormone values, symptoms, and how the AI model works. How can I help you?'
  if (lower.includes('help')) return 'I can help you with: TSH/T3/T4 explanations, thyroid conditions, symptoms, diet & exercise recommendations, SHAP/LIME explainability, and more. What would you like to know?'
  if (lower.includes('risk')) return 'Risk levels in ThyroAI: 🔴 HIGH (>80% confidence) — urgent clinical evaluation needed. 🟡 MEDIUM (60–79%) — follow-up recommended. 🟢 LOW (<60%) — routine monitoring.'
  return 'I specialize in thyroid health and the ThyroAI platform. Try asking about TSH, T3/T4, hypothyroidism, hyperthyroidism, thyroid nodules, SHAP/LIME explanations, diet, or exercise recommendations!'
}

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: '👋 Hello! I\'m ThyroAI Assistant. I can answer questions about thyroid conditions, hormone values, AI model explanations, and health recommendations. How can I help you today?', time: new Date() }
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, typing])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg) return
    setInput('')
    const userMsg = { id: Date.now(), role: 'user', text: msg, time: new Date() }
    setMessages(m => [...m, userMsg])
    setTyping(true)
    await new Promise(r => setTimeout(r, 700 + Math.random() * 500))
    const response = getResponse(msg)
    setMessages(m => [...m, { id: Date.now() + 1, role: 'assistant', text: response, time: new Date() }])
    setTyping(false)
  }

  const handleKeyDown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }

  const clearChat = () => setMessages([{ id: 1, role: 'assistant', text: 'Chat cleared! How can I help you?', time: new Date() }])

  return (
    <div className="max-w-3xl mx-auto space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title">AI Assistant</h1>
          <p className="section-subtitle">Ask about thyroid conditions, hormone values, or how ThyroAI works</p>
        </div>
        <button onClick={clearChat} className="btn-ghost flex items-center gap-2 text-sm">
          <FiTrash2 /> Clear Chat
        </button>
      </div>

      {/* Quick Questions */}
      <div className="flex flex-wrap gap-2">
        {QUICK_QUESTIONS.map(q => (
          <button key={q} onClick={() => sendMessage(q)}
            className="px-3 py-1.5 bg-primary-50 text-primary-700 text-xs font-medium rounded-xl hover:bg-primary-100 transition-colors border border-primary-100">
            {q}
          </button>
        ))}
      </div>

      {/* Chat messages */}
      <div className="card p-4 h-[500px] overflow-y-auto space-y-4">
        <AnimatePresence>
          {messages.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold ${
                msg.role === 'assistant' ? 'bg-primary-600 text-white' : 'bg-accent-400 text-white'
              }`}>
                {msg.role === 'assistant' ? <MdOutlineHealthAndSafety /> : '👤'}
              </div>
              {/* Bubble */}
              <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white rounded-tr-sm'
                  : 'bg-gray-100 text-gray-800 rounded-tl-sm'
              }`}>
                {msg.text}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {typing && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3 items-center">
            <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
              <MdOutlineHealthAndSafety className="text-white text-sm" />
            </div>
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-tl-sm">
              <div className="flex gap-1.5">
                {[0, 1, 2].map(i => (
                  <div key={i} className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about thyroid conditions, hormone values, SHAP explanations..."
            className="input-field resize-none pr-4 min-h-[52px] max-h-[120px]"
            rows={1}
          />
        </div>
        <button onClick={() => sendMessage()} disabled={!input.trim()}
          className="btn-primary px-5 self-end h-[52px] disabled:opacity-40">
          <FiSend />
        </button>
      </div>
      <p className="text-xs text-gray-400 text-center">⚠️ ThyroAI Assistant provides general information only. Always consult a qualified medical professional.</p>
    </div>
  )
}
