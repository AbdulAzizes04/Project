import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building2, DollarSign, Ship, BarChart3, Network,
  TrendingUp, AlertTriangle, CheckCircle, ChevronRight,
  Activity, Cpu, Info, ArrowRight,
} from 'lucide-react';
import {
  Card, PageHeader, Button, Input, Select, RiskBadge, SectionHeader, ProgressBar, Spinner,
} from '@/components/ui';
import { predictionApi } from '@/api/predictionApi';
import type { PredictionResult, PredictionInput } from '@/types';
import { formatPercent, formatPercentRaw, getRiskHex, getModelDisplayName, formatDateTime, clsx } from '@/utils';
import { useToast } from '@/context/ToastContext';
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';

// ============================================================
// SCHEMA
// ============================================================
const schema = z.object({
  companyName: z.string().min(2, 'Required'),
  companyId: z.string().optional(),
  segment: z.string().min(1, 'Required'),
  country: z.string().min(1, 'Required'),
  loanAmount: z.coerce.number().positive('Must be positive'),
  interestRate: z.coerce.number().min(0.1).max(30),
  loanTermMonths: z.coerce.number().positive(),
  outstandingAmount: z.coerce.number().positive(),
  debtToEquityRatio: z.coerce.number().min(0).max(20),
  vesselAge: z.coerce.number().min(0).max(50),
  vesselValue: z.coerce.number().positive(),
  fleetSize: z.coerce.number().positive(),
  vesselType: z.string().min(1),
  avgUtilization: z.coerce.number().min(0).max(1),
  freightRate: z.coerce.number().positive(),
  marketIndex: z.coerce.number(),
  fuelPrice: z.coerce.number().positive(),
  economicGrowth: z.coerce.number(),
  inflation: z.coerce.number(),
  interestRateEnvironment: z.coerce.number(),
  networkCentrality: z.coerce.number().min(0).max(1),
  clusteringCoefficient: z.coerce.number().min(0).max(1),
  connectedCompanies: z.coerce.number().min(0),
  networkExposure: z.enum(['LOW', 'MODERATE', 'ELEVATED', 'HIGH']),
});
type FormValues = z.infer<typeof schema>;

// ============================================================
// RISK GAUGE
// ============================================================
const RiskGauge: React.FC<{ probability: number }> = ({ probability }) => {
  const pct = probability * 100;
  const color = getRiskHex(pct < 35 ? 'LOW' : pct < 65 ? 'MEDIUM' : 'HIGH');
  const data = [{ value: pct, fill: color }];

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={160}>
        <RadialBarChart
          cx="50%" cy="80%"
          innerRadius="70%" outerRadius="100%"
          startAngle={180} endAngle={0}
          data={[{ value: 100, fill: '#F3F4F6' }, ...data]}
        >
          <RadialBar dataKey="value" cornerRadius={8} background={false} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-end pb-4">
        <p className="text-3xl font-bold tabular-nums" style={{ color }}>{pct.toFixed(1)}%</p>
        <p className="text-xs text-content-tertiary">Default Probability</p>
      </div>
    </div>
  );
};

// ============================================================
// FORM SECTION WRAPPER
// ============================================================
const FormSection: React.FC<{
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  children: React.ReactNode;
  number: number;
}> = ({ icon, title, subtitle, children, number }) => (
  <Card>
    <div className="flex items-center gap-3 mb-5">
      <div className="w-8 h-8 bg-primary-light rounded-lg flex items-center justify-center flex-shrink-0">
        <div className="text-primary">{icon}</div>
      </div>
      <div>
        <div className="flex items-center gap-2">
          <span className="text-2xs font-semibold text-primary uppercase tracking-wider">Section {number}</span>
        </div>
        <h3 className="text-sm font-semibold text-content-primary">{title}</h3>
        <p className="text-xs text-content-secondary">{subtitle}</p>
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {children}
    </div>
  </Card>
);

// ============================================================
// PREDICTION RESULT PANEL
// ============================================================
const PredictionResultPanel: React.FC<{ result: PredictionResult; onReset: () => void }> = ({ result, onReset }) => {
  const riskColor = getRiskHex(result.riskCategory);
  const pct = result.defaultProbability * 100;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.35 }}
      className="space-y-4"
    >
      {/* Main Result */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-content-primary">Prediction Result</h2>
            <p className="text-xs text-content-secondary">{result.companyName}</p>
          </div>
          <RiskBadge risk={result.riskCategory} />
        </div>

        <RiskGauge probability={result.defaultProbability} />

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-3 mt-4">
          <div className="bg-surface-50 rounded-xl p-3 text-center border border-surface-200">
            <p className="text-2xs text-content-tertiary uppercase tracking-wider">Confidence</p>
            <p className="text-sm font-bold text-content-primary tabular-nums">{formatPercentRaw(result.confidence * 100)}</p>
          </div>
          <div className="bg-surface-50 rounded-xl p-3 text-center border border-surface-200">
            <p className="text-2xs text-content-tertiary uppercase tracking-wider">Model</p>
            <p className="text-sm font-bold text-content-primary">{getModelDisplayName(result.modelUsed).split(' ').slice(-1)[0]}</p>
          </div>
          <div className="bg-surface-50 rounded-xl p-3 text-center border border-surface-200">
            <p className="text-2xs text-content-tertiary uppercase tracking-wider">Timestamp</p>
            <p className="text-xs font-semibold text-content-primary">{formatDateTime(result.timestamp).split(',')[0]}</p>
          </div>
        </div>

        {/* Risk meter */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-content-tertiary mb-1">
            <span>Low Risk</span><span>Medium</span><span>High Risk</span>
          </div>
          <div className="risk-meter w-full relative">
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg"
              style={{ left: `${pct}%`, transform: 'translateX(-50%)' }}
            />
          </div>
          <div className="mt-2 flex justify-between text-xs text-content-tertiary">
            <span>0%</span><span>50%</span><span>100%</span>
          </div>
        </div>
      </Card>

      {/* Contributing Factors */}
      <Card>
        <SectionHeader
          title="Why was this company classified as high risk?"
          subtitle="Top contributing risk factors from the GNN model"
        />
        <div className="space-y-3">
          {result.contributingFactors.map((f, i) => (
            <div key={i} className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium text-content-primary">{f.name}</span>
                  <span className={clsx(
                    'badge text-2xs',
                    f.impact === 'HIGH' ? 'badge-danger' : f.impact === 'MEDIUM' ? 'badge-warning' : 'badge-neutral'
                  )}>
                    {f.impact}
                  </span>
                </div>
                <ProgressBar
                  value={f.contribution}
                  color={f.direction === 'positive' ? '#DC2626' : '#16A34A'}
                />
              </div>
              <span className="text-xs font-semibold text-content-secondary tabular-nums flex-shrink-0">
                {typeof f.value === 'number' ? f.value.toFixed(2) : f.value}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Network Risk */}
      <Card>
        <SectionHeader title="Network-Based Risk" subtitle="Financial network position analysis" />
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: 'Network Centrality', value: result.networkRisk.centrality.toFixed(3) },
            { label: 'Clustering Coeff.', value: result.networkRisk.clusteringCoefficient.toFixed(3) },
            { label: 'Connected Companies', value: result.networkRisk.connectedCompanies },
            { label: 'Network Exposure', value: result.networkRisk.networkExposure },
          ].map(m => (
            <div key={m.label} className="bg-surface-50 rounded-xl p-3 border border-surface-200">
              <p className="text-2xs text-content-tertiary">{m.label}</p>
              <p className={clsx(
                'text-sm font-bold mt-1',
                m.label === 'Network Exposure' && m.value === 'HIGH' ? 'text-danger' :
                m.label === 'Network Exposure' && m.value === 'ELEVATED' ? 'text-warning' : 'text-content-primary'
              )}>{m.value}</p>
            </div>
          ))}
        </div>
      </Card>

      <Button variant="secondary" className="w-full" onClick={onReset}>
        ← Run Another Prediction
      </Button>
    </motion.div>
  );
};

// ============================================================
// MAIN PAGE
// ============================================================
const Prediction: React.FC = () => {
  const { error: showError } = useToast();
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [predicting, setPredicting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(schema) as any,
    defaultValues: {
      companyName: '',
      segment: 'Bulk Carrier',
      country: 'Greece',
      loanAmount: 25000000,
      interestRate: 6.5,
      loanTermMonths: 60,
      outstandingAmount: 18000000,
      debtToEquityRatio: 3.2,
      vesselAge: 12,
      vesselValue: 31000000,
      fleetSize: 3,
      vesselType: 'Bulk Carrier',
      avgUtilization: 0.74,
      freightRate: 1200,
      marketIndex: 1450,
      fuelPrice: 650,
      economicGrowth: 2.3,
      inflation: 3.1,
      interestRateEnvironment: 4.5,
      networkCentrality: 0.64,
      clusteringCoefficient: 0.52,
      connectedCompanies: 12,
      networkExposure: 'ELEVATED',
    },
  });

  const onSubmit = async (data: FormValues) => {
    setPredicting(true);
    setResult(null);
    try {
      const res = await predictionApi.predict(data as PredictionInput);
      setResult(res);
    } catch {
      showError('Prediction failed', 'Unable to process the prediction. Please try again.');
    } finally {
      setPredicting(false);
    }
  };

  if (result) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Prediction Result"
          subtitle="Maritime loan default risk assessment complete"
          breadcrumb={['Loan Prediction', 'Result']}
        />
        <PredictionResultPanel result={result} onReset={() => setResult(null)} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Maritime Loan Default Prediction"
        subtitle="Evaluate financial, vessel, loan and network risk factors using TDA-enhanced GNN model."
        breadcrumb={['Loan Prediction']}
        actions={
          <Button onClick={handleSubmit(onSubmit)} loading={predicting} leftIcon={<TrendingUp className="w-4 h-4" />}>
            {predicting ? 'Analyzing...' : 'Run Risk Prediction'}
          </Button>
        }
      />

      {predicting && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card p-8 flex flex-col items-center justify-center gap-4"
        >
          <Spinner size="lg" />
          <div className="text-center">
            <p className="font-semibold text-content-primary">Analyzing financial and network risk...</p>
            <p className="text-sm text-content-secondary mt-1">Running TDA feature extraction and GNN inference</p>
          </div>
          <div className="flex gap-2 flex-wrap justify-center">
            {['Extracting TDA features', 'Building network graph', 'Running XGBoost', 'GNN inference', 'Computing SHAP values'].map(s => (
              <span key={s} className="badge-neutral text-2xs px-3 py-1 rounded-full flex items-center gap-1.5 badge">
                <Activity className="w-3 h-3 text-primary animate-pulse" />
                {s}
              </span>
            ))}
          </div>
        </motion.div>
      )}

      {!predicting && (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Section 1: Company */}
          <FormSection number={1} icon={<Building2 className="w-4 h-4" />} title="Company Information" subtitle="Basic company identification and classification">
            <Input label="Company Name *" placeholder="e.g. Oceanic Shipping Ltd." error={errors.companyName?.message} {...register('companyName')} />
            <Input label="Company ID" placeholder="e.g. COMP-0001" {...register('companyId')} />
            <Select label="Industry Segment *" options={[
              { value: 'Bulk Carrier', label: 'Bulk Carrier' },
              { value: 'Container Shipping', label: 'Container Shipping' },
              { value: 'Tanker', label: 'Tanker' },
              { value: 'LNG Carrier', label: 'LNG Carrier' },
              { value: 'Ro-Ro', label: 'Ro-Ro' },
              { value: 'General Cargo', label: 'General Cargo' },
            ]} {...register('segment')} />
            <Select label="Country / Region *" options={[
              'Greece', 'Norway', 'Germany', 'Singapore', 'Japan',
              'South Korea', 'China', 'USA', 'Denmark', 'UK',
            ].map(c => ({ value: c, label: c }))} {...register('country')} />
          </FormSection>

          {/* Section 2: Loan */}
          <FormSection number={2} icon={<DollarSign className="w-4 h-4" />} title="Loan Information" subtitle="Financial loan parameters and debt structure">
            <Input label="Loan Amount ($) *" type="number" placeholder="25000000" error={errors.loanAmount?.message} {...register('loanAmount')} />
            <Input label="Interest Rate (%) *" type="number" step="0.1" placeholder="6.5" error={errors.interestRate?.message} {...register('interestRate')} />
            <Input label="Loan Term (months) *" type="number" placeholder="60" {...register('loanTermMonths')} />
            <Input label="Outstanding Amount ($) *" type="number" placeholder="18000000" {...register('outstandingAmount')} />
            <Input label="Debt-to-Equity Ratio *" type="number" step="0.1" placeholder="3.2" error={errors.debtToEquityRatio?.message} {...register('debtToEquityRatio')} />
          </FormSection>

          {/* Section 3: Vessel */}
          <FormSection number={3} icon={<Ship className="w-4 h-4" />} title="Vessel Information" subtitle="Fleet characteristics and maritime asset details">
            <Input label="Vessel Age (years) *" type="number" placeholder="12" error={errors.vesselAge?.message} {...register('vesselAge')} />
            <Input label="Vessel Value ($) *" type="number" placeholder="31000000" {...register('vesselValue')} />
            <Input label="Fleet Size *" type="number" placeholder="3" {...register('fleetSize')} />
            <Select label="Vessel Type *" options={[
              'Bulk Carrier', 'Container Ship', 'Tanker', 'General Cargo', 'LNG Carrier', 'Ro-Ro',
            ].map(t => ({ value: t, label: t }))} {...register('vesselType')} />
            <Input label="Avg Vessel Utilization (0–1) *" type="number" step="0.01" placeholder="0.74" {...register('avgUtilization')} />
          </FormSection>

          {/* Section 4: Market */}
          <FormSection number={4} icon={<BarChart3 className="w-4 h-4" />} title="Market Information" subtitle="Macroeconomic and freight market conditions">
            <Input label="Freight Rate ($/day) *" type="number" placeholder="1200" {...register('freightRate')} />
            <Input label="Market Index *" type="number" placeholder="1450" {...register('marketIndex')} />
            <Input label="Fuel Price ($/ton) *" type="number" placeholder="650" {...register('fuelPrice')} />
            <Input label="Economic Growth (%) *" type="number" step="0.1" placeholder="2.3" {...register('economicGrowth')} />
            <Input label="Inflation (%) *" type="number" step="0.1" placeholder="3.1" {...register('inflation')} />
            <Input label="Interest Rate Env. (%) *" type="number" step="0.1" placeholder="4.5" {...register('interestRateEnvironment')} />
          </FormSection>

          {/* Section 5: Network */}
          <FormSection number={5} icon={<Network className="w-4 h-4" />} title="Network Information" subtitle="Financial network topology features from TDA analysis">
            <Input label="Network Centrality (0–1) *" type="number" step="0.01" placeholder="0.64" hint="PageRank centrality in maritime network" {...register('networkCentrality')} />
            <Input label="Clustering Coefficient (0–1) *" type="number" step="0.01" placeholder="0.52" {...register('clusteringCoefficient')} />
            <Input label="Connected Companies *" type="number" placeholder="12" {...register('connectedCompanies')} />
            <Select label="Network Exposure *" options={[
              { value: 'LOW', label: 'Low' },
              { value: 'MODERATE', label: 'Moderate' },
              { value: 'ELEVATED', label: 'Elevated' },
              { value: 'HIGH', label: 'High' },
            ]} {...register('networkExposure')} />
          </FormSection>

          {/* Submit */}
          <div className="flex justify-end">
            <Button type="submit" size="lg" loading={predicting} leftIcon={<TrendingUp className="w-4 h-4" />}>
              {predicting ? 'Analyzing...' : 'Run Risk Prediction'}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
};

export default Prediction;
