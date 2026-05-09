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
  const [hovered, setHovered] = React.useState(false);

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
    transition: 'var(--transition-smooth)',
    opacity: disabled ? 0.6 : 1,
    width: fullWidth ? '100%' : 'auto',
    position: 'relative',
    overflow: 'hidden',
    transform: hovered && !disabled ? 'translateY(-1px)' : 'translateY(0)',
    ...style,
  };

  const sizeStyles = {
    sm: { padding: '6px 14px', fontSize: '12px' },
    md: { padding: '10px 20px', fontSize: '14px' },
    lg: { padding: '14px 28px', fontSize: '16px' },
  };

  const variantStyles = {
    primary: {
      background: 'var(--gradient-primary)',
      color: '#ffffff',
      boxShadow: hovered && !disabled ? 'var(--shadow-glow)' : '0 4px 14px rgba(99, 102, 241, 0.25)',
    },
    secondary: {
      background: hovered && !disabled ? 'var(--bg-main)' : 'var(--bg-surface)',
      color: 'var(--text-main)',
      border: '1px solid var(--border-color)',
      boxShadow: hovered && !disabled ? 'var(--shadow-md)' : 'var(--shadow-sm)',
    },
    danger: {
      background: hovered && !disabled ? 'rgba(239, 68, 68, 0.15)' : 'rgba(239, 68, 68, 0.1)',
      color: 'var(--color-danger)',
      border: '1px solid rgba(239, 68, 68, 0.3)',
    },
    ghost: {
      background: hovered && !disabled ? 'var(--bg-surface)' : 'transparent',
      color: hovered && !disabled ? 'var(--text-main)' : 'var(--text-muted)',
      border: '1px solid transparent',
    },
    success: {
      background: 'linear-gradient(135deg, var(--color-success) 0%, #059669 100%)',
      color: '#ffffff',
      boxShadow: hovered && !disabled ? '0 8px 20px rgba(16, 185, 129, 0.25)' : '0 4px 14px rgba(16, 185, 129, 0.25)',
    },
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={className}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ ...baseStyle, ...sizeStyles[size], ...variantStyles[variant] }}
    >
      {icon && <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>}
      {children}
    </button>
  );
};
