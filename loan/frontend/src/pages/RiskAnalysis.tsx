import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, TrendingDown, Shield } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, Cell,
} from 'recharts';
import { Card, PageHeader, SectionHeader, RiskBadge } from '@/components/ui';
import { mockCompanies, mockRiskFactors } from '@/services/mock/mockData';
import { formatCurrency, getRiskHex, clsx } from '@/utils';

const RiskAnalysis: React.FC = () => {
  const high = mockCompanies.filter(c => c.riskCategory === 'HIGH');
  const medium = mockCompanies.filter(c => c.riskCategory === 'MEDIUM');
  const low = mockCompanies.filter(c => c.riskCategory === 'LOW');

  const segmentData = ['Bulk Carrier', 'Container Shipping', 'Tanker', 'LNG Carrier', 'Ro-Ro'].map(seg => {
    const companies = mockCompanies.filter(c => c.segment === seg);
    const avgProb = companies.length
      ? companies.reduce((s, c) => s + c.defaultProbability, 0) / companies.length * 100
      : 0;
    return { segment: seg, avgProbability: parseFloat(avgProb.toFixed(1)), count: companies.length };
  });

  const countryData = ['Greece', 'Norway', 'Germany', 'Singapore', 'Japan'].map(country => {
    const companies = mockCompanies.filter(c => c.country === country);
    const high = companies.filter(c => c.riskCategory === 'HIGH').length;
    return { country, total: companies.length, high, rate: companies.length ? (high / companies.length * 100).toFixed(0) : 0 };
  });

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Risk Analysis"
        subtitle="Portfolio-level risk distribution, segment analysis, and concentration risk"
        breadcrumb={['Risk Analysis']}
      />

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'High Risk', value: high.length, pct: ((high.length / mockCompanies.length) * 100).toFixed(1), color: '#DC2626', bg: 'bg-danger-light' },
          { label: 'Medium Risk', value: medium.length, pct: ((medium.length / mockCompanies.length) * 100).toFixed(1), color: '#F59E0B', bg: 'bg-warning-light' },
          { label: 'Low Risk', value: low.length, pct: ((low.length / mockCompanies.length) * 100).toFixed(1), color: '#16A34A', bg: 'bg-success-light' },
        ].map(m => (
          <Card key={m.label}>
            <div className={clsx('inline-flex items-center justify-center w-10 h-10 rounded-xl mb-3', m.bg)}>
              <Shield className="w-5 h-5" style={{ color: m.color }} />
            </div>
            <p className="text-2xl font-bold tabular-nums" style={{ color: m.color }}>{m.value}</p>
            <p className="text-sm font-medium text-content-secondary mt-0.5">{m.label}</p>
            <p className="text-xs text-content-tertiary mt-1">{m.pct}% of portfolio</p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* Segment analysis */}
        <Card>
          <SectionHeader title="Risk by Vessel Segment" subtitle="Average default probability per segment" />
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={segmentData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
              <XAxis dataKey="segment" tick={{ fontSize: 9, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                tickFormatter={v => v.split(' ')[0]} />
              <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                tickFormatter={v => `${v}%`} />
              <Tooltip formatter={(v: number) => [`${v}%`, 'Avg Default Prob.']} />
              <Bar dataKey="avgProbability" radius={[4, 4, 0, 0]} name="Avg Probability">
                {segmentData.map((entry, i) => (
                  <Cell key={i} fill={entry.avgProbability > 40 ? '#DC2626' : entry.avgProbability > 25 ? '#F59E0B' : '#16A34A'} fillOpacity={0.8} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Country analysis */}
        <Card>
          <SectionHeader title="Risk by Country" subtitle="High-risk company count per country" />
          <div className="space-y-3 mt-2">
            {countryData.map(c => (
              <div key={c.country}>
                <div className="flex justify-between mb-1">
                  <span className="text-xs font-medium text-content-primary">{c.country}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-content-secondary">{c.high}/{c.total}</span>
                    <span className="text-xs font-semibold text-danger tabular-nums">{c.rate}%</span>
                  </div>
                </div>
                <div className="progress-bar">
                  <div className="progress-bar-fill bg-danger" style={{ width: `${c.rate}%`, opacity: 0.7 }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Risk factors */}
      <Card>
        <SectionHeader title="Portfolio Risk Factor Heatmap" subtitle="Contribution to overall portfolio risk" />
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {mockRiskFactors.map((f, i) => (
            <div key={f.name}>
              <div className="flex justify-between mb-1">
                <span className="text-xs font-medium text-content-primary">{f.name}</span>
                <span className="text-xs font-semibold tabular-nums">{f.contribution}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${f.contribution}%`, backgroundColor: i < 3 ? '#F59E0B' : '#94A3B8' }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </motion.div>
  );
};

export default RiskAnalysis;
