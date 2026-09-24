import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Building2, TrendingUp, Ship, Network, Atom, History, Lightbulb, Download } from 'lucide-react';
import {
  Card, PageHeader, Button, RiskBadge, Tabs, Skeleton, SectionHeader,
} from '@/components/ui';
import { companyApi } from '@/api/companyApi';
import type { CompanyDetail } from '@/types';
import {
  formatCurrency, formatPercent, formatDate, getRiskHex, clsx,
} from '@/utils';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis,
} from 'recharts';

const CompanyDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('overview');

  useEffect(() => {
    if (!id) return;
    companyApi.getById(id).then(d => {
      setCompany(d);
      setLoading(false);
    });
  }, [id]);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Building2 className="w-3.5 h-3.5" /> },
    { id: 'financial', label: 'Financial', icon: <TrendingUp className="w-3.5 h-3.5" /> },
    { id: 'vessels', label: 'Vessels', icon: <Ship className="w-3.5 h-3.5" /> },
    { id: 'network', label: 'Network', icon: <Network className="w-3.5 h-3.5" /> },
    { id: 'tda', label: 'TDA Features', icon: <Atom className="w-3.5 h-3.5" /> },
    { id: 'predictions', label: 'Predictions', icon: <History className="w-3.5 h-3.5" /> },
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Skeleton className="h-8 w-8" />
          <Skeleton className="h-8 w-48" />
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[1,2,3].map(i => <Skeleton key={i} className="h-24 rounded-xl" />)}
        </div>
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  if (!company) return (
    <div className="text-center py-20 text-content-secondary">Company not found.</div>
  );

  const riskColor = getRiskHex(company.riskCategory);

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate('/companies')} aria-label="Back">
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="page-title">{company.name}</h1>
              <RiskBadge risk={company.riskCategory} />
            </div>
            <p className="page-subtitle">{company.id} · {company.country} · {company.segment}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>Export Report</Button>
          <Button size="sm" leftIcon={<TrendingUp className="w-3.5 h-3.5" />} onClick={() => navigate('/prediction')}>
            New Prediction
          </Button>
        </div>
      </div>

      {/* Quick KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {[
          { label: 'Default Probability', value: `${(company.defaultProbability * 100).toFixed(1)}%`, sub: company.riskCategory, color: riskColor },
          { label: 'Loan Amount', value: formatCurrency(company.loanAmount), sub: 'Outstanding loan' },
          { label: 'Vessel Value', value: formatCurrency(company.vesselValue), sub: `${company.fleetSize} vessels` },
          { label: 'Debt / Equity', value: `${company.debtToEquity.toFixed(2)}x`, sub: company.debtToEquity > 3 ? 'Above threshold' : 'Within range' },
        ].map(m => (
          <Card key={m.label}>
            <p className="stat-label">{m.label}</p>
            <p className="stat-value mt-1" style={m.color ? { color: m.color } : {}}>{m.value}</p>
            <p className={clsx('text-xs mt-1', m.color ? '' : 'text-content-tertiary')} style={m.color ? { color: m.color } : {}}>
              {m.sub}
            </p>
          </Card>
        ))}
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} active={tab} onChange={setTab} className="overflow-x-auto" />

      {/* Tab Content */}
      <AnimatedTabContent>
        {tab === 'overview' && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {/* Risk Timeline */}
            <Card className="xl:col-span-2">
              <SectionHeader title="Risk Timeline" subtitle="Default probability over 12 months" />
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={company.riskTimeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                    tickFormatter={v => { const d = new Date(v); return `${d.getMonth()+1}/${d.getFullYear().toString().slice(2)}`; }}
                  />
                  <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                    tickFormatter={v => `${(v*100).toFixed(0)}%`} />
                  <Tooltip formatter={(v: number) => [`${(v*100).toFixed(1)}%`, 'Default Prob.']} />
                  <Line type="monotone" dataKey="probability" stroke={riskColor} strokeWidth={2} dot={false}
                    activeDot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            {/* Company Info */}
            <Card>
              <SectionHeader title="Company Profile" />
              <div className="space-y-3">
                {[
                  { label: 'Company ID', value: company.id },
                  { label: 'Country', value: company.country },
                  { label: 'Segment', value: company.segment },
                  { label: 'Status', value: company.status },
                  { label: 'Fleet Size', value: `${company.fleetSize} vessels` },
                ].map(r => (
                  <div key={r.label} className="flex justify-between py-1.5 border-b border-surface-100 last:border-0">
                    <span className="text-xs text-content-secondary">{r.label}</span>
                    <span className="text-xs font-medium text-content-primary capitalize">{r.value}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Loan Info */}
            <Card>
              <SectionHeader title="Loan Summary" />
              <div className="space-y-3">
                {[
                  { label: 'Loan ID', value: company.loan.loanId },
                  { label: 'Type', value: company.loan.loanType },
                  { label: 'Amount', value: formatCurrency(company.loan.amount) },
                  { label: 'Interest Rate', value: `${company.loan.interestRate}%` },
                  { label: 'Maturity', value: formatDate(company.loan.maturityDate) },
                  { label: 'LTV Ratio', value: `${(company.loan.ltvRatio * 100).toFixed(1)}%` },
                ].map(r => (
                  <div key={r.label} className="flex justify-between py-1.5 border-b border-surface-100 last:border-0">
                    <span className="text-xs text-content-secondary">{r.label}</span>
                    <span className="text-xs font-medium text-content-primary">{r.value}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {tab === 'financial' && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <Card>
              <SectionHeader title="Income Statement" />
              <div className="space-y-2">
                {[
                  { label: 'Revenue', value: formatCurrency(company.financials.revenue) },
                  { label: 'Net Income', value: formatCurrency(company.financials.netIncome) },
                  { label: 'Total Assets', value: formatCurrency(company.financials.totalAssets) },
                  { label: 'Total Liabilities', value: formatCurrency(company.financials.totalLiabilities) },
                  { label: 'Equity', value: formatCurrency(company.financials.equity) },
                ].map(r => (
                  <div key={r.label} className="flex justify-between py-2 border-b border-surface-100 last:border-0">
                    <span className="text-xs text-content-secondary">{r.label}</span>
                    <span className="text-xs font-semibold text-content-primary tabular-nums">{r.value}</span>
                  </div>
                ))}
              </div>
            </Card>
            <Card>
              <SectionHeader title="Financial Ratios" />
              <div className="space-y-2">
                {[
                  { label: 'Current Ratio', value: company.financials.currentRatio.toFixed(2) },
                  { label: 'Quick Ratio', value: company.financials.quickRatio.toFixed(2) },
                  { label: 'Interest Coverage', value: company.financials.interestCoverageRatio.toFixed(2) },
                  { label: 'Return on Assets', value: `${company.financials.returnOnAssets.toFixed(1)}%` },
                  { label: 'Return on Equity', value: `${company.financials.returnOnEquity.toFixed(1)}%` },
                ].map(r => (
                  <div key={r.label} className="flex justify-between py-2 border-b border-surface-100 last:border-0">
                    <span className="text-xs text-content-secondary">{r.label}</span>
                    <span className="text-xs font-semibold text-content-primary tabular-nums">{r.value}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {tab === 'vessels' && (
          <Card padding={false}>
            <div className="p-5 border-b border-surface-200">
              <SectionHeader title="Fleet Registry" subtitle={`${company.vessels.length} vessels`} />
            </div>
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Vessel Name</th>
                    <th>Type</th>
                    <th>Age</th>
                    <th>Value</th>
                    <th>DWT</th>
                    <th>Utilization</th>
                    <th>Flag</th>
                  </tr>
                </thead>
                <tbody>
                  {company.vessels.map(v => (
                    <tr key={v.id}>
                      <td className="font-medium">{v.name}</td>
                      <td><span className="badge-neutral badge">{v.type}</span></td>
                      <td className="tabular-nums">{v.age} years</td>
                      <td className="tabular-nums">{formatCurrency(v.value)}</td>
                      <td className="tabular-nums">{v.dwt.toLocaleString()}</td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-surface-100 rounded-full h-1.5">
                            <div className="h-1.5 rounded-full bg-primary" style={{ width: `${v.utilization * 100}%` }} />
                          </div>
                          <span className="text-xs tabular-nums">{(v.utilization * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="text-xs">{v.flag}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {tab === 'network' && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <Card>
              <SectionHeader title="Network Position Metrics" />
              <div className="space-y-4">
                {[
                  { label: 'Centrality', value: company.networkPosition.centrality },
                  { label: 'Betweenness', value: company.networkPosition.betweenness },
                  { label: 'Closeness', value: company.networkPosition.closeness },
                  { label: 'Clustering Coeff.', value: company.networkPosition.clusteringCoefficient },
                ].map(m => (
                  <div key={m.label}>
                    <div className="flex justify-between mb-1">
                      <span className="text-xs text-content-secondary">{m.label}</span>
                      <span className="text-xs font-semibold tabular-nums">{m.value.toFixed(3)}</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-bar-fill bg-primary" style={{ width: `${m.value * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
            <Card>
              <SectionHeader title="Network Summary" />
              <div className="space-y-3">
                {[
                  { label: 'Degree Centrality', value: company.networkPosition.degree },
                  { label: 'Connected Companies', value: company.networkPosition.connectedCompanies },
                  { label: 'Network Exposure', value: company.networkPosition.networkExposure },
                ].map(r => (
                  <div key={r.label} className="flex justify-between py-2 border-b border-surface-100 last:border-0">
                    <span className="text-xs text-content-secondary">{r.label}</span>
                    <span className="text-xs font-semibold text-content-primary">{r.value}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {tab === 'tda' && (
          <div className="grid grid-cols-2 xl:grid-cols-3 gap-4">
            {[
              { label: 'Connected Components (β₀)', value: company.tdaFeatures.bettiNumbers.b0 },
              { label: 'Cycles (β₁)', value: company.tdaFeatures.bettiNumbers.b1 },
              { label: 'Voids (β₂)', value: company.tdaFeatures.bettiNumbers.b2 },
              { label: 'Total Persistence', value: company.tdaFeatures.totalPersistence.toFixed(2) },
              { label: 'Average Persistence', value: company.tdaFeatures.averagePersistence.toFixed(2) },
              { label: 'Max Persistence', value: company.tdaFeatures.maxPersistence.toFixed(2) },
              { label: 'Topological Complexity', value: company.tdaFeatures.topologicalComplexity.toFixed(3) },
              { label: 'Wasserstein Distance', value: company.tdaFeatures.wasserstein.toFixed(3) },
              { label: 'Bottleneck Distance', value: company.tdaFeatures.bottleneck.toFixed(3) },
            ].map(m => (
              <Card key={m.label}>
                <p className="text-2xs text-content-tertiary uppercase tracking-wider">{m.label}</p>
                <p className="text-xl font-bold text-content-primary tabular-nums mt-1">{m.value}</p>
              </Card>
            ))}
          </div>
        )}

        {tab === 'predictions' && (
          <Card>
            <SectionHeader title="Prediction History" subtitle="Past risk assessments for this company" />
            <div className="empty-state">
              <History className="w-12 h-12 text-content-tertiary" />
              <p className="empty-state-title">No predictions yet</p>
              <p className="empty-state-desc">Run a risk assessment to see prediction history here.</p>
              <Button size="sm" onClick={() => navigate('/prediction')}>Run Prediction</Button>
            </div>
          </Card>
        )}
      </AnimatedTabContent>
    </motion.div>
  );
};

const AnimatedTabContent: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <motion.div
    key={Math.random()}
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.2 }}
  >
    {children}
  </motion.div>
);

export default CompanyDetails;
