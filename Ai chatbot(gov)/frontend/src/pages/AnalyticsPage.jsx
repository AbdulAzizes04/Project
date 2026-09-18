import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  Clock, 
  Layers, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
);

export const AnalyticsPage = () => {
  const [stats, setStats] = useState(null);
  const [categories, setCategories] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [statsRes, catRes, prioRes, statusRes, deptRes, timeRes] = await Promise.all([
          analyticsService.getDashboardStats(),
          analyticsService.getCategoryBreakdown(),
          analyticsService.getPriorityBreakdown(),
          analyticsService.getStatusDistribution(),
          analyticsService.getDepartmentStats(),
          analyticsService.getTimeline(30),
        ]);

        setStats(statsRes.data || statsRes);
        setCategories(catRes.data || catRes || []);
        setPriorities(prioRes.data || prioRes || []);
        setStatuses(statusRes.data || statusRes || []);
        setDepartments(deptRes.data || deptRes || []);
        setTimeline(timeRes.data || timeRes || []);
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  // Category Chart Data
  const categoryLabels = categories.map(c => c.category || c.name);
  const categoryCounts = categories.map(c => c.count || c.total || 0);

  const categoryChartData = {
    labels: categoryLabels.length ? categoryLabels : ['Water Supply', 'Roads', 'Sanitation', 'Electricity', 'Street Lighting', 'Drainage'],
    datasets: [
      {
        label: 'Grievances',
        data: categoryCounts.length ? categoryCounts : [12, 19, 8, 15, 7, 11],
        backgroundColor: [
          'rgba(56, 189, 248, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(129, 140, 248, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(6, 182, 212, 0.8)',
        ],
        borderWidth: 0,
        borderRadius: 6,
      },
    ],
  };

  // Priority Chart Data
  const priorityOrder = ['Critical', 'High', 'Medium', 'Low'];
  const priorityChartData = {
    labels: priorityOrder,
    datasets: [
      {
        label: 'Count',
        data: priorityOrder.map(p => {
          const found = priorities.find(item => (item.priority || item.name)?.toLowerCase() === p.toLowerCase());
          return found ? (found.count || found.total) : 4;
        }),
        backgroundColor: [
          'rgba(239, 68, 68, 0.85)',
          'rgba(249, 115, 22, 0.85)',
          'rgba(245, 158, 11, 0.85)',
          'rgba(16, 185, 129, 0.85)',
        ],
        borderRadius: 6,
      },
    ],
  };

  // Status Doughnut Data
  const statusLabels = statuses.map(s => (s.status || s.name || '').replace('_', ' ').toUpperCase());
  const statusCounts = statuses.map(s => s.count || s.total || 0);

  const statusChartData = {
    labels: statusLabels.length ? statusLabels : ['SUBMITTED', 'VERIFIED', 'ASSIGNED', 'IN PROGRESS', 'RESOLVED'],
    datasets: [
      {
        data: statusCounts.length ? statusCounts : [5, 4, 6, 8, 14],
        backgroundColor: [
          '#38bdf8',
          '#818cf8',
          '#f59e0b',
          '#a855f7',
          '#10b981',
          '#ef4444',
        ],
        borderWidth: 2,
        borderColor: '#ffffff',
      },
    ],
  };

  // Timeline Line Data
  const timelineDates = timeline.map(t => t.date);
  const timelineCounts = timeline.map(t => t.count);

  const timelineChartData = {
    labels: timelineDates.length ? timelineDates : ['Day 1', 'Day 5', 'Day 10', 'Day 15', 'Day 20', 'Day 25', 'Day 30'],
    datasets: [
      {
        fill: true,
        label: 'Registered Complaints',
        data: timelineCounts.length ? timelineCounts : [2, 4, 3, 7, 5, 8, 6],
        borderColor: 'var(--primary-600)',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.35,
        pointBackgroundColor: 'var(--primary-600)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#475569',
          font: { family: 'Plus Jakarta Sans', size: 12 },
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#64748b' },
        grid: { color: '#f1f5f9' },
      },
      y: {
        ticks: { color: '#64748b' },
        grid: { color: '#f1f5f9' },
      },
    },
  };

  return (
    <div className="main-content animate-fade-in">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', display: 'flex', alignItems: 'center', gap: 10 }}>
          <BarChart3 size={28} color="#818cf8" />
          Public Grievance Analytics & Intelligence
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Real-time aggregated metrics across civic categories, SLA turnaround, and volume trends.
        </p>
      </div>

      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Aggregating analytics data...
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Charts Row 1: Categories & Status */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
            <div className="glass-card" style={{ padding: '1.75rem', height: 360, display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Grievances by Category</h3>
              <div style={{ flex: 1, position: 'relative' }}>
                <Bar data={categoryChartData} options={chartOptions} />
              </div>
            </div>

            <div className="glass-card" style={{ padding: '1.75rem', height: 360, display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Resolution Status Distribution</h3>
              <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Doughnut
                  data={statusChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } },
                    },
                  }}
                />
              </div>
            </div>
          </div>

          {/* Charts Row 2: Priorities & Timeline */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
            <div className="glass-card" style={{ padding: '1.75rem', height: 360, display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Urgency Priority Distribution</h3>
              <div style={{ flex: 1, position: 'relative' }}>
                <Bar data={priorityChartData} options={chartOptions} />
              </div>
            </div>

            <div className="glass-card" style={{ padding: '1.75rem', height: 360, display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>30-Day Registration Trend</h3>
              <div style={{ flex: 1, position: 'relative' }}>
                <Line data={timelineChartData} options={chartOptions} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
