import React from 'react';

/**
 * EmptyState — Illustration SVG + message quand la liste est vide
 */
export const EmptyState = ({
  title = 'Aucun résultat',
  description = '',
  action,
  icon,
}) => (
  <div style={{
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '3rem 2rem',
    textAlign: 'center',
    gap: '16px',
  }}>
    {icon || (
      <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="60" cy="60" r="56" fill="var(--color-primary-light)" />
        <path d="M40 55C40 46.716 46.716 40 55 40H65C73.284 40 80 46.716 80 55V65C80 73.284 73.284 80 65 80H55C46.716 80 40 73.284 40 65V55Z"
          fill="var(--color-primary)" fillOpacity="0.15" stroke="var(--color-primary)" strokeWidth="1.5" />
        <path d="M52 60H68M60 52V68" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" />
        <circle cx="85" cy="85" r="12" fill="var(--color-primary)" />
        <path d="M81 85H89M85 81V89" stroke="white" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )}
    <div>
      <h3 style={{
        margin: 0, fontSize: '16px', fontWeight: 700,
        color: 'var(--text-main)',
      }}>{title}</h3>
      {description && (
        <p style={{
          margin: '6px 0 0', fontSize: '14px',
          color: 'var(--text-muted)', maxWidth: '300px',
        }}>{description}</p>
      )}
    </div>
    {action && <div>{action}</div>}
  </div>
);

/**
 * EmptyOffers — État vide spécifique pour les offres
 */
export const EmptyOffers = ({ onRetry }) => (
  <EmptyState
    title="Aucune offre trouvée"
    description="Essayez de modifier votre recherche ou de sélectionner une autre source."
    icon={
      <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
        <circle cx="60" cy="60" r="56" fill="var(--color-primary-light)" />
        <rect x="32" y="38" width="56" height="44" rx="6" fill="white" stroke="var(--color-primary)" strokeWidth="1.5" />
        <path d="M42 50H78M42 58H66M42 66H58" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeOpacity="0.5"/>
        <circle cx="83" cy="83" r="14" fill="var(--color-danger)" />
        <path d="M79 83H87" stroke="white" strokeWidth="2" strokeLinecap="round" />
      </svg>
    }
    action={onRetry && (
      <button
        onClick={onRetry}
        style={{
          padding: '10px 24px',
          background: 'var(--color-primary)',
          color: 'white',
          border: 'none',
          borderRadius: 'var(--radius-md)',
          fontWeight: 600,
          cursor: 'pointer',
          fontFamily: 'inherit',
          fontSize: '14px',
        }}
      >
        Retourner au dashboard
      </button>
    )}
  />
);

/**
 * EmptyHistory — État vide pour l'historique
 */
export const EmptyHistory = () => (
  <EmptyState
    title="Aucune recherche récente"
    description="Lancez votre première recherche depuis le dashboard."
    icon={
      <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
        <circle cx="40" cy="40" r="36" fill="var(--color-primary-light)" />
        <circle cx="38" cy="36" r="14" stroke="var(--color-primary)" strokeWidth="2" fill="none" />
        <path d="M48 48L57 57" stroke="var(--color-primary)" strokeWidth="2.5" strokeLinecap="round" />
      </svg>
    }
  />
);
