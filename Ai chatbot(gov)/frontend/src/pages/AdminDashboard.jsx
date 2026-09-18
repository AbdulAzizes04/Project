import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../services/adminService';
import { 
  BarChart3, 
  FileText, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  Users, 
  Building2, 
  Cpu, 
  ArrowRight,
  ShieldAlert
} from 'lucide-react';
import { StatsCard } from '../components/StatsCard';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';

export const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentComplaints, setRecentComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const statsRes = await adminService.getDashboardStats();
        if (statsRes.success) {
          setStats(statsRes.stats || statsRes.data);
        }
        const complaintsRes = await adminService.listAllComplaints({ page_size: 5 });
        setRecentComplaints(complaintsRes.items || complaintsRes.complaints || complaintsRes || []);
      } catch (err) {
        console.error('Failed to load admin dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

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
          <h1 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Admin Command Center</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Central administrative grievance monitoring, AI verification, and municipal department allocation.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link to="/admin/complaints" className="btn btn-primary btn-sm">
            <FileText size={16} />
            Manage Complaints
          </Link>
          <Link to="/admin/models" className="btn btn-secondary btn-sm">
            <Cpu size={16} />
            AI Model Benchmark
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatsCard
          title="Total Grievances"
          value={stats?.total_complaints ?? 0}
          icon={FileText}
          color="#818cf8"
          subtitle="Registered across city"
        />
        <StatsCard
          title="Pending Verification"
          value={stats?.pending_verification ?? 0}
          icon={Clock}
          color="#38bdf8"
          subtitle="Awaiting admin sign-off"
        />
        <StatsCard
          title="In Progress"
          value={stats?.in_progress ?? 0}
          icon={AlertTriangle}
          color="#f59e0b"
          subtitle="Active field work"
        />
        <StatsCard
          title="Resolved Cases"
          value={stats?.resolved ?? 0}
          icon={CheckCircle2}
          color="#10b981"
          subtitle="Successfully redressed"
        />
      </div>

      {/* Fast Navigation Shortcut Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1rem',
        marginBottom: '2.5rem',
      }}>
        <Link to="/admin/complaints" className="glass-card glass-card-interactive" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: 'var(--primary-50)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary-600)', border: '1px solid var(--primary-100)' }}>
                <FileText size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>All Grievances</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Triage & Reassign</div>
              </div>
            </div>
            <ArrowRight size={16} color="var(--text-muted)" />
          </div>
        </Link>

        <Link to="/admin/departments" className="glass-card glass-card-interactive" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: '#fffbeb', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#b45309', border: '1px solid #fde68a' }}>
                <Building2 size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>Departments</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SLA & Routing</div>
              </div>
            </div>
            <ArrowRight size={16} color="var(--text-muted)" />
          </div>
        </Link>

        <Link to="/admin/users" className="glass-card glass-card-interactive" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: '#ecfdf5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#16a34a', border: '1px solid #bbf7d0' }}>
                <Users size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>Staff & Users</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Add Field Officers</div>
              </div>
            </div>
            <ArrowRight size={16} color="var(--text-muted)" />
          </div>
        </Link>

        <Link to="/admin/analytics" className="glass-card glass-card-interactive" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: '#f0f9ff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0284c7', border: '1px solid #bae6fd' }}>
                <BarChart3 size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>Deep Analytics</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Visual Charts</div>
              </div>
            </div>
            <ArrowRight size={16} color="var(--text-muted)" />
          </div>
        </Link>
      </div>

      {/* Recent Complaints Table */}
      <div className="glass-card" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.3rem', color: 'var(--text-primary)' }}>Recent Incoming Grievances</h2>
          <Link to="/admin/complaints" style={{ fontSize: '0.85rem', color: 'var(--primary-600)', display: 'flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
            <span>View Full Roster</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading dashboard data...
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket #</th>
                  <th>Title & Citizen</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentComplaints.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--primary-600)' }}>
                        {c.ticket_number}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{c.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {c.citizen_name || c.citizen?.full_name || 'Citizen'}
                      </div>
                    </td>
                    <td>{c.category}</td>
                    <td>
                      <PriorityBadge priority={c.priority} />
                    </td>
                    <td>
                      <StatusBadge status={c.status} />
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : 'Today'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/complaints/${c.id}`} className="btn btn-secondary btn-sm">
                        Review
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
