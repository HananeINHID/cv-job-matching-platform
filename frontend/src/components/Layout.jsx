import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext.jsx';
import {
  LayoutDashboard, Search, FileText, User, History,
  Settings, Briefcase, Sun, Moon, LogOut, Menu, X, ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/dashboard',  label: 'Dashboard',    icon: LayoutDashboard },
  { path: '/results',    label: 'Résultats',     icon: Search },
  { path: '/cv-form',   label: 'Mon Profil CV', icon: User },
];

/**
 * Sidebar — navigation latérale fixe (desktop) ou drawer (mobile)
 */
export const Sidebar = ({ mobileOpen, onMobileClose }) => {
  const { isDarkMode } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('userNom');
    navigate('/login');
  };

  const sidebarStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    height: '100vh',
    width: '240px',
    backgroundColor: 'var(--bg-surface)',
    borderRight: '1px solid var(--border-color)',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 100,
    boxShadow: 'var(--shadow-md)',
    transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease',
  };

  return (
    <>
      {/* Overlay mobile */}
      {mobileOpen && (
        <div
          onClick={onMobileClose}
          style={{
            position: 'fixed', inset: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 99,
            display: 'none',
          }}
          className="sidebar-overlay"
        />
      )}

      <style>{`
        @media (max-width: 768px) {
          .sidebar-desktop { transform: translateX(-100%) !important; }
          .sidebar-mobile-open { transform: translateX(0) !important; }
          .sidebar-overlay { display: block !important; }
        }
      `}</style>

      <aside
        style={sidebarStyle}
        className={`sidebar-desktop ${mobileOpen ? 'sidebar-mobile-open' : ''}`}
      >
        {/* Logo */}
        <div style={{
          padding: '1.5rem 1.25rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '36px', height: '36px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--gradient-primary)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: 'var(--shadow-glow)',
            }}>
              <Briefcase size={18} color="white" />
            </div>
            <span style={{
              fontSize: '18px', fontWeight: 800,
              color: 'var(--text-main)',
              letterSpacing: '-0.5px'
            }}>CV Matching</span>
          </div>
          <button
            onClick={onMobileClose}
            className="sidebar-close-btn"
            style={{
              display: 'none',
              background: 'transparent', border: 'none',
              cursor: 'pointer', padding: '4px',
              color: 'var(--text-muted)',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '1rem 0.75rem', overflowY: 'auto' }}>
          <p style={{
            fontSize: '10px', fontWeight: 700, letterSpacing: '1px',
            color: 'var(--text-muted)', textTransform: 'uppercase',
            padding: '0 0.5rem', marginBottom: '8px', marginTop: '4px',
          }}>Navigation</p>

          {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              onClick={onMobileClose}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 14px',
                borderRadius: 'var(--radius-md)',
                marginBottom: '6px',
                textDecoration: 'none',
                fontWeight: isActive ? 600 : 500,
                fontSize: '14px',
                color: isActive ? 'var(--color-primary)' : 'var(--text-muted)',
                backgroundColor: isActive ? 'var(--color-primary-light)' : 'transparent',
                transition: 'var(--transition-smooth)',
                position: 'relative',
              })}
              onMouseEnter={(e) => {
                if(!e.currentTarget.style.backgroundColor.includes('var(--color-primary-light)')) {
                  e.currentTarget.style.backgroundColor = 'rgba(100, 116, 139, 0.05)';
                  e.currentTarget.style.color = 'var(--text-main)';
                }
              }}
              onMouseLeave={(e) => {
                if(!e.currentTarget.style.backgroundColor.includes('var(--color-primary-light)')) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--text-muted)';
                }
              }}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span style={{
                      position: 'absolute',
                      left: 0, top: '50%', transform: 'translateY(-50%)',
                      width: '4px', height: '60%',
                      borderRadius: '0 4px 4px 0',
                      backgroundColor: 'var(--color-primary)',
                      boxShadow: 'var(--shadow-glow)',
                    }} />
                  )}
                  <Icon size={18} />
                  <span>{label}</span>
                  {isActive && (
                    <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.6 }} />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div style={{
          padding: '1rem 0.75rem',
          borderTop: '1px solid var(--border-color)',
        }}>
          <button
            onClick={handleLogout}
            style={{
              display: 'flex', alignItems: 'center', gap: '10px',
              width: '100%', padding: '10px 12px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(239, 68, 68, 0.08)',
              color: 'var(--color-danger)',
              border: 'none', cursor: 'pointer',
              fontSize: '14px', fontWeight: 600,
              fontFamily: 'inherit',
              transition: 'background 0.2s ease',
            }}
          >
            <LogOut size={18} />
            Déconnexion
          </button>
        </div>
      </aside>
    </>
  );
};

/**
 * Topbar — Navbar en haut avec avatar, dark mode toggle, hamburger mobile
 */
export const Topbar = ({ onMenuClick, title, breadcrumb }) => {
  const { isDarkMode, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const getNom = () => {
    const saved = localStorage.getItem('userNom');
    if (saved) return saved;
    const token = localStorage.getItem('token');
    if (!token) return 'Utilisateur';
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.username || 'Utilisateur';
    } catch { return 'Utilisateur'; }
  };

  const initiales = getNom().substring(0, 2).toUpperCase();

  return (
    <header 
      className="glass"
      style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      height: '72px',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 1.5rem 0 264px',
      zIndex: 90,
      boxShadow: 'var(--shadow-sm)',
      gap: '16px',
      transition: 'padding 0.3s ease',
    }}>
      {/* Hamburger mobile */}
      <button
        onClick={onMenuClick}
        className="hamburger-btn"
        style={{
          display: 'none',
          background: 'transparent', border: 'none',
          cursor: 'pointer', padding: '6px',
          color: 'var(--text-muted)', borderRadius: 'var(--radius-md)',
        }}
      >
        <Menu size={22} />
      </button>

      <style>{`
        @media (max-width: 768px) {
          .hamburger-btn { display: flex !important; }
          header { padding-left: 1rem !important; }
        }
      `}</style>

      {/* Breadcrumb / Title */}
      <div style={{ flex: 1 }}>
        {breadcrumb && (
          <p style={{ fontSize: '11px', color: 'var(--text-muted)', margin: '0 0 2px', fontWeight: 500 }}>
            {breadcrumb}
          </p>
        )}
        {title && (
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-main)', margin: 0, letterSpacing: '-0.5px' }}>
            {title}
          </h1>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Toggle Dark Mode */}
        <button
          onClick={toggleTheme}
          title={isDarkMode ? "Passer en mode clair" : "Passer en mode sombre"}
          style={{
            background: 'var(--color-primary-light)', border: 'none',
            cursor: 'pointer', padding: '10px',
            color: 'var(--color-primary)', borderRadius: 'var(--radius-full)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'var(--transition-smooth)',
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'rotate(15deg)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'rotate(0deg)'}
        >
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Avatar Utilisateur */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '12px',
          paddingLeft: '16px', borderLeft: '1px solid var(--border-color)',
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', display: 'none' }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)' }}>{getNom()}</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Utilisateur</span>
          </div>
          <div style={{
            width: '40px', height: '40px',
            borderRadius: 'var(--radius-full)',
            background: 'var(--gradient-primary)',
            color: 'white',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 700, fontSize: '14px',
            boxShadow: 'var(--shadow-sm)',
            border: '2px solid var(--bg-surface)'
          }}>
            {initiales}
          </div>
        </div>
      </div>
    </header>
  );
};
