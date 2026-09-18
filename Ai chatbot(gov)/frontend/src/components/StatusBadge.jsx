import React from 'react';

const STATUS_CONFIG = {
  submitted: { label: 'Submitted', className: 'badge-submitted' },
  ai_analyzed: { label: 'AI Analyzed', className: 'badge-verified' },
  verified: { label: 'Verified', className: 'badge-verified' },
  assigned: { label: 'Assigned', className: 'badge-assigned' },
  noted: { label: 'Noted', className: 'badge-noted' },
  in_progress: { label: 'In Progress', className: 'badge-in_progress' },
  resolved: { label: 'Sorted / Resolved', className: 'badge-resolved' },
  sorted: { label: 'Sorted / Resolved', className: 'badge-resolved' },
  closed: { label: 'Closed', className: 'badge-resolved' },
  rejected: { label: 'Rejected', className: 'badge-rejected' },
};

export const StatusBadge = ({ status }) => {
  const normalized = (status || 'submitted').toLowerCase().replace(' ', '_');
  const config = STATUS_CONFIG[normalized] || {
    label: status || 'Unknown',
    className: 'badge-submitted',
  };

  return (
    <span className={`badge ${config.className}`}>
      <span className="badge-dot" />
      {config.label}
    </span>
  );
};
