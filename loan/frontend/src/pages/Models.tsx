import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, CheckCircle, TrendingUp, Cpu } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis,
} from 'recharts';
import { Card, PageHeader, SectionHeader, Skeleton, RiskBadge } from '@/components/ui';
import { modelApi } from '@/api/modelApi';
import type { ModelMetrics } from '@/types';
import { getModelColor, getModelDisplayName, clsx } from '@/utils';

const MODELS: ModelMetrics['model'][] = ['logistic_regression', 'svm', 'xgboost', 'gnn'];
const MODEL_COLORS = {
  logistic_regression: '#6B7280',
  svm: '#2563EB',
  xgboost: '#16A34A',
  gnn: '#F59E0B',
};

const MetricPill: React.FC<{ label: string; value: number; color?: string }> = ({ label, value, color = '#F59E0B' }) => (
  <div className="text-center p-3 bg-surface-50 rounded-xl border border-surface-200">
    <p className="text-2xs text-content-tertiary uppercase tracking-wider">{label}</p>
    <p className="text-xl font-bold tabular-nums mt-1" style={{ color }}>{(value * 100).toFixed(1)}%</p>
  </div>
);

const Models: React.FC = () => {
  const [metrics, setMetrics] = useState<ModelMetrics[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    modelApi.getAll().then(m => { setMetrics(m); setLoading(false); });
  }, []);

  const radarData = ['accuracy', 'precision', 'recall', 'f1Score', 'rocAuc'].map(key => ({
    metric: key === 'f1Score' ? 'F1' : key === 'rocAuc' ? 'ROC-AUC' : key.charAt(0).toUpperCase() + key.slice(1),
    ...Object.fromEntries(metrics.map(m => [m.modelName.split(' ')[0], (m as any)[key] * 100])),
  }));

  const barData = metrics.map(m => ({
    name: m.modelName.split(' ').length > 2 ? m.modelName.split(' ').slice(-1)[0] : m.modelName.split(' ')[0],
    Accuracy: parseFloat((m.accuracy * 100).toFixed(1)),
    Precision: parseFloat((m.precision * 100).toFixed(1)),
    Recall: parseFloat((m.recall * 100).toFixed(1)),
    F1: parseFloat((m.f1Score * 100).toFixed(1)),
    'ROC-AUC': parseFloat((m.rocAuc * 100).toFixed(1)),
    color: MODEL_COLORS[m.model],
  }));

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Machine Learning Model Comparison"
        subtitle="Performance comparison across all trained models for maritime loan default prediction"
        breadcrumb={['Models']}
      />

      {/* Comparison Table */}
      <Card padding={false}>
        <div className="p-5 border-b border-surface-200">
          <SectionHeader title="Model Performance Comparison" subtitle="Evaluated on held-out test set" />
        </div>
        {loading ? (
          <div className="p-5 space-y-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12" />)}</div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th className="text-right">Accuracy</th>
                  <th className="text-right">Precision</th>
                  <th className="text-right">Recall</th>
                  <th className="text-right">F1 Score</th>
                  <th className="text-right">ROC-AUC</th>
                  <th className="text-right">AUC-PR</th>
                  <th className="text-right">Train Time</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((m, i) => {
                  const isBest = m.model === 'gnn';
                  return (
                    <tr key={m.model} className={isBest ? 'bg-primary-light/30' : ''}>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: MODEL_COLORS[m.model] }} />
                          <span className="font-medium">{m.modelName}</span>
                          {isBest && <span className="badge badge-primary text-2xs">Best</span>}
                        </div>
                      </td>
                      {['accuracy', 'precision', 'recall', 'f1Score', 'rocAuc', 'aucPr'].map(key => {
                        const val = (m as any)[key] as number;
                        const isHighlight = val > 0.9;
                        return (
                          <td key={key} className="text-right tabular-nums">
                            <span className={clsx('font-semibold', isHighlight ? 'text-success' : 'text-content-primary')}>
                              {(val * 100).toFixed(1)}%
                            </span>
                          </td>
                        );
                      })}
                      <td className="text-right text-xs tabular-nums text-content-secondary">
                        {m.trainingTime < 60 ? `${m.trainingTime}s` : `${(m.trainingTime / 60).toFixed(1)}m`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* Bar comparison */}
        <Card>
          <SectionHeader title="Performance Metrics Comparison" />
          {loading ? <Skeleton className="h-48" /> : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                  tickFormatter={v => `${v}%`} domain={[70, 100]} />
                <Tooltip formatter={(v: number) => `${v}%`} />
                <Legend wrapperStyle={{ fontSize: 10 }} />
                {['Accuracy', 'F1', 'ROC-AUC'].map((key, i) => (
                  <Bar key={key} dataKey={key} fill={['#F59E0B', '#16A34A', '#2563EB'][i]} radius={[3, 3, 0, 0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        {/* Radar chart */}
        <Card>
          <SectionHeader title="Multi-Metric Radar" subtitle="All models compared across 5 metrics" />
          {loading ? <Skeleton className="h-48" /> : (
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#E5E7EB" />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 10, fill: '#9CA3AF' }} />
                {metrics.map(m => (
                  <Radar
                    key={m.model}
                    name={m.modelName.split(' ').slice(-1)[0]}
                    dataKey={m.modelName.split(' ')[0]}
                    stroke={MODEL_COLORS[m.model]}
                    fill={MODEL_COLORS[m.model]}
                    fillOpacity={0.1}
                    strokeWidth={2}
                  />
                ))}
                <Legend wrapperStyle={{ fontSize: 10 }} />
                <Tooltip formatter={(v: number) => `${v.toFixed(1)}%`} />
              </RadarChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {/* Model cards */}
      {!loading && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {metrics.map(m => (
            <Card key={m.model}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: MODEL_COLORS[m.model] }} />
                  <h3 className="text-sm font-semibold text-content-primary">{m.modelName}</h3>
                  {m.model === 'gnn' && <span className="badge badge-primary text-2xs">Best Performer</span>}
                </div>
                <span className="text-xl font-bold text-success tabular-nums">{(m.rocAuc * 100).toFixed(1)}%</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <MetricPill label="Accuracy" value={m.accuracy} color={MODEL_COLORS[m.model]} />
                <MetricPill label="F1 Score" value={m.f1Score} color={MODEL_COLORS[m.model]} />
                <MetricPill label="Recall" value={m.recall} color={MODEL_COLORS[m.model]} />
              </div>
              {m.parameters > 0 && (
                <p className="text-2xs text-content-tertiary mt-3">
                  {m.parameters.toLocaleString()} parameters · {m.trainingTime}s training time
                </p>
              )}
            </Card>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default Models;
