import React from 'react';
import { clsx } from '@/utils';

// ============================================================
// BADGE
// ============================================================
interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'primary';
  className?: string;
}
export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', className }) => {
  const variants = {
    success: 'badge-success',
    warning: 'badge-warning',
    danger: 'badge-danger',
    info: 'badge-info',
    neutral: 'badge-neutral',
    primary: 'badge-primary',
  };
  return <span className={clsx('badge', variants[variant], className)}>{children}</span>;
};

// ============================================================
// RISK BADGE
// ============================================================
interface RiskBadgeProps {
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
  className?: string;
}
export const RiskBadge: React.FC<RiskBadgeProps> = ({ risk, className }) => {
  const cls = { LOW: 'badge-risk-low', MEDIUM: 'badge-risk-medium', HIGH: 'badge-risk-high' }[risk];
  const dots = { LOW: 'bg-success', MEDIUM: 'bg-warning', HIGH: 'bg-danger' }[risk];
  return (
    <span className={clsx('badge', cls, className)}>
      <span className={clsx('w-1.5 h-1.5 rounded-full', dots)} />
      {risk}
    </span>
  );
};

// ============================================================
// BUTTON
// ============================================================
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}
export const Button: React.FC<ButtonProps> = ({
  children, variant = 'primary', size = 'md', loading, leftIcon, rightIcon, className, disabled, ...rest
}) => {
  const variantCls = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    ghost: 'btn-ghost',
    danger: 'btn-danger',
  }[variant];
  const sizeCls = { sm: 'btn-sm', md: '', lg: 'btn-lg', icon: 'btn-icon' }[size];
  return (
    <button className={clsx('btn', variantCls, sizeCls, className)} disabled={disabled || loading} {...rest}>
      {loading ? (
        <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="30 60" />
        </svg>
      ) : leftIcon}
      {children}
      {!loading && rightIcon}
    </button>
  );
};

// ============================================================
// CARD
// ============================================================
interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: boolean;
  style?: React.CSSProperties;
}
export const Card: React.FC<CardProps> = ({ children, className, hover, padding = true, style }) => (
  <div className={clsx(hover ? 'card-hover' : 'card', padding && 'p-5', className)} style={style}>{children}</div>
);

// ============================================================
// INPUT
// ============================================================
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
}
export const Input: React.FC<InputProps> = ({ label, error, hint, leftIcon, className, id, ...rest }) => (
  <div className="form-group">
    {label && <label className="label" htmlFor={id}>{label}</label>}
    <div className="relative">
      {leftIcon && <div className="absolute left-3 top-1/2 -translate-y-1/2 text-content-tertiary">{leftIcon}</div>}
      <input
        id={id}
        className={clsx('input', leftIcon && 'pl-9', error && 'input-error', className)}
        {...rest}
      />
    </div>
    {error && <p className="text-xs text-danger mt-1">{error}</p>}
    {hint && !error && <p className="text-xs text-content-tertiary mt-1">{hint}</p>}
  </div>
);

// ============================================================
// SELECT
// ============================================================
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}
export const Select: React.FC<SelectProps> = ({ label, error, options, className, id, ...rest }) => (
  <div className="form-group">
    {label && <label className="label" htmlFor={id}>{label}</label>}
    <select id={id} className={clsx('input', error && 'input-error', className)} {...rest}>
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
    {error && <p className="text-xs text-danger mt-1">{error}</p>}
  </div>
);

// ============================================================
// SKELETON
// ============================================================
export const Skeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={clsx('skeleton', className)} />
);

export const SkeletonCard: React.FC = () => (
  <div className="card p-5 space-y-3">
    <Skeleton className="h-4 w-24" />
    <Skeleton className="h-8 w-32" />
    <Skeleton className="h-3 w-20" />
  </div>
);

// ============================================================
// EMPTY STATE
// ============================================================
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}
export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action }) => (
  <div className="empty-state">
    {icon && <div className="text-content-tertiary">{icon}</div>}
    <div>
      <p className="empty-state-title">{title}</p>
      {description && <p className="empty-state-desc mt-1">{description}</p>}
    </div>
    {action}
  </div>
);

// ============================================================
// SPINNER
// ============================================================
export const Spinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({ size = 'md', className }) => {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' };
  return (
    <svg className={clsx(sizes[size], 'animate-spin text-primary', className)} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
      <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" className="opacity-75" />
    </svg>
  );
};

// ============================================================
// PROGRESS BAR
// ============================================================
interface ProgressBarProps {
  value: number; // 0–100
  color?: string;
  className?: string;
  showLabel?: boolean;
}
export const ProgressBar: React.FC<ProgressBarProps> = ({ value, color = '#F59E0B', className, showLabel }) => (
  <div className={clsx('flex items-center gap-2', className)}>
    <div className="progress-bar flex-1">
      <div className="progress-bar-fill" style={{ width: `${Math.min(100, value)}%`, backgroundColor: color }} />
    </div>
    {showLabel && <span className="text-xs font-semibold text-content-secondary w-8 text-right tabular-nums">{value}%</span>}
  </div>
);

// ============================================================
// STAT CARD (used in KPI row)
// ============================================================
interface StatProps {
  label: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  iconBg?: string;
  prefix?: string;
  suffix?: string;
}
export const StatCard: React.FC<StatProps> = ({ label, value, change, icon, iconBg = 'bg-primary-light' }) => (
  <Card className="flex items-start gap-4 min-w-0">
    <div className={clsx('p-3 rounded-xl flex-shrink-0', iconBg)}>
      <div className="text-primary w-5 h-5">{icon}</div>
    </div>
    <div className="min-w-0">
      <p className="stat-label">{label}</p>
      <p className="stat-value mt-1">{value}</p>
      {change !== undefined && (
        <p className={clsx('text-xs mt-1 font-medium', change >= 0 ? 'text-success' : 'text-danger')}>
          {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(1)}% vs last month
        </p>
      )}
    </div>
  </Card>
);

// ============================================================
// PAGE HEADER
// ============================================================
interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  breadcrumb?: string[];
}
export const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, actions, breadcrumb }) => (
  <div className="page-header flex items-start justify-between gap-4">
    <div>
      {breadcrumb && (
        <p className="text-xs text-content-tertiary mb-1">
          {breadcrumb.join(' / ')}
        </p>
      )}
      <h1 className="page-title">{title}</h1>
      {subtitle && <p className="page-subtitle">{subtitle}</p>}
    </div>
    {actions && <div className="flex items-center gap-2 flex-shrink-0">{actions}</div>}
  </div>
);

// ============================================================
// TABS
// ============================================================
interface TabsProps {
  tabs: { id: string; label: string; icon?: React.ReactNode }[];
  active: string;
  onChange: (id: string) => void;
  className?: string;
}
export const Tabs: React.FC<TabsProps> = ({ tabs, active, onChange, className }) => (
  <div className={clsx('flex gap-1 bg-surface-100 p-1 rounded-lg', className)}>
    {tabs.map(t => (
      <button
        key={t.id}
        onClick={() => onChange(t.id)}
        className={clsx(
          'flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200',
          active === t.id
            ? 'bg-white text-content-primary shadow-card'
            : 'text-content-secondary hover:text-content-primary'
        )}
      >
        {t.icon}
        {t.label}
      </button>
    ))}
  </div>
);

// ============================================================
// TOOLTIP
// ============================================================
interface TooltipProps { children: React.ReactNode; content: string; }
export const Tooltip: React.FC<TooltipProps> = ({ children, content }) => (
  <div className="relative group inline-flex">
    {children}
    <div className="tooltip-content -top-9 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none absolute">
      {content}
    </div>
  </div>
);

// ============================================================
// SECTION HEADER
// ============================================================
interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}
export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, subtitle, actions }) => (
  <div className="flex items-center justify-between mb-4">
    <div>
      <h3 className="section-title">{title}</h3>
      {subtitle && <p className="section-subtitle mt-0.5">{subtitle}</p>}
    </div>
    {actions && <div>{actions}</div>}
  </div>
);
