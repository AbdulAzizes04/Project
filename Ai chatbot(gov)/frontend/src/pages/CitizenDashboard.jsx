import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { complaintService } from '../services/complaintService';
import { 
  Bot, 
  PlusCircle, 
  FileText, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  ExternalLink, 
  Search,
  ArrowUpRight
} from 'lucide-react';
import { StatsCard } from '../components/StatsCard';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';

export const CitizenDashboard = () => {
  const { user } = useAuth();
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    const fetchComplaints = async () => {
      try {
        const data = await complaintService.getMyComplaints();
        setComplaints(data || []);
      } catch (err) {
        console.error('Failed to load complaints:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchComplaints();
  }, []);

  const total = complaints.length;
  const inProgress = complaints.filter(c => ['assigned', 'in_progress'].includes(c.status)).length;
  const resolved = complaints.filter(c => c.status === 'resolved').length;
  const submitted = complaints.filter(c => c.status === 'submitted').length;

  const filteredComplaints = complaints.filter(c => {
    const matchesSearch = 
      c.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.ticket_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.category?.toLowerCase().includes(searchTerm.toLowerCase());

    if (statusFilter === 'ALL') return matchesSearch;
    return matchesSearch && c.status === statusFilter.toLowerCase();
  });

  return (
    <div className="main-content animate-fade-in">
      {/* Welcome Banner */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>
            Namaste, {user?.full_name || 'Citizen'}
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Track and manage your registered public grievances with automated AI resolution updates.
          </p>
        </div>

        <Link to="/chat" className="btn btn-accent" style={{ padding: '0.75rem 1.6rem', fontSize: '0.95rem' }}>
          <Bot size={20} />
          Lodge Grievance with AI
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatsCard
          title="Total Registered"
          value={total}
          icon={FileText}
          color="#818cf8"
          subtitle="All-time grievances"
        />
        <StatsCard
          title="Submitted / Queued"
          value={submitted}
          icon={Clock}
          color="#38bdf8"
          subtitle="Awaiting verification"
        />
        <StatsCard
          title="Active In Progress"
          value={inProgress}
          icon={AlertCircle}
          color="#f59e0b"
          subtitle="Assigned to field staff"
        />
        <StatsCard
          title="Resolved"
          value={resolved}
          icon={CheckCircle2}
          color="#10b981"
          subtitle="Successfully closed"
        />
      </div>

      {/* Grievances List Card */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}>
          <h2 style={{ fontSize: '1.3rem' }}>My Grievance History</h2>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            {/* Search Input */}
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                placeholder="Search ticket, title..."
                className="form-input"
                style={{ padding: '0.5rem 0.8rem 0.5rem 2.2rem', fontSize: '0.85rem', width: 220 }}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 10, top: 11 }} />
            </div>

            {/* Filter Tabs */}
            <select
              className="form-select"
              style={{ padding: '0.5rem 0.8rem', fontSize: '0.85rem' }}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="ASSIGNED">Assigned</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading your grievances...
          </div>
        ) : filteredComplaints.length === 0 ? (
          <div style={{
            padding: '4rem 1rem',
            textAlign: 'center',
            background: 'var(--bg-subtle)',
            borderRadius: 12,
            border: '1px dashed var(--border-subtle)',
          }}>
            <Bot size={42} color="#818cf8" style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>No grievances found</h3>
            <p style={{ color: 'var(--text-secondary)', maxWidth: 460, margin: '0 auto 1.5rem', fontSize: '0.9rem' }}>
              You haven't filed any complaints matching this criteria. Click below to start an interactive grievance session with our conversational AI.
            </p>
            <Link to="/chat" className="btn btn-primary">
              <PlusCircle size={16} />
              Lodge New Grievance
            </Link>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticket #</th>
                  <th>Title & Department</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Date Filed</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredComplaints.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <span style={{
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 700,
                        color: 'var(--primary-600)',
                        fontSize: '0.85rem',
                      }}>
                        {c.ticket_number}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-primary)' }}>{c.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                        {c.category} • {c.location || 'Local ward'}
                      </div>
                    </td>
                    <td>
                      <PriorityBadge priority={c.priority} />
                    </td>
                    <td>
                      <StatusBadge status={c.status} />
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : 'Today'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link
                        to={`/complaints/${c.id}`}
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '0.35rem 0.75rem' }}
                      >
                        View
                        <ArrowUpRight size={14} />
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
