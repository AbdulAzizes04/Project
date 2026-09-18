import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { complaintService } from '../services/complaintService';
import { 
  ArrowLeft, 
  Clock, 
  Building, 
  MapPin, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  UserCheck, 
  ShieldAlert,
  Send,
  Camera,
  X
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { AIConfidenceBadge } from '../components/AIConfidenceBadge';
import { StatusTimeline } from '../components/StatusTimeline';

export const ComplaintDetailPage = () => {
  const { id } = useParams();
  const { user, isAdmin, isStaff } = useAuth();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Quick status update for Staff / Admin
  const [newStatus, setNewStatus] = useState('');
  const [remarks, setRemarks] = useState('');
  const [updating, setUpdating] = useState(false);
  const [viewPhotoModal, setViewPhotoModal] = useState(null);

  const loadData = async () => {
    try {
      const data = await complaintService.getComplaintById(id);
      setComplaint(data);
      setNewStatus(data.status);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load complaint details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleStatusUpdate = async (e) => {
    e.preventDefault();
    if (!newStatus || updating) return;
    setUpdating(true);
    try {
      await complaintService.updateStatus(id, newStatus, remarks);
      setRemarks('');
      await loadData();
    } catch (err) {
      alert('Status update failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="main-content" style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading grievance information...
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="main-content" style={{ maxWidth: 600, margin: '3rem auto' }}>
        <div className="glass-card" style={{ textAlign: 'center', padding: '2.5rem' }}>
          <AlertCircle size={36} color="#ef4444" style={{ margin: '0 auto 1rem' }} />
          <h3>Error</h3>
          <p style={{ color: 'var(--text-secondary)', margin: '1rem 0' }}>{error || 'Not found'}</p>
          <button onClick={() => navigate(-1)} className="btn btn-secondary">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="main-content animate-fade-in" style={{ maxWidth: 1100 }}>
      <button 
        onClick={() => navigate(-1)} 
        className="btn btn-secondary btn-sm"
        style={{ marginBottom: '1.5rem' }}
      >
        <ArrowLeft size={16} />
        Back
      </button>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '2rem', alignItems: 'start' }}>
        {/* Left Column: Complaint Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          <div className="glass-card" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#38bdf8', fontSize: '1.1rem' }}>
                  {complaint.ticket_number}
                </span>
                <h1 style={{ fontSize: '1.6rem', marginTop: 4, marginBottom: 8 }}>{complaint.title}</h1>
                <div style={{ display: 'flex', gap: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem', flexWrap: 'wrap' }}>
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
                    Filed {new Date(complaint.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.6rem' }}>
                <PriorityBadge priority={complaint.priority} />
                <StatusBadge status={complaint.status} />
              </div>
            </div>

            <div style={{
              background: 'rgba(0,0,0,0.25)',
              padding: '1.25rem',
              borderRadius: 12,
              border: '1px solid var(--border-subtle)',
              marginBottom: '1.5rem',
            }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 6 }}>
                COMPLAINT DESCRIPTION
              </div>
              <p style={{ fontSize: '0.95rem', lineHeight: 1.6 }}>{complaint.description}</p>
            </div>

            {/* Photo Evidence Card */}
            {complaint.image_url && (
              <div style={{
                background: 'rgba(0,0,0,0.25)',
                padding: '1.25rem',
                borderRadius: 12,
                border: '1px solid var(--border-subtle)',
                marginBottom: '1.5rem',
              }}>
                <div style={{ fontSize: '0.78rem', color: '#0284c7', fontWeight: 600, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Camera size={15} />
                  PHOTO EVIDENCE ATTACHED
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                  <img
                    src={complaint.image_url}
                    alt="Grievance evidence"
                    onClick={() => setViewPhotoModal(complaint.image_url)}
                    style={{
                      maxWidth: 320,
                      maxHeight: 220,
                      borderRadius: 10,
                      objectFit: 'cover',
                      border: '1px solid var(--border-subtle)',
                      cursor: 'pointer',
                      boxShadow: '0 4px 15px rgba(0,0,0,0.08)',
                    }}
                  />
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    <div>Uploaded by citizen during intake.</div>
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

            {/* AI Metadata Box */}
            <div style={{
              background: '#eff6ff',
              border: '1px solid #bfdbfe',
              borderRadius: 14,
              padding: '1.25rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 700, fontSize: '0.9rem', color: '#1e40af' }}>
                  <Sparkles size={16} color="#2563eb" />
                  AI Machine Learning Prediction Record
                </div>
                {complaint.ai_confidence && (
                  <AIConfidenceBadge confidence={complaint.ai_confidence} />
                )}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', fontSize: '0.85rem' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Predicted Category: </span>
                  <strong style={{ color: 'var(--text-primary)' }}>{complaint.predicted_category || complaint.category}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Predicted Priority: </span>
                  <strong style={{ color: 'var(--text-primary)' }}>{complaint.predicted_priority || complaint.priority}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Duplicate Flag: </span>
                  <strong style={{ color: complaint.is_duplicate ? '#dc2626' : '#059669' }}>
                    {complaint.is_duplicate ? 'Yes (Linked)' : 'No duplicate'}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          {/* Action History Timeline Card */}
          <div className="glass-card" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '1.5rem' }}>Lifecycle Timeline</h3>
            <StatusTimeline history={complaint.status_history} currentStatus={complaint.status} />
          </div>
        </div>

        {/* Right Column: Actions & Meta Info */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Staff / Admin Status Action Card */}
          {(isAdmin || isStaff) && (
            <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1rem' }}>
                <ShieldAlert size={18} color="var(--primary-600)" />
                <h3 style={{ fontSize: '1.05rem' }}>Update Grievance Status</h3>
              </div>

              <form onSubmit={handleStatusUpdate}>
                <div className="form-group">
                  <label className="form-label">Next Status</label>
                  <select
                    className="form-select"
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                  >
                    <option value="submitted">Submitted</option>
                    <option value="verified">Verified</option>
                    <option value="assigned">Assigned</option>
                    <option value="noted">Noted (Acknowledged)</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Sorted / Resolved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Action Remarks</label>
                  <textarea
                    rows={3}
                    className="form-textarea"
                    placeholder="Enter resolution notes, technician dispatch details..."
                    value={remarks}
                    onChange={(e) => setRemarks(e.target.value)}
                  />
                </div>

                <button
                  type="submit"
                  disabled={updating}
                  className="btn btn-primary"
                  style={{ width: '100%' }}
                >
                  <Send size={16} />
                  {updating ? 'Updating...' : 'Save Status'}
                </button>
              </form>
            </div>
          )}

          {/* Department Card */}
          <div className="glass-card" style={{ padding: '1.5rem' }}>
            <h4 style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', fontWeight: 600 }}>
              DEPARTMENT DETAILS
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.88rem' }}>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Assigned Department</div>
                <div style={{ fontWeight: 600, color: 'var(--primary-600)', marginTop: 2 }}>
                  {complaint.department?.name || 'Department of ' + complaint.category}
                </div>
              </div>
              {complaint.assigned_to && (
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Assigned Officer</div>
                  <div style={{ fontWeight: 600, marginTop: 2 }}>{complaint.assigned_to.full_name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{complaint.assigned_to.email}</div>
                </div>
              )}
              {complaint.sla_target_hours && (
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Resolution SLA</div>
                  <div style={{ fontWeight: 700, color: '#059669', marginTop: 2 }}>
                    Within {complaint.sla_target_hours} Hours
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

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
