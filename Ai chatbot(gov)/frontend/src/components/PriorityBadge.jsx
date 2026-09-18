import React from 'react';
import { AlertCircle, AlertTriangle, Info, Flame } from 'lucide-react';

export const PriorityBadge = ({ priority }) => {
  const norm = (priority || 'medium').toLowerCase();

  const config = {
    critical: { label: 'Critical', class: 'badge-critical', icon: Flame },
    high: { label: 'High', class: 'badge-high', icon: AlertTriangle },
    medium: { label: 'Medium', class: 'badge-medium', icon: AlertCircle },
    low: { label: 'Low', class: 'badge-low', icon: Info },
  }[norm] || { label: priority || 'Medium', class: 'badge-medium', icon: AlertCircle };

  const Icon = config.icon;

  return (
    <span className={`badge ${config.class}`}>
      <Icon size={12} style={{ marginRight: 2 }} />
      {config.label}
    </span>
  );
};
