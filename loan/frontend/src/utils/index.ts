import type { RiskCategory, ModelType } from '@/types';

// ============================================================
// FORMATTERS
// ============================================================
export const formatCurrency = (value: number, decimals = 1): string => {
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(decimals)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(decimals)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(decimals)}K`;
  return `$${value.toFixed(0)}`;
};

export const formatPercent = (value: number, decimals = 1): string =>
  `${(value * 100).toFixed(decimals)}%`;

export const formatPercentRaw = (value: number, decimals = 1): string =>
  `${value.toFixed(decimals)}%`;

export const formatDate = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
};

export const formatDateTime = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

export const formatNumber = (n: number, decimals = 0): string =>
  n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

export const formatDecimals = (n: number, dec = 2): string => n.toFixed(dec);

// ============================================================
// RISK HELPERS
// ============================================================
export const getRiskColor = (risk: RiskCategory | string): string => {
  const map: Record<string, string> = {
    LOW: 'text-success',
    MEDIUM: 'text-warning',
    HIGH: 'text-danger',
  };
  return map[risk] || 'text-content-secondary';
};

export const getRiskBgClass = (risk: RiskCategory | string): string => {
  const map: Record<string, string> = {
    LOW: 'badge-risk-low',
    MEDIUM: 'badge-risk-medium',
    HIGH: 'badge-risk-high',
  };
  return map[risk] || 'badge-neutral';
};

export const getRiskHex = (risk: RiskCategory | string): string => {
  const map: Record<string, string> = {
    LOW: '#16A34A',
    MEDIUM: '#F59E0B',
    HIGH: '#DC2626',
  };
  return map[risk] || '#6B7280';
};

export const getProbabilityColor = (prob: number): string => {
  if (prob < 0.35) return '#16A34A';
  if (prob < 0.65) return '#F59E0B';
  return '#DC2626';
};

export const getProbabilityCategory = (prob: number): RiskCategory => {
  if (prob < 0.35) return 'LOW';
  if (prob < 0.65) return 'MEDIUM';
  return 'HIGH';
};

export const getNetworkExposureColor = (exposure: string): string => {
  const map: Record<string, string> = {
    LOW: 'text-success',
    MODERATE: 'text-info',
    ELEVATED: 'text-warning',
    HIGH: 'text-danger',
  };
  return map[exposure] || 'text-content-secondary';
};

// ============================================================
// MODEL HELPERS
// ============================================================
export const getModelDisplayName = (model: ModelType | string): string => {
  const map: Record<string, string> = {
    logistic_regression: 'Logistic Regression',
    svm: 'Support Vector Machine',
    xgboost: 'XGBoost',
    gnn: 'Graph Neural Network',
  };
  return map[model] || model;
};

export const getModelColor = (model: ModelType | string): string => {
  const map: Record<string, string> = {
    logistic_regression: '#6B7280',
    svm: '#2563EB',
    xgboost: '#16A34A',
    gnn: '#F59E0B',
  };
  return map[model] || '#6B7280';
};

// ============================================================
// MISC
// ============================================================
export const clsx = (...classes: (string | boolean | undefined | null)[]): string =>
  classes.filter(Boolean).join(' ');

export const truncate = (str: string, max: number): string =>
  str.length > max ? `${str.slice(0, max)}...` : str;

export const initials = (name: string): string =>
  name.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase();

export const relativeTime = (iso: string): string => {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
};
