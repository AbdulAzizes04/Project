import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Atom, Info, RefreshCw, Download } from 'lucide-react';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Cell,
} from 'recharts';
import { Card, PageHeader, Button, SectionHeader, Spinner, Tabs } from '@/components/ui';
import { generateMockTDA } from '@/services/mock/mockData';
import type { TDAFeatures, PersistencePair } from '@/types';
import { clsx } from '@/utils';

// ============================================================
// PERSISTENCE DIAGRAM
// ============================================================
const PersistenceDiagram: React.FC<{ features: TDAFeatures }> = ({ features }) => {
  const allPairs: (PersistencePair & { dim: string; color: string })[] = [
    ...features.persistentHomology.h0.map(p => ({ ...p, dim: 'H₀', color: '#16A34A' })),
    ...features.persistentHomology.h1.map(p => ({ ...p, dim: 'H₁', color: '#F59E0B' })),
    ...features.persistentHomology.h2.map(p => ({ ...p, dim: 'H₂', color: '#2563EB' })),
  ];

  const maxVal = Math.max(...allPairs.map(p => p.death)) * 1.1;

  return (
    <div>
      <p className="text-xs text-content-secondary mb-3">
        Each point represents a topological feature. Points further from the diagonal have higher persistence (more significant features).
      </p>
      <ResponsiveContainer width="100%" height={280}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="birth" type="number" name="Birth"
            domain={[0, maxVal]} tick={{ fontSize: 10, fill: '#9CA3AF' }}
            tickLine={false} axisLine={false} label={{ value: 'Birth', position: 'bottom', fontSize: 11, fill: '#9CA3AF' }}
          />
          <YAxis
            dataKey="death" type="number" name="Death"
            domain={[0, maxVal]} tick={{ fontSize: 10, fill: '#9CA3AF' }}
            tickLine={false} axisLine={false} label={{ value: 'Death', angle: -90, position: 'left', fontSize: 11, fill: '#9CA3AF' }}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0].payload as PersistencePair & { dim: string; color: string };
              return (
                <div className="bg-white border border-surface-200 rounded-xl shadow-dropdown p-3 text-xs">
                  <p className="font-semibold" style={{ color: d.color }}>{d.dim}</p>
                  <p>Birth: {d.birth.toFixed(3)}</p>
                  <p>Death: {d.death.toFixed(3)}</p>
                  <p>Persistence: {d.persistence.toFixed(3)}</p>
                </div>
              );
            }}
          />
          {/* Diagonal line y = x */}
          <ReferenceLine segment={[{ x: 0, y: 0 }, { x: maxVal, y: maxVal }]}
            stroke="#E5E7EB" strokeDasharray="4 4" />
          <Scatter data={allPairs} shape={(props: any) => {
            const { cx, cy, payload } = props;
            return (
              <circle cx={cx} cy={cy} r={5}
                fill={payload.color} fillOpacity={0.7}
                stroke={payload.color} strokeWidth={1} />
            );
          }} />
        </ScatterChart>
      </ResponsiveContainer>
      {/* Dimension legend */}
      <div className="flex gap-4 justify-center mt-2">
        {[{ dim: 'H₀', color: '#16A34A', label: 'Connected Components' },
          { dim: 'H₁', color: '#F59E0B', label: 'Loops / Cycles' },
          { dim: 'H₂', color: '#2563EB', label: 'Voids / Cavities' }].map(l => (
          <div key={l.dim} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: l.color }} />
            <span className="text-xs text-content-secondary">{l.dim} — {l.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================
// PERSISTENCE BARCODE
// ============================================================
const PersistenceBarcode: React.FC<{ features: TDAFeatures }> = ({ features }) => {
  const allPairs: (PersistencePair & { dim: string; color: string; label: string })[] = [
    ...features.persistentHomology.h0.map((p, i) => ({ ...p, dim: 'H₀', color: '#16A34A', label: `H₀-${i+1}` })),
    ...features.persistentHomology.h1.map((p, i) => ({ ...p, dim: 'H₁', color: '#F59E0B', label: `H₁-${i+1}` })),
    ...features.persistentHomology.h2.map((p, i) => ({ ...p, dim: 'H₂', color: '#2563EB', label: `H₂-${i+1}` })),
  ];
  const maxDeath = Math.max(...allPairs.map(p => p.death));

  return (
    <div>
      <p className="text-xs text-content-secondary mb-3">
        Each bar represents a topological feature. Bar length = persistence (lifetime). Longer bars = more significant features.
      </p>
      <div className="space-y-1.5">
        {allPairs.map((pair, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="text-2xs text-content-tertiary w-10 text-right flex-shrink-0">{pair.label}</span>
            <div className="flex-1 bg-surface-100 rounded-sm h-4 relative">
              <div
                className="absolute top-0 h-full rounded-sm"
                style={{
                  left: `${(pair.birth / maxDeath) * 100}%`,
                  width: `${((pair.death - pair.birth) / maxDeath) * 100}%`,
                  backgroundColor: pair.color,
                  opacity: 0.7,
                }}
              />
            </div>
            <span className="text-2xs text-content-tertiary w-10 tabular-nums">{pair.persistence.toFixed(2)}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-between text-2xs text-content-tertiary mt-2">
        <span>0</span><span>{(maxDeath / 2).toFixed(1)}</span><span>{maxDeath.toFixed(1)}</span>
      </div>
    </div>
  );
};

// ============================================================
// TDA FEATURES TABLE
// ============================================================
const TDAFeaturesTable: React.FC<{ features: TDAFeatures }> = ({ features }) => (
  <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
    <div>
      <h4 className="text-xs font-semibold text-content-secondary uppercase tracking-wider mb-3">Betti Numbers</h4>
      <div className="space-y-2">
        {[
          { label: 'β₀ — Connected Components', value: features.bettiNumbers.b0, color: '#16A34A' },
          { label: 'β₁ — Independent Cycles', value: features.bettiNumbers.b1, color: '#F59E0B' },
          { label: 'β₂ — Enclosed Voids', value: features.bettiNumbers.b2, color: '#2563EB' },
        ].map(m => (
          <div key={m.label} className="flex justify-between items-center py-2 border-b border-surface-100">
            <span className="text-xs text-content-secondary">{m.label}</span>
            <span className="text-sm font-bold tabular-nums" style={{ color: m.color }}>{m.value}</span>
          </div>
        ))}
      </div>
    </div>
    <div>
      <h4 className="text-xs font-semibold text-content-secondary uppercase tracking-wider mb-3">Persistence Metrics</h4>
      <div className="space-y-2">
        {[
          { label: 'Total Persistence', value: features.totalPersistence.toFixed(3) },
          { label: 'Average Persistence', value: features.averagePersistence.toFixed(3) },
          { label: 'Max Persistence', value: features.maxPersistence.toFixed(3) },
          { label: 'Topological Complexity', value: features.topologicalComplexity.toFixed(4) },
          { label: 'Wasserstein Distance', value: features.wasserstein.toFixed(4) },
          { label: 'Bottleneck Distance', value: features.bottleneck.toFixed(4) },
        ].map(m => (
          <div key={m.label} className="flex justify-between items-center py-2 border-b border-surface-100">
            <span className="text-xs text-content-secondary">{m.label}</span>
            <span className="text-xs font-semibold tabular-nums text-content-primary">{m.value}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// ============================================================
// MAIN PAGE
// ============================================================
const TDAAnalysis: React.FC = () => {
  const [features, setFeatures] = useState<TDAFeatures | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('diagram');

  useEffect(() => {
    setTimeout(() => {
      setFeatures(generateMockTDA());
      setLoading(false);
    }, 1200);
  }, []);

  const tabs = [
    { id: 'diagram', label: 'Persistence Diagram' },
    { id: 'barcode', label: 'Persistence Barcode' },
    { id: 'features', label: 'Extracted Features' },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Topological Data Analysis"
        subtitle="Hidden structural patterns and persistent relationships in the maritime financial network"
        breadcrumb={['TDA Analysis']}
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
              onClick={() => { setLoading(true); setTimeout(() => { setFeatures(generateMockTDA()); setLoading(false); }, 1000); }}>
              Recompute
            </Button>
            <Button variant="secondary" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>Export</Button>
          </div>
        }
      />

      {/* Info card */}
      <div className="bg-primary-light border border-primary/20 rounded-xl p-4 flex gap-3">
        <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-semibold text-content-primary">About Topological Data Analysis</p>
          <p className="text-xs text-content-secondary mt-1">
            TDA uses persistent homology to identify structural patterns in the maritime financial network at multiple scales.
            Persistent features (long bars / distant points) represent stable topological structures that are
            robust to noise and provide powerful features for loan default prediction.
            The Vietoris-Rips complex is constructed from pairwise distances between company financial profiles.
          </p>
        </div>
      </div>

      {/* KPI Summary */}
      {features && (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {[
            { label: 'Connected Components (β₀)', value: features.bettiNumbers.b0, color: '#16A34A' },
            { label: 'Cycles (β₁)', value: features.bettiNumbers.b1, color: '#F59E0B' },
            { label: 'Voids (β₂)', value: features.bettiNumbers.b2, color: '#2563EB' },
            { label: 'Total Persistence', value: features.totalPersistence.toFixed(2), color: '#6B7280' },
          ].map(m => (
            <Card key={m.label}>
              <p className="stat-label">{m.label}</p>
              <p className="text-2xl font-bold tabular-nums mt-1" style={{ color: m.color }}>{m.value}</p>
            </Card>
          ))}
        </div>
      )}

      {/* Main visualization */}
      <Card>
        <div className="mb-4">
          <Tabs tabs={tabs} active={tab} onChange={setTab} />
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <Spinner size="lg" />
            <p className="text-sm text-content-secondary">Computing persistent homology...</p>
            <p className="text-xs text-content-tertiary">Building Vietoris-Rips complex from maritime financial data</p>
          </div>
        ) : features ? (
          <motion.div
            key={tab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {tab === 'diagram' && <PersistenceDiagram features={features} />}
            {tab === 'barcode' && <PersistenceBarcode features={features} />}
            {tab === 'features' && <TDAFeaturesTable features={features} />}
          </motion.div>
        ) : null}
      </Card>

      {/* Interpretation */}
      {features && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {[
            {
              title: 'H₀ — Connected Components',
              color: '#16A34A',
              desc: `${features.bettiNumbers.b0} persistent connected components detected in the maritime network. These represent isolated financial clusters with limited inter-company risk exposure.`,
            },
            {
              title: 'H₁ — Independent Cycles',
              color: '#F59E0B',
              desc: `${features.bettiNumbers.b1} independent cycles (loops) in the correlation network. Cycles indicate circular financial dependencies that may amplify risk contagion.`,
            },
            {
              title: 'H₂ — Enclosed Voids',
              color: '#2563EB',
              desc: `${features.bettiNumbers.b2} higher-order topological void${features.bettiNumbers.b2 !== 1 ? 's' : ''} identified. Voids indicate regions of financial isolation and structural gaps in the network.`,
            },
          ].map(m => (
            <Card key={m.title} className="border-l-4" style={{ borderLeftColor: m.color }}>
              <p className="text-sm font-semibold text-content-primary">{m.title}</p>
              <p className="text-xs text-content-secondary mt-2 leading-relaxed">{m.desc}</p>
            </Card>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default TDAAnalysis;
