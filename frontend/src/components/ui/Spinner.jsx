import React from 'react';

/**
 * Spinner — Indicateur de chargement animé
 */
export const Spinner = ({ size = 24, color = 'var(--color-primary)' }) => (
  <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
    <style>{`
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `}</style>
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ animation: 'spin 0.8s linear infinite' }}
    >
      <circle cx="12" cy="12" r="10" stroke={color} strokeOpacity="0.2" strokeWidth="3" />
      <path
        d="M12 2a10 10 0 0 1 10 10"
        stroke={color}
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  </span>
);

/**
 * PageLoader — Plein écran de chargement
 */
export const PageLoader = ({ message = 'Chargement...' }) => (
  <div style={{
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '16px',
    backgroundColor: 'var(--bg-main)',
  }}>
    <Spinner size={48} />
    <p style={{ fontSize: '15px', color: 'var(--text-muted)', fontWeight: 500, margin: 0 }}>
      {message}
    </p>
  </div>
);
