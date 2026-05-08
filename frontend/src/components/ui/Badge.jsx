import React from 'react';

/**
 * Badge coloré selon le type : success | warning | danger | info | neutral
 */
export const Badge = ({ children, variant = 'neutral', size = 'md', dot = false }) => {
  const variantStyles = {
    success: { bg: 'rgba(16, 185, 129, 0.15)', color: 'var(--color-success)', border: 'rgba(16, 185, 129, 0.3)' },
    warning: { bg: 'rgba(245, 158, 11, 0.15)', color: 'var(--color-warning)', border: 'rgba(245, 158, 11, 0.3)' },
    danger:  { bg: 'rgba(239, 68, 68, 0.15)',  color: 'var(--color-danger)',  border: 'rgba(239, 68, 68, 0.3)' },
    info:    { bg: 'rgba(37, 99, 235, 0.15)',   color: 'var(--color-primary)', border: 'rgba(37, 99, 235, 0.3)' },
    neutral: { bg: 'var(--color-neutral-100)',  color: 'var(--text-muted)',    border: 'var(--border-color)' },
  };

  const sizeStyles = {
    sm: { padding: '2px 8px', fontSize: '11px' },
    md: { padding: '4px 12px', fontSize: '12px' },
    lg: { padding: '6px 16px', fontSize: '13px' },
  };

  const v = variantStyles[variant] || variantStyles.neutral;

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '5px',
      backgroundColor: v.bg,
      color: v.color,
      border: `1px solid ${v.border}`,
      borderRadius: 'var(--radius-full)',
      fontWeight: 600,
      letterSpacing: '0.01em',
      ...sizeStyles[size],
    }}>
      {dot && (
        <span style={{
          width: '6px', height: '6px',
          borderRadius: '50%',
          backgroundColor: v.color,
          flexShrink: 0,
        }} />
      )}
      {children}
    </span>
  );
};

/**
 * ScoreBadge — Badge de score coloré automatiquement selon le % 
 */
export const ScoreBadge = ({ score, size = 'md' }) => {
  const variant = score >= 70 ? 'success' : score >= 40 ? 'warning' : 'danger';
  return <Badge variant={variant} size={size}>{score}%</Badge>;
};
