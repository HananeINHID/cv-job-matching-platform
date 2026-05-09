import React from 'react';

/**
 * Card — Conteneur surface avec ombre et bordure
 */
export const Card = ({ children, style = {}, className = '', onClick, hoverable = false }) => {
  const [hovered, setHovered] = React.useState(false);

  return (
    <div
      className={`${className} ${hoverable ? 'hover-card' : ''} glass-card`}
      onClick={onClick}
      onMouseEnter={() => hoverable && setHovered(true)}
      onMouseLeave={() => hoverable && setHovered(false)}
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: `1px solid var(--border-color)`,
        borderRadius: 'var(--radius-lg)',
        boxShadow: hovered ? 'var(--shadow-lg)' : 'var(--shadow-sm)',
        transition: 'var(--transition-smooth)',
        transform: hovered ? 'translateY(-3px)' : 'translateY(0)',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'hidden',
        ...style,
      }}
    >
      <style>{`
        .glass-card {
           backdrop-filter: blur(10px);
           -webkit-backdrop-filter: blur(10px);
        }
      `}</style>
      {children}
    </div>
  );
};

/**
 * CardHeader — En-tête de Card avec titre et action optionnelle
 */
export const CardHeader = ({ title, subtitle, action, icon }) => (
  <div style={{
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    padding: '1.25rem 1.5rem',
    borderBottom: '1px solid var(--border-color)',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      {icon && (
        <span style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--color-primary)',
          backgroundColor: 'var(--color-primary-light)',
          padding: '8px',
          borderRadius: 'var(--radius-md)',
        }}>{icon}</span>
      )}
      <div>
        <h3 style={{
          margin: 0, fontSize: '16px', fontWeight: 700,
          color: 'var(--text-main)', letterSpacing: '-0.3px',
        }}>{title}</h3>
        {subtitle && (
          <p style={{ margin: '4px 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
    {action && <div>{action}</div>}
  </div>
);

/**
 * CardBody — Corps d'une Card avec padding
 */
export const CardBody = ({ children, style = {} }) => (
  <div style={{ padding: '1.5rem', ...style }}>{children}</div>
);
