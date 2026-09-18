import React, { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';
import { Users, UserPlus, Shield, UserCheck, X, Mail, Phone, Lock, Building } from 'lucide-react';

export const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState('');
  const [showAddStaffModal, setShowAddStaffModal] = useState(false);

  const [staffForm, setStaffForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: 'Staff@123',
    department_id: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const [usersRes, deptsRes] = await Promise.all([
        adminService.listUsers({ role: roleFilter || undefined }),
        adminService.listDepartments(),
      ]);
      setUsers(usersRes.users || usersRes || []);
      setDepartments(deptsRes.departments || deptsRes || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [roleFilter]);

  const handleCreateStaff = async (e) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      await adminService.createStaff(staffForm);
      setShowAddStaffModal(false);
      setStaffForm({
        full_name: '',
        email: '',
        phone: '',
        password: 'Staff@123',
        department_id: '',
      });
      await loadUsers();
    } catch (err) {
      alert('Failed to create staff account: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const getDeptName = (deptId) => {
    const d = departments.find((item) => item.id === deptId);
    return d ? d.name : '—';
  };

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
          <h1 style={{ fontSize: '1.8rem', marginBottom: '0.25rem' }}>Users & Staff Directory</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Manage registered citizen accounts and create field officer staff credentials.
          </p>
        </div>

        <button onClick={() => setShowAddStaffModal(true)} className="btn btn-primary btn-sm">
          <UserPlus size={16} />
          Add Staff Member
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-card" style={{ padding: '1rem', marginBottom: '1.5rem', display: 'flex', gap: '1rem' }}>
        <select
          className="form-select"
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          style={{ width: 200 }}
        >
          <option value="">All Roles</option>
          <option value="citizen">Citizens</option>
          <option value="staff">Staff Officers</option>
          <option value="admin">Administrators</option>
        </select>
      </div>

      {/* Users Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading user directory...
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Contact Phone</th>
                  <th>Joined Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{u.full_name}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{u.email}</div>
                    </td>
                    <td>
                      <span style={{
                        padding: '0.2rem 0.6rem',
                        borderRadius: 20,
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                        background: u.role === 'admin' ? '#eff6ff' : u.role === 'staff' ? '#ecfdf5' : '#f1f5f9',
                        color: u.role === 'admin' ? '#1d4ed8' : u.role === 'staff' ? '#047857' : '#475569',
                        border: u.role === 'admin' ? '1px solid #bfdbfe' : u.role === 'staff' ? '1px solid #a7f3d0' : '1px solid #cbd5e1',
                      }}>
                        {u.role}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.85rem' }}>
                      {u.department_id ? getDeptName(u.department_id) : '—'}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {u.phone || '—'}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 4,
                        fontSize: '0.75rem',
                        color: u.is_active ? '#059669' : '#dc2626',
                        fontWeight: 600,
                      }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: u.is_active ? '#059669' : '#dc2626' }} />
                        {u.is_active ? 'Active' : 'Disabled'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: Add Staff Member */}
      {showAddStaffModal && (
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
                <UserPlus size={20} color="var(--primary-600)" />
                Register Staff Member
              </h3>
              <button
                onClick={() => setShowAddStaffModal(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateStaff}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  required
                  className="form-input"
                  placeholder="e.g. Suresh Kumar"
                  value={staffForm.full_name}
                  onChange={(e) => setStaffForm({ ...staffForm, full_name: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Official Email</label>
                <input
                  type="email"
                  required
                  className="form-input"
                  placeholder="suresh.water@gov.in"
                  value={staffForm.email}
                  onChange={(e) => setStaffForm({ ...staffForm, email: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Assigned Department</label>
                <select
                  className="form-select"
                  value={staffForm.department_id}
                  onChange={(e) => setStaffForm({ ...staffForm, department_id: e.target.value })}
                >
                  <option value="">Select Department</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <input
                  type="tel"
                  className="form-input"
                  placeholder="9876543210"
                  value={staffForm.phone}
                  onChange={(e) => setStaffForm({ ...staffForm, phone: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Default Password</label>
                <input
                  type="text"
                  required
                  className="form-input"
                  value={staffForm.password}
                  onChange={(e) => setStaffForm({ ...staffForm, password: e.target.value })}
                />
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  User will be prompted to change password on first login.
                </span>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAddStaffModal(false)}
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                >
                  {submitting ? 'Creating...' : 'Create Staff Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
