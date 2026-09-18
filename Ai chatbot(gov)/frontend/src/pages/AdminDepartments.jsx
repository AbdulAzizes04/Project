import React, { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';
import { Building2, Plus, Clock, ShieldCheck, Edit2, X, AlertCircle } from 'lucide-react';

export const AdminDepartments = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingDept, setEditingDept] = useState(null);

  const [form, setForm] = useState({
    name: '',
    code: '',
    description: '',
    category_mapping: 'Water Supply',
    sla_hours_critical: 12,
    sla_hours_high: 24,
    sla_hours_medium: 72,
    sla_hours_low: 168,
  });
  const [submitting, setSubmitting] = useState(false);

  const loadDepartments = async () => {
    try {
      const data = await adminService.listDepartments();
      setDepartments(data.departments || data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  const handleOpenAdd = () => {
    setEditingDept(null);
    setForm({
      name: '',
      code: '',
      description: '',
      category_mapping: 'Water Supply',
      sla_hours_critical: 12,
      sla_hours_high: 24,
      sla_hours_medium: 72,
      sla_hours_low: 168,
    });
    setShowAddModal(true);
  };

  const handleOpenEdit = (dept) => {
    setEditingDept(dept);
    setForm({
      name: dept.name,
      code: dept.code,
      description: dept.description || '',
      category_mapping: dept.category_mapping || 'Water Supply',
      sla_hours_critical: dept.sla_hours_critical || 12,
      sla_hours_high: dept.sla_hours_high || 24,
      sla_hours_medium: dept.sla_hours_medium || 72,
      sla_hours_low: dept.sla_hours_low || 168,
    });
    setShowAddModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (editingDept) {
        await adminService.updateDepartment(editingDept.id, form);
      } else {
        await adminService.createDepartment(form);
      }
      setShowAddModal(false);
      await loadDepartments();
    } catch (err) {
      alert('Failed to save department: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
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
          <h1 style={{ fontSize: '1.8rem', marginBottom: '0.25rem' }}>Municipal Departments & Routing</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Configure automatic AI category routing mappings and SLA resolution deadlines.
          </p>
        </div>

        <button onClick={handleOpenAdd} className="btn btn-primary btn-sm">
          <Plus size={16} />
          Add Department
        </button>
      </div>

      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading departments...
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.5rem',
        }}>
          {departments.map((dept) => (
            <div key={dept.id} className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.75rem',
                    color: 'var(--primary-700)',
                    background: '#eff6ff',
                    border: '1px solid #bfdbfe',
                    padding: '0.2rem 0.5rem',
                    borderRadius: 6,
                    fontWeight: 700,
                  }}>
                    {dept.code}
                  </span>
                  <h3 style={{ fontSize: '1.15rem', marginTop: 6, color: 'var(--text-primary)' }}>{dept.name}</h3>
                </div>
                <button
                  onClick={() => handleOpenEdit(dept)}
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '0.35rem 0.6rem' }}
                  title="Edit Department & SLA"
                >
                  <Edit2 size={13} />
                </button>
              </div>

              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', flex: 1, marginBottom: '1.25rem', lineHeight: 1.5 }}>
                {dept.description || 'Handles municipal services for citizen grievances.'}
              </p>

              <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: '0.9rem', marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 2 }}>
                  ROUTED AI CATEGORY
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--primary-600)' }}>
                  {dept.category_mapping || 'All categories'}
                </div>
              </div>

              {/* SLA Breakdown */}
              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.9rem' }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Clock size={12} />
                  RESOLUTION SLA TARGETS
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6, textAlign: 'center', fontSize: '0.75rem' }}>
                  <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '0.35rem 0.2rem', borderRadius: 6, color: '#b91c1c' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 600 }}>Critical</div>
                    <strong>{dept.sla_hours_critical}h</strong>
                  </div>
                  <div style={{ background: '#fff7ed', border: '1px solid #fed7aa', padding: '0.35rem 0.2rem', borderRadius: 6, color: '#c2410c' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 600 }}>High</div>
                    <strong>{dept.sla_hours_high}h</strong>
                  </div>
                  <div style={{ background: '#fffbeb', border: '1px solid #fde68a', padding: '0.35rem 0.2rem', borderRadius: 6, color: '#b45309' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 600 }}>Med</div>
                    <strong>{dept.sla_hours_medium}h</strong>
                  </div>
                  <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', padding: '0.35rem 0.2rem', borderRadius: 6, color: '#047857' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 600 }}>Low</div>
                    <strong>{dept.sla_hours_low}h</strong>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Add or Edit Department */}
      {showAddModal && (
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
            maxWidth: 520,
            padding: '2rem',
            background: '#ffffff',
            borderRadius: 16,
            border: '1px solid var(--border-subtle)',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-primary)' }}>
                <Building2 size={20} color="var(--primary-600)" />
                {editingDept ? 'Edit Department' : 'Create Department'}
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Department Name</label>
                <input
                  type="text"
                  required
                  className="form-input"
                  placeholder="e.g. Department of Water Supply"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Code</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. WATER"
                    value={form.code}
                    onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Mapped Category</label>
                  <select
                    className="form-select"
                    value={form.category_mapping}
                    onChange={(e) => setForm({ ...form, category_mapping: e.target.value })}
                  >
                    <option value="Water Supply">Water Supply</option>
                    <option value="Roads">Roads</option>
                    <option value="Sanitation">Sanitation</option>
                    <option value="Electricity">Electricity</option>
                    <option value="Street Lighting">Street Lighting</option>
                    <option value="Drainage">Drainage</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Department mandate & coverage..."
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label className="form-label">Resolution SLA Deadlines (Hours)</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem', marginTop: 4 }}>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: '#fca5a5' }}>Critical</span>
                    <input
                      type="number"
                      required
                      className="form-input"
                      value={form.sla_hours_critical}
                      onChange={(e) => setForm({ ...form, sla_hours_critical: Number(e.target.value) })}
                    />
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: '#fdba74' }}>High</span>
                    <input
                      type="number"
                      required
                      className="form-input"
                      value={form.sla_hours_high}
                      onChange={(e) => setForm({ ...form, sla_hours_high: Number(e.target.value) })}
                    />
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: '#fde047' }}>Medium</span>
                    <input
                      type="number"
                      required
                      className="form-input"
                      value={form.sla_hours_medium}
                      onChange={(e) => setForm({ ...form, sla_hours_medium: Number(e.target.value) })}
                    />
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: '#86efac' }}>Low</span>
                    <input
                      type="number"
                      required
                      className="form-input"
                      value={form.sla_hours_low}
                      onChange={(e) => setForm({ ...form, sla_hours_low: Number(e.target.value) })}
                    />
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
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
                  {submitting ? 'Saving...' : editingDept ? 'Update Department' : 'Create Department'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
