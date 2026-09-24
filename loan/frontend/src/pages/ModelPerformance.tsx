import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, BarChart3 } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar, Cell, ReferenceLine,
} from 'recharts';
import { Card, PageHeader, SectionHeader, Skeleton, Tabs, Select } from '@/components/ui';
import { modelApi } from '@/api/modelApi';
import type { ModelMetrics, ROCPoint, PRPoint, ConfusionMatrix, FeatureImportance } from '@/types';
import { getModelDisplayName, clsx } from '@/utils';

const MODEL_OPTIONS = [
  { value: 'gnn', label: 'Graph Neural Network' },
  { value: 'xgboost', label: 'XGBoost' },
  { value: 'svm', label: 'Support Vector Machine' },
  { value: 'logistic_regression', label: 'Logistic Regression' },
];

const ConfMatrixViz: React.FC<{ cm: ConfusionMatrix }> = ({ cm }) => {
  const total = cm.tn + cm.fp + cm.fn + cm.tp;
  const cells = [
    { label: 'TN', value: cm.tn, bg: '#DCFCE7', text: '#166534', desc: 'True Negative' },
    { label: 'FP', value: cm.fp, bg: '#FEE2E2', text: '#991B1B', desc: 'False Positive' },
    { label: 'FN', value: cm.fn, bg: '#FEF3C7', text: '#92400E', desc: 'False Negative' },
    { label: 'TP', value: cm.tp, bg: '#DCFCE7', text: '#166534', desc: 'True Positive' },
  ];
  return (
    <div>
      <div className="grid grid-cols-2 gap-1 mb-3">
        <div className="text-center text-2xs text-content-tertiary py-1 bg-surface-50 rounded">Predicted: No Default</div>
        <div className="text-center text-2xs text-content-tertiary py-1 bg-surface-50 rounded">Predicted: Default</div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {cells.map(c => (
          <div key={c.label} className="rounded-xl p-4 text-center" style={{ backgroundColor: c.bg }}>
            <p className="text-xs font-semibold" style={{ color: c.text }}>{c.desc}</p>
            <p className="text-2xl font-bold tabular-nums mt-1" style={{ color: c.text }}>{c.value}</p>
            <p className="text-2xs mt-0.5" style={{ color: c.text }}>{((c.value / total) * 100).toFixed(1)}%</p>
          </div>
        ))}
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2">
        {[
          { label: 'Sensitivity (Recall)', value: `${((cm.tp / (cm.tp + cm.fn)) * 100).toFixed(1)}%` },
          { label: 'Specificity', value: `${((cm.tn / (cm.tn + cm.fp)) * 100).toFixed(1)}%` },
          { label: 'Positive Predictive Value', value: `${((cm.tp / (cm.tp + cm.fp)) * 100).toFixed(1)}%` },
          { label: 'Negative Predictive Value', value: `${((cm.tn / (cm.tn + cm.fn)) * 100).toFixed(1)}%` },
        ].map(m => (
          <div key={m.label} className="flex justify-between bg-surface-50 rounded-lg px-3 py-1.5">
            <span className="text-2xs text-content-secondary">{m.label}</span>
            <span className="text-2xs font-semibold text-content-primary">{m.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const ModelPerformance: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState('gnn');
  const [perfData, setPerfData] = useState<{
    metrics?: ModelMetrics;
    roc?: ROCPoint[];
    pr?: PRPoint[];
    confusion?: ConfusionMatrix;
    featureImportance?: FeatureImportance[];
  }>({});
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('roc');

  useEffect(() => {
    setLoading(true);
    modelApi.getPerformance(selectedModel).then(d => {
      setPerfData(d);
      setLoading(false);
    });
  }, [selectedModel]);

  const tabs = [
    { id: 'roc', label: 'ROC Curve' },
    { id: 'pr', label: 'PR Curve' },
    { id: 'confusion', label: 'Confusion Matrix' },
    { id: 'features', label: 'Feature Importance' },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Model Performance Analysis"
        subtitle="Detailed evaluation metrics, curves, and interpretability for each model"
        breadcrumb={['Models', 'Performance']}
        actions={
          <Select
            options={MODEL_OPTIONS}
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            className="w-52"
          />
        }
      />

      {/* Metric Summary */}
      {perfData.metrics && (
        <div className="grid grid-cols-2 xl:grid-cols-5 gap-4">
          {[
            { label: 'Accuracy', value: perfData.metrics.accuracy },
            { label: 'Precision', value: perfData.metrics.precision },
            { label: 'Recall', value: perfData.metrics.recall },
            { label: 'F1 Score', value: perfData.metrics.f1Score },
            { label: 'ROC-AUC', value: perfData.metrics.rocAuc },
          ].map(m => (
            <Card key={m.label}>
              <p className="stat-label">{m.label}</p>
              <p className="text-2xl font-bold text-success tabular-nums mt-1">{(m.value * 100).toFixed(1)}%</p>
            </Card>
          ))}
        </div>
      )}

      {/* Visualization tabs */}
      <Card>
        <div className="mb-5">
          <Tabs tabs={tabs} active={tab} onChange={setTab} />
        </div>

        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-64" />
          </div>
        ) : (
          <motion.div key={tab} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
            {tab === 'roc' && perfData.roc && (
              <div>
                <p className="text-xs text-content-secondary mb-4">
                  ROC-AUC = {perfData.metrics ? (perfData.metrics.rocAuc * 100).toFixed(2) : '—'}% · Area under the Receiver Operating Characteristic curve
                </p>
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={perfData.roc} margin={{ top: 4, right: 4, bottom: 20, left: -20 }}>
                    <defs>
                      <linearGradient id="rocGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                    <XAxis dataKey="fpr" tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                      label={{ value: 'False Positive Rate', position: 'bottom', fontSize: 11, fill: '#9CA3AF' }} />
                    <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                      label={{ value: 'True Positive Rate', angle: -90, position: 'left', fontSize: 11, fill: '#9CA3AF' }} />
                    <Tooltip formatter={(v: number) => v.toFixed(3)} />
                    <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]} stroke="#E5E7EB" strokeDasharray="4 4" />
                    <Area type="monotone" dataKey="tpr" stroke="#F59E0B" strokeWidth={2.5} fill="url(#rocGrad)" dot={false} name="TPR" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {tab === 'pr' && perfData.pr && (
              <div>
                <p className="text-xs text-content-secondary mb-4">
                  AUC-PR = {perfData.metrics ? (perfData.metrics.aucPr * 100).toFixed(2) : '—'}% · Precision-Recall curve (more informative for imbalanced datasets)
                </p>
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={perfData.pr} margin={{ top: 4, right: 4, bottom: 20, left: -20 }}>
                    <defs>
                      <linearGradient id="prGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                    <XAxis dataKey="recall" tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                      label={{ value: 'Recall', position: 'bottom', fontSize: 11, fill: '#9CA3AF' }} />
                    <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                      label={{ value: 'Precision', angle: -90, position: 'left', fontSize: 11, fill: '#9CA3AF' }} />
                    <Tooltip formatter={(v: number) => v.toFixed(3)} />
                    <Area type="monotone" dataKey="precision" stroke="#2563EB" strokeWidth={2.5} fill="url(#prGrad)" dot={false} name="Precision" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {tab === 'confusion' && perfData.confusion && (
              <div className="max-w-sm mx-auto">
                <p className="text-xs text-content-secondary mb-4 text-center">
                  Confusion matrix on test set — {perfData.confusion.tn + perfData.confusion.fp + perfData.confusion.fn + perfData.confusion.tp} samples
                </p>
                <ConfMatrixViz cm={perfData.confusion} />
              </div>
            )}

            {tab === 'features' && perfData.featureImportance && (
              <div>
                <p className="text-xs text-content-secondary mb-4">
                  SHAP-based feature importance — relative contribution to default probability prediction
                </p>
                <div className="space-y-2">
                  {perfData.featureImportance.map((f, i) => (
                    <div key={f.feature} className="flex items-center gap-3">
                      <span className="text-2xs text-content-tertiary w-4 text-right">{f.rank}</span>
                      <span className="text-xs text-content-primary w-44 flex-shrink-0">{f.feature}</span>
                      <div className="flex-1 bg-surface-100 rounded-full h-5 relative">
                        <div
                          className="absolute top-0 left-0 h-full rounded-full flex items-center pl-2"
                          style={{ width: `${f.importance * 600}%`, backgroundColor: i < 3 ? '#F59E0B' : '#94A3B8' }}
                        >
                          <span className="text-2xs font-semibold text-white">{(f.importance * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </Card>
    </motion.div>
  );
};

export default ModelPerformance;
