import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Bot, 
  Search, 
  Sparkles, 
  ShieldCheck, 
  ArrowRight, 
  Layers, 
  Clock, 
  TrendingUp, 
  Cpu, 
  Building2,
  CheckCircle2,
  Activity
} from 'lucide-react';

export const Landing = () => {
  const [ticketInput, setTicketInput] = useState('');
  const navigate = useNavigate();

  const handleTrackSubmit = (e) => {
    e.preventDefault();
    if (ticketInput.trim()) {
      navigate(`/track?ticket=${ticketInput.trim()}`);
    }
  };

  const departments = [
    { name: 'Water Supply & Sewerage', code: 'WATER', cat: 'Water Supply', color: '#38bdf8' },
    { name: 'Roads & Infrastructure', code: 'ROADS', cat: 'Roads', color: '#f59e0b' },
    { name: 'Solid Waste & Sanitation', code: 'SWM', cat: 'Sanitation', color: '#10b981' },
    { name: 'Electricity Board', code: 'ELEC', cat: 'Electricity', color: '#818cf8' },
    { name: 'Street Lighting Div.', code: 'LIGHTS', cat: 'Street Lighting', color: '#fbbf24' },
    { name: 'Drainage & Stormwater', code: 'DRAIN', cat: 'Drainage', color: '#06b6d4' },
  ];

  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <section style={{
        padding: '4.5rem 1.5rem 3.5rem',
        textAlign: 'center',
        maxWidth: 1000,
        margin: '0 auto',
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          background: 'rgba(99, 102, 241, 0.12)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          padding: '0.4rem 1rem',
          borderRadius: 30,
          fontSize: '0.85rem',
          color: '#c7d2fe',
          marginBottom: '1.5rem',
        }}>
          <Sparkles size={16} color="#818cf8" />
          <span>Next-Generation e-Governance AI Redressal Portal</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(2.3rem, 5vw, 3.8rem)',
          lineHeight: 1.15,
          fontWeight: 800,
          letterSpacing: '-0.03em',
          marginBottom: '1.25rem',
        }}>
          Automated Public Grievance Redressal Powered by <span style={{
            background: 'var(--primary-gradient)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>Intelligent AI</span>
        </h1>

        <p style={{
          fontSize: '1.15rem',
          color: 'var(--text-secondary)',
          maxWidth: 720,
          margin: '0 auto 2.5rem',
          lineHeight: 1.6,
        }}>
          Lodge public grievances with conversational AI. Automatic NLP category classification, 
          urgency priority scoring, semantic duplicate detection, and automated department routing.
        </p>

        {/* Live Complaint Search Bar */}
        <form 
          onSubmit={handleTrackSubmit}
          style={{
            maxWidth: 620,
            margin: '0 auto 2rem',
            display: 'flex',
            gap: '0.75rem',
            background: 'var(--bg-surface-elevated)',
            padding: '0.5rem',
            borderRadius: 14,
            border: '1px solid var(--border-subtle)',
            boxShadow: 'var(--shadow-lg)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', paddingLeft: '0.75rem', color: 'var(--text-muted)' }}>
            <Search size={20} />
          </div>
          <input
            type="text"
            value={ticketInput}
            onChange={(e) => setTicketInput(e.target.value)}
            placeholder="Enter Ticket Number (e.g. GRV-2026-0001)"
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              fontSize: '0.95rem',
              outline: 'none',
            }}
          />
          <button type="submit" className="btn btn-primary" style={{ padding: '0.6rem 1.4rem' }}>
            Track Status
          </button>
        </form>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/chat" className="btn btn-accent" style={{ fontSize: '1rem', padding: '0.8rem 1.8rem' }}>
            <Bot size={18} />
            Lodge Grievance with AI Chatbot
          </Link>
          <Link to="/login" className="btn btn-secondary" style={{ fontSize: '1rem', padding: '0.8rem 1.6rem' }}>
            Portal Sign In
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section style={{ maxWidth: 1200, margin: '2rem auto 4rem', padding: '0 1.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.85rem', marginBottom: '0.5rem' }}>AI Redressal Engine Architecture</h2>
          <p style={{ color: 'var(--text-secondary)' }}>End-to-end automated pipeline from natural citizen text to departmental action</p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem',
        }}>
          <div className="glass-card glass-card-interactive">
            <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(79, 70, 229, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818cf8', marginBottom: '1.25rem' }}>
              <Bot size={24} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Conversational Agent</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              State machine dialogue extracts complaint details, address, landmark, and duration naturally without complex multi-page government forms.
            </p>
          </div>

          <div className="glass-card glass-card-interactive">
            <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#06b6d4', marginBottom: '1.25rem' }}>
              <Cpu size={24} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>NLP Text Classification</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Calibrated LinearSVC model trained on 1,200+ domain records classifies grievances into 6 departments with over 90% weighted F1 accuracy.
            </p>
          </div>

          <div className="glass-card glass-card-interactive">
            <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f59e0b', marginBottom: '1.25rem' }}>
              <TrendingUp size={24} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Priority & SLA Engine</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Gradient Boosting classifier predicts Low / Medium / High / Critical priority dynamically, triggering automated SLA timers from 12 to 168 hours.
            </p>
          </div>

          <div className="glass-card glass-card-interactive">
            <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#10b981', marginBottom: '1.25rem' }}>
              <Layers size={24} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Semantic Duplicate Detection</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Cosine similarity vector search flags identical complaints in the same locality, preventing duplicate work orders and server overload.
            </p>
          </div>
        </div>
      </section>

      {/* Departments Covered */}
      <section style={{ maxWidth: 1200, margin: '0 auto 4rem', padding: '0 1.5rem' }}>
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 20,
          padding: '2.5rem 2rem',
        }}>
          <h3 style={{ fontSize: '1.4rem', marginBottom: '1.5rem', textAlign: 'center' }}>
            Connected Municipal Departments
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}>
            {departments.map((d) => (
              <div
                key={d.code}
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 12,
                  padding: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                }}
              >
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: d.color }} />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{d.name}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Code: {d.code}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Credentials Quick-Launch Banner */}
      <section style={{ maxWidth: 1000, margin: '0 auto 5rem', padding: '0 1.5rem' }}>
        <div className="glass-card" style={{ border: '1px solid #bfdbfe', background: 'linear-gradient(135deg, #eff6ff 0%, #ffffff 100%)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '0.75rem' }}>
            <Activity size={20} color="var(--primary-600)" />
            <h4 style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>Academic Evaluation & Viva Quick Access</h4>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Use the pre-configured accounts below or visit the Sign In page for one-click instant authentication:
          </p>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <div style={{ background: '#ffffff', padding: '0.75rem 1rem', borderRadius: 10, flex: 1, minWidth: 220, border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--primary-700)', fontWeight: 700 }}>ADMINISTRATOR / TPO</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: 4, color: 'var(--text-primary)' }}>admin@gov.in</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Admin@123</div>
            </div>
            <div style={{ background: '#ffffff', padding: '0.75rem 1rem', borderRadius: 10, flex: 1, minWidth: 220, border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 700 }}>STAFF / FIELD OFFICER</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: 4, color: 'var(--text-primary)' }}>staff.water@gov.in</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Staff@123</div>
            </div>
            <div style={{ background: '#ffffff', padding: '0.75rem 1rem', borderRadius: 10, flex: 1, minWidth: 220, border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ fontSize: '0.75rem', color: '#d97706', fontWeight: 700 }}>CITIZEN USER</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: 4, color: 'var(--text-primary)' }}>ramesh.sharma@gmail.com</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Citizen@123</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
