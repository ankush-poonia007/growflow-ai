import { useState, useCallback } from 'react';
import { Link, useLocation } from 'react-router';
import { GrowFlowBrand } from '@/components/ui/Logo';
import { Button } from '@/components/ui/Button';
import { WorkplaceSelector } from './WorkplaceSelector';
import { MobileNav } from './MobileNav';
import { useAuth } from '@/auth/useAuth';
import { getDefaultDestinationForRole } from '@/auth/returnTo';
import { cn } from '@/utils/cn';
import './Header.css';

const NAV_LINKS = [
  { label: 'Features', to: '/features' },
  { label: 'Showcase', to: '/showcase' },
  { label: 'Documentation', to: '/documentation' },
  { label: 'Contact', to: '/contact' },
] as const;

export function Header() {
  const location = useLocation();
  const { isAuthenticated, signOut, user } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const workspaceDestination = getDefaultDestinationForRole(user?.role);

  const toggleMobile = useCallback(() => setMobileOpen((o) => !o), []);
  const closeMobile = useCallback(() => setMobileOpen(false), []);

  return (
    <>
      <header className="gf-header" role="banner">
        <div className="gf-header__inner">
          {/* Brand */}
          <Link to="/" aria-label="GrowFlow home">
            <GrowFlowBrand />
          </Link>

          {/* Desktop Navigation */}
          <nav className="gf-header__nav" aria-label="Main navigation">
            {NAV_LINKS.map(({ label, to }) => (
              <Link
                key={to}
                to={to}
                className={cn(
                  'gf-header__link',
                  location.pathname === to && 'gf-header__link--active',
                )}
              >
                {label}
              </Link>
            ))}
          </nav>

          {/* Actions */}
          <div className="gf-header__actions">
            <WorkplaceSelector />

            {isAuthenticated ? (
              <>
                <Button as="link" to={workspaceDestination} variant="secondary" size="sm">
                  Workspace
                </Button>
                <Button
                  as="button"
                  variant="tertiary"
                  size="sm"
                  onClick={() => {
                    void signOut();
                  }}
                >
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                {location.pathname !== '/auth/student/sign-in' && (
                  <Button as="link" to="/auth/student/sign-in" variant="secondary" size="sm">
                    Login
                  </Button>
                )}
                <Button as="link" to="/auth/student/register" variant="primary" size="sm">
                  Sign Up
                </Button>
              </>
            )}

            {/* Mobile hamburger */}
            <button
              className="gf-header__hamburger"
              onClick={toggleMobile}
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileOpen}
            >
              {mobileOpen ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M3 12h18M3 6h18M3 18h18" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Navigation Drawer */}
      <MobileNav isOpen={mobileOpen} onClose={closeMobile} />
    </>
  );
}
