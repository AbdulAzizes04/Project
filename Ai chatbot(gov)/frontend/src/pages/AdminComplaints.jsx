import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../services/adminService';
import { complaintService } from '../services/complaintService';
import { 
  Search, 
  Filter, 
  CheckCircle, 
  UserCheck, 
  ShieldAlert, 
  ExternalLink, 
  Building,
  Sparkles,
  Camera,
  X
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { AIConfidenceBadge } from '../components/AIConfidenceBadge';

export const AdminComplaints = () => {
  const [complaints, setComplaints] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [staffList, setStaffList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewPhotoUrl, setViewPhotoUrl] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Modals
  const [activeModal, setActiveModal] = useState(null); // 'assign' | 'verify'
  const [selectedComplaint, setSelectedComplaint] = useState(null);

  // Modal form states
  const [assignDeptId, setAssignDeptId] = useState('');
  const [assignStaffId, setAssignStaffId] = useState('');
  const [verifyCategory, setVerifyCategory] = useState('');
  const [verifyPriority, setVerifyPriority] = useState('');
  const [verifyDeptId, setVerifyDeptId] = useState('');
  const [verifyNotes, setVerifyNotes] = useState('');
  const [processing, setProcessing] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (categoryFilter) params.category = categoryFilter;

      const [complaintsRes, deptsRes, staffRes] = await Promise.all([
        adminService.listAllComplaints(params),
        adminService.listDepartments(),
        adminService.listStaff(),
      ]);

      setComplaints(complaintsRes.items || complaintsRes.complaints || complaintsRes || []);
      setDepartments(deptsRes.departments || deptsRes || []);
      setStaffList(staffRes.staff || []);
    } catch (err) {
      console.error('Error fetching complaints list:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, priorityFilter, categoryFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const openAssignModal = (complaint) => {
    setSelectedComplaint(complaint);
    setAssignDeptId(complaint.department_id || '');
    setAssignStaffId(complaint.assigned_to_id || '');
    setActiveModal('assign');
  };

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComplaint || processing) return;
    setProcessing(true);
    try {
      await complaintService.assignComplaint(
        selectedComplaint.id,
        assignStaffId || null,
        assignDeptId || null
      );
      setActiveModal(null);
      await loadData();
    } catch (err) {
      alert('Assignment failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setProcessing(false);
    }
  };

  const openVerifyModal = (complaint) => {
    setSelectedComplaint(complaint);
    setVerifyCategory(complaint.category);
    setVerifyPriority(complaint.priority);
    setVerifyDeptId(complaint.department_id || '');
    setVerifyNotes('Verified and aligned with departmental scope');
    setActiveModal('verify');
  };

  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    if (!selectedComplaint || processing) return;
    setProcessing(true);
    try {
      await complaintService.verifyComplaint(
        selectedComplaint.id,
        verifyCategory,
        verifyPriority,
        verifyDeptId || null,
        verifyNotes
      );
      setActiveModal(null);
      await loadData();
    } catch (err) {
      alert('Verification failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setProcessing(false);
    }
  };

  const filteredStaff = assignDeptId
    ? staffList.filter((s) => s.department_id === assignDeptId)
    : staffList;

  return (
    <div className="main-content animate-fade-in">
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', marginBottom: '0.25rem' }}>Grievance Triage & Allocation</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Review AI predictions, verify classifications, and dispatch work orders to field officers.
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-card" style={{ padding: '1.25rem', marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Search Box */}
          <form onSubmit={handleSearchSubmit} style={{ flex: 1, minWidth: 260, position: 'relative' }}>
            <input
              type="text"
              placeholder="Search by ticket # or title..."
              className="form-input"
              style={{ width: '100%', paddingLeft: '2.4rem' }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 14 }} />
          </form>

          {/* Status Select */}
          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: 160 }}
          >
            <option value="">All Statuses</option>
            <option value="submitted">Submitted</option>
            <option value="verified">Verified</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="rejected">Rejected</option>
          </select>

          {/* Priority Select */}
          <select
            className="form-select"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            style={{ width: 150 }}
          >
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          {/* Category Select */}
          <select
            className="form-select"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{ width: 170 }}
          >
            <option value="">All Categories</option>
            <option value="Water Supply">Water Supply</option>
            <option value="Roads">Roads</option>
            <option value="Sanitation">Sanitation</option>
            <option value="Electricity">Electricity</option>
            <option value="Street Lighting">Street Lighting</option>
            <option value="Drainage">Drainage</option>
          </select>
        </div>
      </div>

      {/* Complaints Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading grievances...
          </div>
        ) : complaints.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No complaints found matching the active filters.
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Grievance Info</th>
                  <th>AI Prediction</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Assigned Officer</th>
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
                    <td style={{ maxWidth: 320 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-primary)' }}>{c.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                        {c.category} • {c.location || 'Ward area'}
                      </div>
                      {c.image_url && (
                        <div style={{ marginTop: 5 }}>
                          <button
                            type="button"
                            onClick={() => setViewPhotoUrl(c.image_url)}
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 4,
                              padding: '2px 8px',
                              background: 'var(--primary-50)',
                              border: '1px solid var(--primary-200)',
                              borderRadius: 4,
                              color: 'var(--primary-600)',
                              fontSize: '0.72rem',
                              fontWeight: 600,
                              cursor: 'pointer',
                            }}
                          >
                            <Camera size={11} />
                            <span>Photo Evidence</span>
                          </button>
                        </div>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>{c.predicted_category || c.category}</span>
                        {c.ai_confidence && <AIConfidenceBadge confidence={c.ai_confidence} />}
                      </div>
                    </td>
                    <td>
                      <PriorityBadge priority={c.priority} />
                    </td>
                    <td>
                      <StatusBadge status={c.status} />
                    </td>
                    <td style={{ fontSize: '0.85rem' }}>
                      {c.assigned_to ? (
                        <div style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{c.assigned_to.full_name}</div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Unassigned</span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        {c.status === 'submitted' && (
                          <button
                            onClick={() => openVerifyModal(c)}
                            className="btn btn-secondary btn-sm"
                            title="Verify AI Classification"
                            style={{ color: '#818cf8', borderColor: 'rgba(99,102,241,0.4)' }}
                          >
                            <Sparkles size={13} />
                            Verify
                          </button>
                        )}
                        <button
                          onClick={() => openAssignModal(c)}
                          className="btn btn-secondary btn-sm"
                          title="Assign to Staff Officer"
                        >
                          <UserCheck size={13} />
                          Assign
                        </button>
                        <Link
                          to={`/complaints/${c.id}`}
                          className="btn btn-secondary btn-sm"
                          title="Full Details"
                        >
                          <ExternalLink size={13} />
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

      {/* MODAL: Assign Complaint */}
      {activeModal === 'assign' && selectedComplaint && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(6px)',
          zIndex: 999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem',
        }}>
          <div className="animate-fade-in" style={{
            width: '100%',
            maxWidth: 480,
            padding: '2rem',
            background: '#ffffff',
            borderRadius: 16,
            border: '1px solid var(--border-subtle)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-primary)' }}>
                <UserCheck size={20} color="var(--primary-600)" />
                Assign Complaint
              </h3>
              <button
                onClick={() => setActiveModal(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
              Assigning <strong style={{ color: 'var(--primary-600)' }}>{selectedComplaint.ticket_number}</strong>: "{selectedComplaint.title}"
            </div>

            <form onSubmit={handleAssignSubmit}>
              <div className="form-group">
                <label className="form-label">Select Department</label>
                <select
                  className="form-select"
                  value={assignDeptId}
                  onChange={(e) => {
                    setAssignDeptId(e.target.value);
                    setAssignStaffId('');
                  }}
                >
                  <option value="">Choose Department</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Assign Field Officer / Staff</label>
                <select
                  className="form-select"
                  value={assignStaffId}
                  onChange={(e) => setAssignStaffId(e.target.value)}
                >
                  <option value="">Select Officer (Optional)</option>
                  {filteredStaff.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.full_name} ({s.email})
                    </option>
                  ))}
                </select>
                {filteredStaff.length === 0 && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    No staff currently assigned to this department.
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.75rem' }}>
                <button
                  type="button"
                  onClick={() => setActiveModal(null)}
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={processing}
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                >
                  {processing ? 'Assigning...' : 'Confirm Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Verify AI Prediction */}
      {activeModal === 'verify' && selectedComplaint && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(6px)',
          zIndex: 999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem',
        }}>
          <div className="animate-fade-in" style={{
            width: '100%',
            maxWidth: 500,
            padding: '2rem',
            background: '#ffffff',
            borderRadius: 16,
            border: '1px solid var(--border-subtle)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-primary)' }}>
                <Sparkles size={20} color="var(--primary-600)" />
                Verify AI Prediction
              </h3>
              <button
                onClick={() => setActiveModal(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
              Confirm or override AI classification for <strong style={{ color: 'var(--primary-600)' }}>{selectedComplaint.ticket_number}</strong>
            </div>

            <form onSubmit={handleVerifySubmit}>
              <div className="form-group">
                <label className="form-label">Verified Category</label>
                <select
                  className="form-select"
                  value={verifyCategory}
                  onChange={(e) => setVerifyCategory(e.target.value)}
                >
                  <option value="Water Supply">Water Supply</option>
                  <option value="Roads">Roads</option>
                  <option value="Sanitation">Sanitation</option>
                  <option value="Electricity">Electricity</option>
                  <option value="Street Lighting">Street Lighting</option>
                  <option value="Drainage">Drainage</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Verified Priority</label>
                <select
                  className="form-select"
                  value={verifyPriority}
                  onChange={(e) => setVerifyPriority(e.target.value)}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Routing Department</label>
                <select
                  className="form-select"
                  value={verifyDeptId}
                  onChange={(e) => setVerifyDeptId(e.target.value)}
                >
                  <option value="">Keep current / Auto-match</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Verification Notes</label>
                <input
                  type="text"
                  className="form-input"
                  value={verifyNotes}
                  onChange={(e) => setVerifyNotes(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.75rem' }}>
                <button
                  type="button"
                  onClick={() => setActiveModal(null)}
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={processing}
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                >
                  {processing ? 'Verifying...' : 'Approve & Mark Verified'}
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
