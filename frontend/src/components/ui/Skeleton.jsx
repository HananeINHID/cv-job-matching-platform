import React from 'react';

/**
 * Skeleton — Placeholder animé pour le chargement
 */
export const Skeleton = ({ width = '100%', height = '16px', borderRadius = 'var(--radius-md)', style = {} }) => (
  <div style={{
    width,
    height,
    borderRadius,
    background: 'linear-gradient(90deg, var(--color-neutral-200) 25%, var(--color-neutral-100) 50%, var(--color-neutral-200) 75%)',
    backgroundSize: '200% 100%',
    animation: 'skeleton-shimmer 1.5s infinite',
    ...style,
  }} />
);

/**
 * SkeletonCard — Skeleton complet pour une card d'offre
 */
export const SkeletonCard = () => (
  <div style={{
    backgroundColor: 'var(--bg-surface)',
    border: '1px solid var(--border-color)',
    borderRadius: 'var(--radius-lg)',
    padding: '1.5rem',
    boxShadow: 'var(--shadow-sm)',
  }}>
    <style>{`
      @keyframes skeleton-shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
      }
    `}</style>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <Skeleton width="44px" height="44px" borderRadius="50%" />
        <div>
          <Skeleton width="160px" height="14px" style={{ marginBottom: '6px' }} />
          <Skeleton width="100px" height="12px" />
        </div>
      </div>
      <Skeleton width="56px" height="28px" borderRadius="var(--radius-full)" />
    </div>
    <Skeleton width="80%" height="12px" style={{ marginBottom: '6px' }} />
    <Skeleton width="60%" height="12px" style={{ marginBottom: '16px' }} />
    <div style={{ display: 'flex', gap: '6px' }}>
      <Skeleton width="70px" height="22px" borderRadius="var(--radius-full)" />
      <Skeleton width="85px" height="22px" borderRadius="var(--radius-full)" />
      <Skeleton width="60px" height="22px" borderRadius="var(--radius-full)" />
    </div>
  </div>
);

/**
 * SkeletonKPI — Skeleton pour les cards de statistiques
 */
export const SkeletonKPI = () => (
  <div style={{
    backgroundColor: 'var(--bg-surface)',
    border: '1px solid var(--border-color)',
    borderRadius: 'var(--radius-lg)',
    padding: '1.25rem',
  }}>
    <Skeleton width="32px" height="32px" borderRadius="var(--radius-md)" style={{ marginBottom: '12px' }} />
    <Skeleton width="80%" height="12px" style={{ marginBottom: '6px' }} />
    <Skeleton width="50%" height="28px" />
  </div>
);
