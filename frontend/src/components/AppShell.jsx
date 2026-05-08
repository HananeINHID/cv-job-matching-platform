import React, { useState } from 'react';
import { Sidebar, Topbar } from './Layout';

/**
 * AppShell — Wrapper principal pour les pages authentifiées
 * Inclut la Sidebar + Topbar + le contenu principal
 */
const AppShell = ({ children, title, breadcrumb }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sidebar
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />

      {/* Contenu principal */}
      <div style={{
        flex: 1,
        marginLeft: '240px',
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        transition: 'margin-left 0.3s ease',
      }}
        className="main-content"
      >
        <style>{`
          @media (max-width: 768px) {
            .main-content { margin-left: 0 !important; }
          }
        `}</style>

        {/* Topbar */}
        <Topbar
          onMenuClick={() => setMobileOpen(true)}
          title={title}
          breadcrumb={breadcrumb}
        />

        {/* Page content */}
        <main style={{
          flex: 1,
          marginTop: '64px',
          padding: '2rem',
          backgroundColor: 'var(--bg-main)',
          boxSizing: 'border-box',
        }}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppShell;
