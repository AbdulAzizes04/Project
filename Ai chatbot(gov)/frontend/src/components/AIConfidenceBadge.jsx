import React from 'react';
import { Sparkles } from 'lucide-react';

export const AIConfidenceBadge = ({ confidence, showLabel = true }) => {
  const score = typeof confidence === 'number' ? confidence : 0.85;
  const pct = Math.round(score > 1 ? score : score * 100);

  let color = '#10b981'; // green > 80%
  let bg = 'rgba(16, 185, 129, 0.15)';
  if (pct < 60) {
    color = '#f59e0b'; // amber
    bg = 'rgba(245, 158, 11, 0.15)';
  } else if (pct < 40) {
    color = '#ef4444'; // red
    bg = 'rgba(239, 68, 68, 0.15)';
  }

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      background: bg,
      border: `1px solid ${color}33`,
      borderRadius: 20,
      padding: '0.2rem 0.6rem',
      fontSize: '0.78rem',
      fontWeight: 600,
      color: color,
    }}>
      <Sparkles size={13} />
      <span>{pct}% AI Confidence</span>
    </div>
  );
};
