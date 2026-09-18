import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { complaintService } from '../services/complaintService';
import { 
  Search, 
  CheckCircle2, 
  Clock, 
  Building, 
  MapPin, 
  AlertCircle, 
  ShieldCheck, 
  User,
  ArrowLeft,
  Camera,
  X
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusTimeline } from '../components/StatusTimeline';

export const TrackComplaintPage = () => {
  const [searchParams] = useSearchParams();
  const [ticketInput, setTicketInput] = useState(searchParams.get('ticket') || '');
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewPhotoModal, setViewPhotoModal] = useState(null);

  const fetchTrackData = async (ticketNo) => {
    if (!ticketNo?.trim()) return;
    setLoading(true);
    setError('');
    setComplaint(null);
    try {
      const data = await complaintService.trackByTicketNumber(ticketNo.trim());
      setComplaint(data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Complaint not found with this ticket number. Please check and try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initialTicket = searchParams.get('ticket');
    if (initialTicket) {
      setTicketInput(initialTicket);
      fetchTrackData(initialTicket);
    }
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchTrackData(ticketInput);
  };

  const steps = ['submitted', 'verified', 'assigned', 'in_progress', 'resolved'];
  const getStepIdx = (status) => {
    if (!status) return 0;
    const s = status.toLowerCase();
    if (s === 'noted') return 2;
    if (s === 'closed') return 4;
    const idx = steps.indexOf(s);
    return idx >= 0 ? idx : 0;
  };
  const currentStepIdx = complaint ? getStepIdx(complaint.status) : 0;

  return (
    <div className="main-content animate-fade-in" style={{ maxWidth: 860 }}>
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Public Grievance Tracker</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Enter your official government ticket number to view live resolution status, assigned officer, and history.
        </p>
      </div>

      {/* Ticket Search Form */}
      <form
        onSubmit={handleSearch}
        style={{
          display: 'flex',
          gap: '0.75rem',
          background: 'var(--bg-surface-elevated)',
          padding: '0.6rem',
          borderRadius: 14,
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-md)',
          marginBottom: '2.5rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', paddingLeft: '0.75rem', color: 'var(--text-muted)' }}>
          <Search size={20} />
        </div>
        <input
          type="text"
          value={ticketInput}
          onChange={(e) => setTicketInput(e.target.value)}
          placeholder="e.g. GRV-2026-0001"
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            color: 'var(--text-primary)',
            fontSize: '1rem',
            fontFamily: 'var(--font-mono)',
            outline: 'none',
          }}
        />
        <button type="submit" disabled={loading || !ticketInput.trim()} className="btn btn-primary">
          {loading ? 'Searching...' : 'Track Ticket'}
        </button>
      </form>

      {error && (
        <div className="glass-card" style={{
          background: '#fef2f2',
          border: '1px solid #fecaca',
          textAlign: 'center',
          padding: '2.5rem 1.5rem',
          color: '#b91c1c',
          marginBottom: '2rem',
        }}>
          <AlertCircle size={36} color="#ef4444" style={{ margin: '0 auto 0.75rem' }} />
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: '#b91c1c' }}>Ticket Not Found</h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{error}</p>
        </div>
      )}

      {complaint && (
        <div className="glass-card animate-fade-in" style={{ padding: '2rem' }}>
          {/* Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '1.5rem',
            marginBottom: '1.5rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}>
            <div>
              <div style={{
                fontFamily: 'var(--font-mono)',
                color: '#38bdf8',
                fontWeight: 700,
                fontSize: '1.1rem',
                marginBottom: 4,
              }}>
                {complaint.ticket_number}
              </div>
              <h2 style={{ fontSize: '1.4rem', marginBottom: 6 }}>{complaint.title}</h2>
              <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem', flexWrap: 'wrap' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Building size={14} />
                  {complaint.category}
                </span>
                {complaint.location && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <MapPin size={14} />
                    {complaint.location}
                  </span>
                )}
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Clock size={14} />
                  Filed on {new Date(complaint.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
              <PriorityBadge priority={complaint.priority} />
              <StatusBadge status={complaint.status} />
            </div>
          </div>

          {/* Stepper Pipeline */}
          <div style={{ margin: '2rem 0', padding: '1rem', background: 'rgba(0,0,0,0.25)', borderRadius: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative' }}>
              {steps.map((step, idx) => {
                const isPassed = idx <= currentStepIdx;
                const isCurrent = idx === currentStepIdx;
                return (
                  <div key={step} style={{ textAlign: 'center', zIndex: 2, flex: 1 }}>
                    <div style={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      margin: '0 auto 8px',
                      background: isPassed ? 'var(--primary-gradient)' : '#e2e8f0',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: isPassed ? '#fff' : 'var(--text-muted)',
                      border: isCurrent ? '2px solid var(--primary-600)' : 'none',
                      boxShadow: isCurrent ? '0 0 10px rgba(37,99,235,0.3)' : 'none',
                    }}>
                      {isPassed ? <CheckCircle2 size={16} /> : idx + 1}
                    </div>
                    <div style={{
                      fontSize: '0.72rem',
                      fontWeight: isCurrent ? 700 : 500,
                      color: isPassed ? 'var(--text-primary)' : 'var(--text-muted)',
                      textTransform: 'capitalize',
                    }}>
                      {step.replace('_', ' ')}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Description & Department */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
            <div style={{ background: 'var(--bg-surface-secondary)', padding: '1.25rem', borderRadius: 12, border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 6 }}>
                GRIEVANCE DESCRIPTION
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                {complaint.description}
              </p>
            </div>

            <div style={{ background: 'var(--bg-surface-secondary)', padding: '1.25rem', borderRadius: 12, border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 6 }}>
                DEPARTMENT & ASSIGNMENT
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.88rem' }}>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>Handling Dept: </span>
                  <strong style={{ color: 'var(--primary-600)' }}>{complaint.department?.name || 'Department of ' + complaint.category}</strong>
                </div>
                {complaint.assigned_to && (
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>Assigned Officer: </span>
                    <span style={{ color: 'var(--text-primary)' }}>{complaint.assigned_to.full_name}</span>
                  </div>
                )}
                {complaint.sla_target_hours && (
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>Target SLA Resolution: </span>
                    <strong style={{ color: '#16a34a' }}>{complaint.sla_target_hours} Hours</strong>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Photo Evidence Card */}
          {complaint.image_url && (
            <div style={{
              background: 'var(--bg-surface-secondary)',
              padding: '1.25rem',
              borderRadius: 12,
              border: '1px solid var(--border-subtle)',
              marginBottom: '2rem',
            }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--primary-600)', fontWeight: 600, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Camera size={15} />
                INCIDENT PHOTO EVIDENCE
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                <img
                  src={complaint.image_url}
                  alt="Grievance evidence"
                  onClick={() => setViewPhotoModal(complaint.image_url)}
                  style={{
                    maxWidth: 280,
                    maxHeight: 180,
                    borderRadius: 10,
                    objectFit: 'cover',
                    border: '1px solid var(--border-subtle)',
                    cursor: 'pointer',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.08)',
                  }}
                />
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  <div>Citizen uploaded photo evidence during intake.</div>
                  <button
                    type="button"
                    onClick={() => setViewPhotoModal(complaint.image_url)}
                    className="btn btn-secondary btn-sm"
                    style={{ marginTop: 8, display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  >
                    <Camera size={13} />
                    View Full Size
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* History Timeline */}
          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1.25rem' }}>Action History & Updates</h3>
            <StatusTimeline history={complaint.status_history} currentStatus={complaint.status} />
          </div>
        </div>
      )}

      {/* Lightbox Photo Preview Modal */}
      {viewPhotoModal && (
        <div 
          onClick={() => setViewPhotoModal(null)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.85)',
            backdropFilter: 'blur(10px)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
          }}
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            style={{ position: 'relative', maxWidth: '90vw', maxHeight: '90vh' }}
          >
            <img 
              src={viewPhotoModal} 
              alt="Grievance evidence full view" 
              style={{
                maxWidth: '100%',
                maxHeight: '80vh',
                borderRadius: 14,
                boxShadow: '0 20px 50px rgba(0,0,0,0.8)',
                border: '1px solid rgba(255,255,255,0.15)',
              }}
            />
            <button
              onClick={() => setViewPhotoModal(null)}
              style={{
                position: 'absolute',
                top: -16,
                right: -16,
                background: '#1e293b',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '50%',
                width: 36,
                height: 36,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
