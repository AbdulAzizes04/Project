import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, TrendingUp, TrendingDown, Info } from 'lucide-react';
import { Card, PageHeader, SectionHeader, RiskBadge, ProgressBar, Spinner } from '@/components/ui';
import { mockPredictionHistory } from '@/services/mock/mockData';
import { generatePredictionResult } from '@/services/mock/mockData';
import type { PredictionResult, ShapValue } from '@/types';
import { formatPercentRaw, getRiskHex, getModelDisplayName, formatDateTime, clsx } from '@/utils';

// Simulate some pre-computed explainability results
const DEMO_RESULTS: PredictionResult[] = [0, 1, 2].map(i => {
  const hist = mockPredictionHistory[i];
  return {
    id: hist.id,
    companyName: hist.companyName,
    defaultProbability: hist.defaultProbability,
    riskCategory: hist.riskCategory,
    confidence: hist.confidence,
    modelUsed: hist.modelUsed,
    timestamp: hist.date,
    contributingFactors: [
      { name: 'Debt-to-Equity Ratio', value: 3.8, impact: 'HIGH', direction: 'positive', contribution: 38 },
      { name: 'Vessel Age', value: '14 years', impact: 'HIGH', direction: 'positive', contribution: 27 },
      { name: 'Interest Rate', value: '7.2%', impact: 'MEDIUM', direction: 'positive', contribution: 18 },
      { name: 'Vessel Utilization', value: '71%', impact: 'MEDIUM', direction: 'positive', contribution: 12 },
      { name: 'Freight Market Rate', value: '$950/day', impact: 'MEDIUM', direction: 'positive', contribution: 10 },
      { name: 'Network Centrality', value: 0.72, impact: 'HIGH', direction: 'positive', contribution: 22 },
      { name: 'Clustering Coefficient', value: 0.55, impact: 'LOW', direction: 'negative', contribution: -8 },
      { name: 'Economic Growth', value: '2.8%', impact: 'LOW', direction: 'negative', contribution: -6 },
    ],
    networkRisk: {
      centrality: 0.72, degree: 14, betweenness: 0.31,
      closeness: 0.62, clusteringCoefficient: 0.55,
      connectedCompanies: 14, networkExposure: 'ELEVATED',
    },
    shapValues: [
      { feature: 'Debt-to-Equity Ratio', value: 3.8, shapValue: 0.142, direction: 'increases' },
      { feature: 'Network Centrality', value: 0.72, shapValue: 0.118, direction: 'increases' },
      { feature: 'Vessel Age', value: 14, shapValue: 0.094, direction: 'increases' },
      { feature: 'Interest Rate', value: 7.2, shapValue: 0.071, direction: 'increases' },
      { feature: 'Freight Rate', value: 950, shapValue: 0.058, direction: 'increases' },
      { feature: 'Vessel Utilization', value: 0.71, shapValue: -0.042, direction: 'decreases' },
      { feature: 'Clustering Coeff.', value: 0.55, shapValue: -0.031, direction: 'decreases' },
      { feature: 'Economic Growth', value: 2.8, shapValue: -0.022, direction: 'decreases' },
    ],
  };
});

const ShapBar: React.FC<{ sv: ShapValue }> = ({ sv }) => {
  const isPos = sv.direction === 'increases';
  const pct = Math.abs(sv.shapValue) * 300;
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-content-primary w-44 flex-shrink-0">{sv.feature}</span>
      <div className="flex-1 relative h-6 flex items-center">
        <div className="w-full flex items-center">
          {isPos ? (
            <>
              <div className="flex-1" />
              <div
                className="h-4 rounded-r-sm flex items-center px-1.5"
                style={{ width: `${Math.min(pct, 50)}%`, backgroundColor: '#FEE2E2' }}
              >
                <TrendingUp className="w-3 h-3 text-danger flex-shrink-0" />
              </div>
            </>
          ) : (
            <>
              <div
                className="h-4 rounded-l-sm flex items-center justify-end px-1.5"
                style={{ width: `${Math.min(pct, 50)}%`, backgroundColor: '#DCFCE7' }}
              >
                <TrendingDown className="w-3 h-3 text-success flex-shrink-0" />
              </div>
              <div className="flex-1" />
            </>
          )}
        </div>
      </div>
      <span className={clsx('text-xs font-semibold w-16 text-right tabular-nums', isPos ? 'text-danger' : 'text-success')}>
        {isPos ? '+' : ''}{sv.shapValue.toFixed(4)}
      </span>
      <span className="text-xs text-content-secondary w-12 text-right tabular-nums">{sv.value}</span>
    </div>
  );
};

const Explainability: React.FC = () => {
  const [selected, setSelected] = useState(0);
  const result = DEMO_RESULTS[selected];

  const positive = result.shapValues?.filter(s => s.direction === 'increases')
    .sort((a, b) => b.shapValue - a.shapValue) || [];
  const negative = result.shapValues?.filter(s => s.direction === 'decreases')
    .sort((a, b) => a.shapValue - b.shapValue) || [];

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Prediction Explainability"
        subtitle="SHAP-based feature attribution — understand why each company was classified at its risk level"
        breadcrumb={['Explainability']}
      />

      {/* Info */}
      <div className="bg-primary-light border border-primary/20 rounded-xl p-4 flex gap-3">
        <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
        <p className="text-xs text-content-secondary">
          <strong className="text-content-primary">SHAP (SHapley Additive exPlanations)</strong> decomposes the prediction into contributions from each feature.
          Positive SHAP values increase the default probability (red bars). Negative SHAP values decrease it (green bars).
          The base value is the average prediction across the training set.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Selector */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-content-secondary uppercase tracking-wider mb-2">Recent Predictions</p>
          {DEMO_RESULTS.map((r, i) => (
            <button
              key={r.id}
              onClick={() => setSelected(i)}
              className={clsx(
                'w-full text-left p-3 rounded-xl border transition-all',
                selected === i
                  ? 'border-primary bg-primary-light'
                  : 'border-surface-200 bg-white hover:bg-surface-50'
              )}
            >
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-semibold text-content-primary truncate">{r.companyName}</p>
                <RiskBadge risk={r.riskCategory} />
              </div>
              <p className="text-xs text-content-secondary">
                {formatPercentRaw(r.defaultProbability * 100)} · {getModelDisplayName(r.modelUsed)}
              </p>
            </button>
          ))}
        </div>

        {/* SHAP waterfall */}
        <div className="xl:col-span-2 space-y-4">
          {/* Header */}
          <Card>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-sm font-bold text-content-primary">{result.companyName}</h3>
                <p className="text-xs text-content-secondary mt-0.5">{formatDateTime(result.timestamp)}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold tabular-nums" style={{ color: getRiskHex(result.riskCategory) }}>
                  {formatPercentRaw(result.defaultProbability * 100)}
                </p>
                <RiskBadge risk={result.riskCategory} />
              </div>
            </div>
          </Card>

          {/* SHAP chart */}
          <Card>
            <SectionHeader
              title="SHAP Feature Attribution"
              subtitle={`${positive.length} positive · ${negative.length} negative contributors`}
            />
            <div className="space-y-1">
              {/* Center axis */}
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xs text-success font-semibold w-44">↓ Decreases Risk</span>
                <div className="flex-1 text-center text-2xs text-content-tertiary">SHAP Value</div>
                <span className="text-2xs text-danger font-semibold w-28 text-right">↑ Increases Risk</span>
              </div>
              {result.shapValues?.map(sv => <ShapBar key={sv.feature} sv={sv} />)}
            </div>
          </Card>

          {/* Contributors */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <Card>
              <SectionHeader title="Risk-Increasing Factors" />
              <div className="space-y-2">
                {positive.slice(0, 5).map((sv, i) => (
                  <div key={sv.feature} className="flex items-center gap-2">
                    <span className="badge badge-danger text-2xs w-5 h-5 flex items-center justify-center p-0 rounded-full flex-shrink-0">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-content-primary truncate">{sv.feature}</p>
                      <p className="text-2xs text-danger">+{sv.shapValue.toFixed(4)} SHAP</p>
                    </div>
                    <span className="text-xs text-content-secondary tabular-nums">{sv.value}</span>
                  </div>
                ))}
              </div>
            </Card>
            <Card>
              <SectionHeader title="Risk-Reducing Factors" />
              <div className="space-y-2">
                {negative.slice(0, 5).map((sv, i) => (
                  <div key={sv.feature} className="flex items-center gap-2">
                    <span className="badge badge-success text-2xs w-5 h-5 flex items-center justify-center p-0 rounded-full flex-shrink-0">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-content-primary truncate">{sv.feature}</p>
                      <p className="text-2xs text-success">{sv.shapValue.toFixed(4)} SHAP</p>
                    </div>
                    <span className="text-xs text-content-secondary tabular-nums">{sv.value}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Explainability;
