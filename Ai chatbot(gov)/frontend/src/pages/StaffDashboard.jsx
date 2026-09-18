import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminService } from '../services/adminService';
import { complaintService } from '../services/complaintService';
import { 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  ArrowUpRight, 
  MapPin, 
  FileText,
  X,
  Send,
  Camera,
  Layers,
  CheckCircle,
  ClipboardList
} from 'lucide-react';
import { StatsCard } from '../components/StatsCard';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';

export const StaffDashboard = () => {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [viewScope, setViewScope] = useState('my'); // 'my' | 'dept'

  // Status update modal
  const [activeComplaint, setActiveComplaint] = useState(null);
  const [nextStatus, setNextStatus] = useState('noted'); // 'noted' | 'in_progress' | 'resolved'
  const [remarks, setRemarks] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Lightbox photo viewer
  const [viewPhotoUrl, setViewPhotoUrl] = useState(null);

  const loadAssignedComplaints = async () => {
    setLoading(true);
    try {
      const params = {
        status: statusFilter || undefined,
      };
      if (viewScope === 'my' && user?.id) {
        params.assigned_to_id = user.id;
      }

      const res = await adminService.listAllComplaints(params);
      setComplaints(res.items || res.complaints || res || []);
    } catch (err) {
      console.error('Error fetching complaints for staff desk:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssignedComplaints();
  }, [user, statusFilter, viewScope]);

  const handleOpenStatusModal = (complaint) => {
    setActiveComplaint(complaint);
    // Suggest logical next status
    if (complaint.status === 'assigned') {
      setNextStatus('noted');
      setRemarks('Work order noted and site inspection scheduled by field officer.');
    } else if (complaint.status === 'noted') {
      setNextStatus('in_progress');
      setRemarks('Field crew deployed on site with repair machinery and materials.');
    } else {
      setNextStatus('resolved');
      setRemarks('Grievance issue has been fully addressed, repaired, and sorted.');
    }
  };

  const handleQuickStatusSelect = (statusKey) => {
    setNextStatus(statusKey);
    if (statusKey === 'noted') {
      setRemarks('Work order noted and site inspection scheduled by field officer.');
    } else if (statusKey === 'in_progress') {
      setRemarks('Field crew deployed on site with repair machinery and materials.');
    } else if (statusKey === 'resolved') {
      setRemarks('Grievance issue has been fully addressed, repaired, and sorted on site.');
    }
  };

  const handleUpdateStatus = async (e) => {
    e.preventDefault();
    if (!activeComplaint || submitting) return;
    setSubmitting(true);
    try {
      await complaintService.updateStatus(activeComplaint.id, nextStatus, remarks);
      setActiveComplaint(null);
      await loadAssignedComplaints();
    } catch (err) {
      alert('Status update failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const total = complaints.length;
  const notedCount = complaints.filter(c => c.status === 'noted').length;
  const inProgress = complaints.filter(c => c.status === 'in_progress').length;
  const resolved = complaints.filter(c => ['resolved', 'closed'].includes(c.status)).length;

  return (
    <div className="main-content animate-fade-in">
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', display: 'flex', alignItems: 'center', gap: 10 }}>
            <ShieldAlert size={28} color="#818cf8" />
            Field Officer Operations Desk
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Welcome, <strong>{user?.full_name}</strong>. Manage your municipal work orders with live citizen status updates.
          </p>
        </div>

        {/* Scope Switcher Tabs */}
        <div style={{
          display: 'flex',
          background: 'var(--bg-subtle)',
          padding: '4px',
          borderRadius: 12,
          border: '1px solid var(--border-subtle)',
          gap: 4,
        }}>
          <button
            onClick={() => setViewScope('my')}
            style={{
              padding: '0.45rem 0.9rem',
              borderRadius: 8,
              border: 'none',
              background: viewScope === 'my' ? 'var(--primary-gradient)' : 'transparent',
              color: viewScope === 'my' ? '#fff' : 'var(--text-secondary)',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'var(--transition-fast)',
            }}
          >
            <ClipboardList size={15} />
            My Work Orders
          </button>
          <button
            onClick={() => setViewScope('dept')}
            style={{
              padding: '0.45rem 0.9rem',
              borderRadius: 8,
              border: 'none',
              background: viewScope === 'dept' ? 'var(--primary-gradient)' : 'transparent',
              color: viewScope === 'dept' ? '#fff' : 'var(--text-secondary)',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'var(--transition-fast)',
            }}
          >
            <Layers size={15} />
            Department Queue
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <StatsCard
          title="Total in View"
          value={total}
          icon={FileText}
          color="#818cf8"
          subtitle={viewScope === 'my' ? "Assigned to you" : "Department active orders"}
        />
        <StatsCard
          title="Noted / Acknowledged"
          value={notedCount}
          icon={ClipboardList}
          color="#22d3ee"
          subtitle="Site inspected & noted"
        />
        <StatsCard
          title="Active Field Work"
          value={inProgress}
          icon={AlertTriangle}
          color="#f59e0b"
          subtitle="Repair work in progress"
        />
        <StatsCard
          title="Sorted & Resolved"
          value={resolved}
          icon={CheckCircle2}
          color="#10b981"
          subtitle="Completed work orders"
        />
      </div>

      {/* Work Orders Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', marginBottom: 2 }}>
              {viewScope === 'my' ? 'My Assigned Work Orders' : 'All Department Grievances'}
            </h2>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Showing {complaints.length} complaint{complaints.length !== 1 ? 's' : ''}
            </div>
          </div>

          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: 190 }}
          >
            <option value="">All Statuses</option>
            <option value="assigned">Assigned (Queued)</option>
            <option value="noted">Noted (Acknowledged)</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Sorted / Resolved</option>
          </select>
        </div>

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading work orders...
          </div>
        ) : complaints.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No work orders found in this queue matching the filter.
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Grievance Details</th>
                  <th>Photo Evidence</th>
                  <th>Location</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>SLA Target</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {complaints.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--primary-600)' }}>
                        {c.ticket_number}
                      </span>
                    </td>
                    <td style={{ maxWidth: 280 }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                        {c.category}
                      </div>
                    </td>
                    <td>
                      {c.image_url ? (
                        <button 
                          type="button"
                          onClick={() => setViewPhotoUrl(c.image_url)}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6,
                            padding: '4px 9px',
                            background: '#f0f9ff',
                            border: '1px solid #bae6fd',
                            borderRadius: 6,
                            cursor: 'pointer',
                            fontSize: '0.75rem',
                            color: '#0369a1',
                            fontWeight: 600,
                          }}
                          title="Click to view attached citizen photo"
                        >
                          <Camera size={13} />
                          <span>View Photo</span>
                        </button>
                      ) : (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>No photo</span>
                      )}
                    </td>
                    <td style={{ fontSize: '0.85rem' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <MapPin size={13} color="var(--text-muted)" />
                        {c.location || 'Ward area'}
                      </span>
                    </td>
                    <td>
                      <PriorityBadge priority={c.priority} />
                    </td>
                    <td>
                      <StatusBadge status={c.status} />
                    </td>
                    <td style={{ fontSize: '0.82rem', color: '#34d399', fontWeight: 600 }}>
                      {c.sla_target_hours ? `${c.sla_target_hours} Hours` : '24 Hours'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        <button
                          onClick={() => handleOpenStatusModal(c)}
                          className="btn btn-primary btn-sm"
                          style={{ padding: '0.35rem 0.75rem', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                        >
                          <CheckCircle size={13} />
                          Update
                        </button>
                        <Link to={`/complaints/${c.id}`} className="btn btn-secondary btn-sm" style={{ padding: '0.35rem 0.65rem' }}>
                          <ArrowUpRight size={14} />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: Field Officer Status Update (Noted, Progress, Sorted) */}
      {activeComplaint && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(8px)',
          zIndex: 999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem',
        }}>
          <div className="animate-fade-in" style={{
            width: '100%',
            maxWidth: 540,
            padding: '2rem',
            background: '#ffffff',
            borderRadius: 16,
            border: '1px solid var(--border-subtle)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-primary)' }}>
                  <ShieldAlert size={22} color="var(--primary-600)" />
                  Update Work Order Status
                </h3>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 2 }}>
                  Ticket: <strong style={{ color: 'var(--primary-600)' }}>{activeComplaint.ticket_number}</strong>
                </div>
              </div>
              <button
                onClick={() => setActiveComplaint(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{
              background: 'var(--bg-subtle)',
              padding: '0.85rem 1rem',
              borderRadius: 10,
              border: '1px solid var(--border-subtle)',
              fontSize: '0.86rem',
              marginBottom: '1.5rem',
            }}>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{activeComplaint.title}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                {activeComplaint.category} • Location: {activeComplaint.location || 'Local area'}
              </div>
            </div>

            <form onSubmit={handleUpdateStatus}>
              {/* Quick Workflow Action Buttons (Noted / Progress / Sorted) */}
              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Select Work Order Action:</span>
                  <span style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 600 }}>Citizen receives instant notification</span>
                </label>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.6rem', marginTop: 4 }}>
                  {/* Button 1: Noted */}
                  <button
                    type="button"
                    onClick={() => handleQuickStatusSelect('noted')}
                    style={{
                      padding: '0.75rem 0.5rem',
                      borderRadius: 10,
                      border: nextStatus === 'noted' ? '2px solid #0284c7' : '1px solid var(--border-subtle)',
                      background: nextStatus === 'noted' ? '#f0f9ff' : '#ffffff',
                      color: nextStatus === 'noted' ? '#0369a1' : 'var(--text-secondary)',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 4,
                      transition: 'var(--transition-fast)',
                    }}
                  >
                    <ClipboardList size={18} />
                    <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>1. Noted</span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Acknowledged</span>
                  </button>

                  {/* Button 2: Progress */}
                  <button
                    type="button"
                    onClick={() => handleQuickStatusSelect('in_progress')}
                    style={{
                      padding: '0.75rem 0.5rem',
                      borderRadius: 10,
                      border: nextStatus === 'in_progress' ? '2px solid #7c3aed' : '1px solid var(--border-subtle)',
                      background: nextStatus === 'in_progress' ? '#f5f3ff' : '#ffffff',
                      color: nextStatus === 'in_progress' ? '#6d28d9' : 'var(--text-secondary)',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 4,
                      transition: 'var(--transition-fast)',
                    }}
                  >
                    <AlertTriangle size={18} />
                    <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>2. In Progress</span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Work Underway</span>
                  </button>

                  {/* Button 3: Sorted */}
                  <button
                    type="button"
                    onClick={() => handleQuickStatusSelect('resolved')}
                    style={{
                      padding: '0.75rem 0.5rem',
                      borderRadius: 10,
                      border: nextStatus === 'resolved' ? '2px solid #059669' : '1px solid var(--border-subtle)',
                      background: nextStatus === 'resolved' ? '#ecfdf5' : '#ffffff',
                      color: nextStatus === 'resolved' ? '#047857' : 'var(--text-secondary)',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 4,
                      transition: 'var(--transition-fast)',
                    }}
                  >
                    <CheckCircle2 size={18} />
                    <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>3. Sorted</span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Resolved</span>
                  </button>
                </div>
              </div>

              {/* Remarks Textarea */}
              <div className="form-group" style={{ marginTop: '1.25rem' }}>
                <label className="form-label">
                  Field Remarks & Public Action Details:
                </label>
                <textarea
                  rows={3}
                  required
                  className="form-textarea"
                  placeholder="Describe inspection observations, repair work underway, or final resolution notes..."
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                />
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  This update will be sent directly to the citizen and recorded in the audit lifecycle timeline.
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.75rem' }}>
                <button
                  type="button"
                  onClick={() => setActiveComplaint(null)}
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !remarks.trim()}
                  className="btn btn-primary"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
                >
                  <Send size={15} />
                  {submitting ? 'Updating...' : 'Publish Update to Citizen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lightbox Photo Preview Modal */}
      {viewPhotoUrl && (
        <div 
          onClick={() => setViewPhotoUrl(null)}
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
              src={viewPhotoUrl} 
              alt="Grievance evidence" 
              style={{
                maxWidth: '100%',
                maxHeight: '80vh',
                borderRadius: 14,
                boxShadow: '0 20px 50px rgba(0,0,0,0.8)',
                border: '1px solid rgba(255,255,255,0.15)',
              }}
            />
            <button
              onClick={() => setViewPhotoUrl(null)}
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
