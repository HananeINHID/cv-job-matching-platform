import React from 'react';

/**
 * Composant Button réutilisable
 * Variants: primary | secondary | danger | ghost
 * Sizes: sm | md | lg
 */
export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  fullWidth = false,
  icon,
  type = 'button',
  className = '',
  style = {},
}) => {
  const baseStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    fontFamily: 'inherit',
    fontWeight: 600,
    borderRadius: 'var(--radius-md)',
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease',
    opacity: disabled ? 0.6 : 1,
    width: fullWidth ? '100%' : 'auto',
    ...style,
  };

  const sizeStyles = {
    sm: { padding: '6px 14px', fontSize: '12px' },
    md: { padding: '10px 20px', fontSize: '14px' },
    lg: { padding: '14px 28px', fontSize: '16px' },
  };

  const variantStyles = {
    primary: {
      background: 'linear-gradient(135deg, var(--color-primary) 0%, #1D4ED8 100%)',
      color: '#ffffff',
      boxShadow: '0 4px 14px rgba(37, 99, 235, 0.35)',
    },
    secondary: {
      background: 'var(--bg-surface)',
      color: 'var(--text-main)',
      border: '1.5px solid var(--border-color)',
      boxShadow: 'var(--shadow-sm)',
    },
    danger: {
      background: 'rgba(239, 68, 68, 0.1)',
      color: 'var(--color-danger)',
      border: '1.5px solid rgba(239, 68, 68, 0.3)',
    },
    ghost: {
      background: 'transparent',
      color: 'var(--text-muted)',
      border: '1.5px solid var(--border-color)',
    },
    success: {
      background: 'linear-gradient(135deg, var(--color-success) 0%, #059669 100%)',
      color: '#ffffff',
      boxShadow: '0 4px 14px rgba(16, 185, 129, 0.35)',
    },
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={className}
      style={{ ...baseStyle, ...sizeStyles[size], ...variantStyles[variant] }}
    >
      {icon && <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>}
      {children}
    </button>
  );
};
