import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Building2, TrendingUp, AlertTriangle, Activity,
  Cpu, Network, RefreshCw, Download, Eye, BarChart2,
} from 'lucide-react';
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis,
  Tooltip, CartesianGrid, Legend,
} from 'recharts';
import {
  Card, PageHeader, StatCard, RiskBadge, Button,
  Skeleton, SkeletonCard, SectionHeader, ProgressBar,
} from '@/components/ui';
import { dashboardApi } from '@/api/dashboardApi';
import { companyApi } from '@/api/companyApi';
import type { DashboardSummary, TrendPoint, RiskDistribution, RiskFactor, Company } from '@/types';
import {
  formatCurrency, formatPercentRaw, formatDate, getRiskHex,
  getNetworkExposureColor, clsx,
} from '@/utils';
import { useNavigate } from 'react-router-dom';

const TREND_PERIODS = ['7d', '30d', '90d', '1y'] as const;
type TrendPeriod = typeof TREND_PERIODS[number];

const RISK_COLORS = { LOW: '#16A34A', MEDIUM: '#F59E0B', HIGH: '#DC2626' };

// ============================================================
// SUB-COMPONENTS
// ============================================================

const KpiSkeleton = () => (
  <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
    {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
  </div>
);

const CustomTooltipLine: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-surface-200 rounded-xl shadow-dropdown p-3">
      <p className="text-xs text-content-secondary mb-1">{label}</p>
      <p className="text-sm font-semibold text-content-primary">
        {payload[0]?.value?.toFixed(1)}% default probability
      </p>
    </div>
  );
};

const CustomTooltipBar: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-surface-200 rounded-xl shadow-dropdown p-3">
      <p className="text-xs font-medium text-content-primary mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} className="text-xs text-content-secondary">
          {p.name}: <span className="font-semibold" style={{ color: p.color }}>{p.value}</span>
        </p>
      ))}
    </div>
  );
};

// ============================================================
// MAIN DASHBOARD
// ============================================================
const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [distribution, setDistribution] = useState<RiskDistribution | null>(null);
  const [riskFactors, setRiskFactors] = useState<RiskFactor[]>([]);
  const [highRisk, setHighRisk] = useState<Company[]>([]);
  const [trendPeriod, setTrendPeriod] = useState<TrendPeriod>('30d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [s, d, rf, hr] = await Promise.all([
          dashboardApi.getSummary(),
          dashboardApi.getRiskDistribution(),
          dashboardApi.getRiskFactors(),
          companyApi.getHighRisk(8),
        ]);
        setSummary(s);
        setDistribution(d);
        setRiskFactors(rf);
        setHighRisk(hr);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  useEffect(() => {
    dashboardApi.getTrend(trendPeriod).then(setTrend);
  }, [trendPeriod]);

  // Donut chart data
  const donutData = distribution
    ? [
        { name: 'Low Risk', value: distribution.low, color: '#16A34A' },
        { name: 'Medium Risk', value: distribution.medium, color: '#F59E0B' },
        { name: 'High Risk', value: distribution.high, color: '#DC2626' },
      ]
    : [];

  // Format trend for chart — downsample if long
  const chartTrend = trend.length > 60
    ? trend.filter((_, i) => i % Math.ceil(trend.length / 60) === 0)
    : trend;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  };

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-6">
      {/* Page Header */}
      <motion.div variants={itemVariants}>
        <PageHeader
          title="Maritime Loan Default Risk Dashboard"
          subtitle="AI-powered financial and network risk intelligence for maritime lending."
          actions={
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
                Refresh
              </Button>
              <Button variant="secondary" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>
                Export
              </Button>
            </div>
          }
        />
      </motion.div>

      {/* KPI Cards */}
      <motion.div variants={itemVariants}>
        {loading ? <KpiSkeleton /> : (
          <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
            <StatCard
              label="Total Companies"
              value={summary?.totalCompanies.toLocaleString() || '—'}
              change={summary?.changes.totalCompanies}
              icon={<Building2 className="w-5 h-5" />}
              iconBg="bg-primary-light"
            />
            <StatCard
              label="Loans Assessed"
              value={summary?.loansAssessed.toLocaleString() || '—'}
              change={summary?.changes.loansAssessed}
              icon={<BarChart2 className="w-5 h-5" />}
              iconBg="bg-info-light"
            />
            <StatCard
              label="High Risk Companies"
              value={summary?.highRiskCompanies.toLocaleString() || '—'}
              change={summary?.changes.highRiskCompanies}
              icon={<AlertTriangle className="w-5 h-5" />}
              iconBg="bg-danger-light"
            />
            <StatCard
              label="Avg Default Probability"
              value={`${summary?.avgDefaultProbability.toFixed(1) || '—'}%`}
              change={summary?.changes.avgDefaultProbability}
              icon={<TrendingUp className="w-5 h-5" />}
              iconBg="bg-warning-light"
            />
            <StatCard
              label="Model Accuracy (GNN)"
              value={`${summary?.modelAccuracy.toFixed(1) || '—'}%`}
              icon={<Cpu className="w-5 h-5" />}
              iconBg="bg-success-light"
            />
            <StatCard
              label="Network Risk Alerts"
              value={summary?.networkRiskAlerts.toLocaleString() || '—'}
              icon={<Network className="w-5 h-5" />}
              iconBg="bg-primary-light"
            />
          </div>
        )}
      </motion.div>

      {/* Charts Row 1: Risk Distribution + Trend */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        {/* Risk Distribution */}
        <motion.div variants={itemVariants} className="xl:col-span-2">
          <Card className="h-full">
            <SectionHeader
              title="Loan Default Risk Distribution"
              subtitle={distribution ? `${distribution.total.toLocaleString()} companies assessed` : ''}
            />
            {loading ? (
              <div className="flex items-center justify-center h-48"><Skeleton className="w-36 h-36 rounded-full" /></div>
            ) : (
              <div>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {donutData.map((entry, idx) => (
                        <Cell key={idx} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      content={({ active, payload }) => active && payload?.length ? (
                        <div className="bg-white border border-surface-200 rounded-xl shadow-dropdown p-3">
                          <p className="text-xs font-semibold" style={{ color: payload[0].payload.color }}>
                            {payload[0].name}
                          </p>
                          <p className="text-sm font-bold text-content-primary">{payload[0].value}</p>
                          <p className="text-xs text-content-tertiary">
                            {((payload[0].value as number / (distribution?.total || 1)) * 100).toFixed(1)}%
                          </p>
                        </div>
                      ) : null}
                    />
                  </PieChart>
                </ResponsiveContainer>
                {/* Legend */}
                <div className="space-y-2 mt-2">
                  {donutData.map(d => (
                    <div key={d.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                        <span className="text-xs text-content-secondary">{d.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-content-primary tabular-nums">{d.value}</span>
                        <span className="text-xs text-content-tertiary tabular-nums">
                          ({((d.value / (distribution?.total || 1)) * 100).toFixed(0)}%)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </motion.div>

        {/* Default Probability Trend */}
        <motion.div variants={itemVariants} className="xl:col-span-3">
          <Card className="h-full">
            <div className="flex items-center justify-between mb-4">
              <SectionHeader title="Default Probability Trend" subtitle="Average across monitored portfolio" />
              <div className="flex gap-1">
                {TREND_PERIODS.map(p => (
                  <button
                    key={p}
                    onClick={() => setTrendPeriod(p)}
                    className={clsx(
                      'text-xs px-2.5 py-1 rounded-md font-medium transition-all',
                      trendPeriod === p
                        ? 'bg-primary text-white'
                        : 'text-content-secondary hover:bg-surface-100'
                    )}
                  >
                    {p.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            {chartTrend.length === 0 ? (
              <div className="flex items-center justify-center h-48">
                <Skeleton className="w-full h-40" />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={chartTrend} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="probGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 10, fill: '#9CA3AF' }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={v => {
                      const d = new Date(v);
                      return `${d.getDate()}/${d.getMonth() + 1}`;
                    }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: '#9CA3AF' }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={v => `${v}%`}
                    domain={[0, 80]}
                  />
                  <Tooltip content={<CustomTooltipLine />} />
                  <Area
                    type="monotone"
                    dataKey="probability"
                    stroke="#F59E0B"
                    strokeWidth={2}
                    fill="url(#probGrad)"
                    dot={false}
                    activeDot={{ r: 4, fill: '#F59E0B' }}
                    name="Default Probability"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Card>
        </motion.div>
      </div>

      {/* Charts Row 2: Risk Factors + Network Insights */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* Key Risk Drivers */}
        <motion.div variants={itemVariants}>
          <Card className="h-full">
            <SectionHeader
              title="Key Risk Drivers"
              subtitle="Feature importance from GNN model"
              actions={<Button variant="ghost" size="sm">Details</Button>}
            />
            {loading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-6" />)}
              </div>
            ) : (
              <div className="space-y-3">
                {riskFactors.map((f, i) => (
                  <div key={f.name}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-content-primary">{f.name}</span>
                      <span className="text-xs font-semibold text-content-secondary tabular-nums">{f.contribution}%</span>
                    </div>
                    <ProgressBar
                      value={f.contribution}
                      color={i < 3 ? '#F59E0B' : '#94A3B8'}
                    />
                  </div>
                ))}
              </div>
            )}
          </Card>
        </motion.div>

        {/* Network Risk Summary */}
        <motion.div variants={itemVariants}>
          <Card className="h-full">
            <SectionHeader
              title="Network Risk Insights"
              subtitle="Maritime financial network overview"
              actions={
                <Button variant="ghost" size="sm" onClick={() => navigate('/network-analysis')}>
                  View Map
                </Button>
              }
            />
            {loading ? (
              <div className="space-y-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16" />)}</div>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {[
                    { label: 'Network Density', value: '0.18', sub: 'Moderate connectivity' },
                    { label: 'Avg Centrality', value: '0.54', sub: 'Above threshold' },
                    { label: 'High-Risk Clusters', value: '12', sub: 'Requires monitoring' },
                    { label: 'Contagion Risk', value: 'ELEVATED', sub: '3 key nodes' },
                  ].map(m => (
                    <div key={m.label} className="bg-surface-50 rounded-xl p-3 border border-surface-200">
                      <p className="text-2xs text-content-tertiary uppercase tracking-wider">{m.label}</p>
                      <p className={clsx(
                        'text-sm font-bold mt-1',
                        m.value === 'ELEVATED' ? 'text-warning' : 'text-content-primary'
                      )}>{m.value}</p>
                      <p className="text-2xs text-content-tertiary mt-0.5">{m.sub}</p>
                    </div>
                  ))}
                </div>
                {/* Mini bar chart */}
                <ResponsiveContainer width="100%" height={100}>
                  <BarChart
                    data={[
                      { type: 'Financial', count: 48 },
                      { type: 'Correlation', count: 32 },
                      { type: 'Contractual', count: 19 },
                    ]}
                    margin={{ top: 4, right: 4, bottom: 0, left: -20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
                    <XAxis dataKey="type" tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false} />
                    <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false} />
                    <Tooltip content={<CustomTooltipBar />} />
                    <Bar dataKey="count" fill="#F59E0B" radius={[4, 4, 0, 0]} name="Connections" />
                  </BarChart>
                </ResponsiveContainer>
              </>
            )}
          </Card>
        </motion.div>
      </div>

      {/* High Risk Companies Table */}
      <motion.div variants={itemVariants}>
        <Card padding={false}>
          <div className="p-5 border-b border-surface-200">
            <SectionHeader
              title="High-Risk Companies"
              subtitle="Companies requiring immediate attention"
              actions={
                <Button variant="secondary" size="sm" onClick={() => navigate('/companies')}>
                  View All Companies
                </Button>
              }
            />
          </div>
          {loading ? (
            <div className="p-5 space-y-3">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10" />)}
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Loan Amount</th>
                    <th>Vessel Value</th>
                    <th>Debt/Equity</th>
                    <th>Default Prob.</th>
                    <th>Risk</th>
                    <th>Network Risk</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {highRisk.map(c => (
                    <tr key={c.id}>
                      <td>
                        <div>
                          <p className="font-medium text-content-primary">{c.name}</p>
                          <p className="text-2xs text-content-tertiary">{c.id} · {c.country}</p>
                        </div>
                      </td>
                      <td className="tabular-nums font-medium">{formatCurrency(c.loanAmount)}</td>
                      <td className="tabular-nums">{formatCurrency(c.vesselValue)}</td>
                      <td className="tabular-nums font-medium text-danger">{c.debtToEquity.toFixed(1)}x</td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-surface-100 rounded-full h-1.5">
                            <div
                              className="h-1.5 rounded-full"
                              style={{
                                width: `${c.defaultProbability * 100}%`,
                                backgroundColor: getRiskHex(c.riskCategory),
                              }}
                            />
                          </div>
                          <span className="text-xs font-semibold tabular-nums" style={{ color: getRiskHex(c.riskCategory) }}>
                            {formatPercentRaw(c.defaultProbability * 100)}
                          </span>
                        </div>
                      </td>
                      <td><RiskBadge risk={c.riskCategory} /></td>
                      <td>
                        <span className={clsx('text-xs font-medium', getNetworkExposureColor(c.networkRisk))}>
                          {c.networkRisk}
                        </span>
                      </td>
                      <td>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            leftIcon={<Eye className="w-3 h-3" />}
                            onClick={() => navigate(`/companies/${c.id}`)}
                          >
                            View
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
