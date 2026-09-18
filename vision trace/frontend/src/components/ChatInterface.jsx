import { useRef, useState, useEffect } from 'react';
import { Send, Bot, User, Zap } from 'lucide-react';
import { sendChat } from '../services/api';

const QUICK_ACTIONS = [
  { label: 'Track 7 Full Summary', q: 'Give me the complete behavioral summary for Track 7' },
  { label: 'Helmet Removal Event', q: 'When was the helmet removal detected?' },
  { label: 'Highest Confidence Match', q: 'Which track has the highest confidence score?' },
  { label: 'Count Persons', q: 'How many persons were detected and tracked?' },
  { label: 'Evidence Timeline', q: 'Show me the full evidence timeline' },
  { label: 'Case Summary', q: 'Give me a summary of the investigation' },
];

export default function ChatInterface({ caseId }) {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content:
        '🤖 **VisionTrace AI Forensic Assistant** online.\n\nI can answer questions about the current investigation — tracked individuals, confidence scores, evidence timeline, and case summary.\n\nTry asking: *"Where did Track 7 first appear?"*',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (question = input) => {
    if (!question.trim() || loading) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const res = await sendChat(question, caseId);
      setMessages((m) => [...m, { role: 'ai', content: res.data.answer, sources: res.data.sources }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'ai', content: '⚠️ Backend connection failed. Please ensure the FastAPI server is running on port 8000.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const renderMarkdown = (text) => {
    // Simple inline markdown renderer
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#e2e8f0">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em style="color:#94a3b8">$1</em>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className="flex flex-col" style={{ height: '100%', gap: 0 }}>
      {/* ── Quick Actions ─────────────────────────────────────────── */}
      <div
        className="flex flex-wrap gap-2 p-4"
        style={{ borderBottom: '1px solid #1a2a4a' }}
      >
        {QUICK_ACTIONS.map((qa) => (
          <button
            key={qa.label}
            onClick={() => send(qa.q)}
            style={{
              background: '#0f1f3d', border: '1px solid #1a2a4a',
              color: '#94a3b8', borderRadius: 20, padding: '5px 12px',
              fontSize: 11, cursor: 'pointer', fontWeight: 500,
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#00d4ff44';
              e.currentTarget.style.color = '#00d4ff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#1a2a4a';
              e.currentTarget.style.color = '#94a3b8';
            }}
          >
            <Zap size={10} style={{ display: 'inline', marginRight: 4 }} />
            {qa.label}
          </button>
        ))}
      </div>

      {/* ── Messages ──────────────────────────────────────────────── */}
      <div
        className="flex-1 overflow-y-auto p-4"
        style={{ display: 'flex', flexDirection: 'column', gap: 12 }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`animate-fade-in ${msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}`}
          >
            <div className="flex items-center gap-2 mb-2">
              {msg.role === 'ai' ? (
                <Bot size={14} color="#00d4ff" />
              ) : (
                <User size={14} color="#94a3b8" />
              )}
              <span style={{ fontSize: 11, color: msg.role === 'ai' ? '#00d4ff' : '#94a3b8', fontWeight: 600 }}>
                {msg.role === 'ai' ? 'AI Forensic Agent' : 'Investigator'}
              </span>
            </div>
            <div
              style={{ fontSize: 13, color: '#e2e8f0', lineHeight: 1.6 }}
              dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
            />
            {msg.sources?.length > 0 && (
              <div style={{ marginTop: 8, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {msg.sources.map((s, si) => (
                  <span
                    key={si}
                    style={{
                      fontSize: 10, color: '#4a5568', background: '#0f1f3d',
                      border: '1px solid #1a2a4a', borderRadius: 10,
                      padding: '2px 8px',
                    }}
                  >
                    📎 {s}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble-ai animate-fade-in">
            <div className="flex items-center gap-2">
              <Bot size={14} color="#00d4ff" />
              <span style={{ fontSize: 11, color: '#00d4ff' }}>Analysing...</span>
            </div>
            <div style={{ display: 'flex', gap: 4, marginTop: 8 }}>
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  style={{
                    width: 6, height: 6, borderRadius: '50%',
                    background: '#00d4ff',
                    animation: `pulse 1.2s ${i * 0.2}s infinite`,
                  }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── Input ─────────────────────────────────────────────────── */}
      <div
        className="p-4"
        style={{ borderTop: '1px solid #1a2a4a', background: '#0a1628' }}
      >
        <div
          className="flex gap-2"
          style={{
            background: '#0f1f3d', border: '1px solid #1a2a4a',
            borderRadius: 10, padding: '8px 12px',
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ask about the investigation..."
            style={{
              flex: 1, background: 'none', border: 'none', outline: 'none',
              color: '#e2e8f0', fontSize: 13,
            }}
          />
          <button
            onClick={() => send()}
            disabled={loading || !input.trim()}
            style={{
              background: input.trim() ? '#00d4ff22' : '#1a2a4a',
              border: `1px solid ${input.trim() ? '#00d4ff44' : '#1a2a4a'}`,
              borderRadius: 8, width: 34, height: 34,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: input.trim() ? 'pointer' : 'not-allowed',
              color: input.trim() ? '#00d4ff' : '#4a5568',
              flexShrink: 0, transition: 'all 0.2s',
            }}
          >
            <Send size={14} />
          </button>
        </div>
        <div style={{ fontSize: 10, color: '#1a2a4a', marginTop: 6, textAlign: 'center' }}>
          Answers grounded in investigation database — no hallucination
        </div>
      </div>
    </div>
  );
}
