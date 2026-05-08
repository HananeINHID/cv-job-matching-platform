import React from 'react';

/**
 * Card — Conteneur surface avec ombre et bordure
 */
export const Card = ({ children, style = {}, className = '', onClick, hoverable = false }) => {
  const [hovered, setHovered] = React.useState(false);

  return (
    <div
      className={className}
      onClick={onClick}
      onMouseEnter={() => hoverable && setHovered(true)}
      onMouseLeave={() => hoverable && setHovered(false)}
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: `1px solid var(--border-color)`,
        borderRadius: 'var(--radius-lg)',
        boxShadow: hovered ? 'var(--shadow-lg)' : 'var(--shadow-sm)',
        transition: 'box-shadow 0.2s ease, transform 0.2s ease',
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
    >
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
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      {icon && (
        <span style={{
          display: 'flex', alignItems: 'center',
          color: 'var(--color-primary)',
        }}>{icon}</span>
      )}
      <div>
        <h3 style={{
          margin: 0, fontSize: '15px', fontWeight: 700,
          color: 'var(--text-main)',
        }}>{title}</h3>
        {subtitle && (
          <p style={{ margin: '2px 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
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
