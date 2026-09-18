import { useEffect, useRef } from 'react';
import { Link } from 'react-router';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/auth/useAuth';
import { getDefaultDestinationForRole } from '@/auth/returnTo';
import { cn } from '@/utils/cn';
import './MobileNav.css';

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

const NAV_LINKS = [
  { label: 'Features', to: '/features' },
  { label: 'Showcase', to: '/showcase' },
  { label: 'Documentation', to: '/documentation' },
  { label: 'Contact', to: '/contact' },
];

export function MobileNav({ isOpen, onClose }: MobileNavProps) {
  const { isAuthenticated, signOut, user } = useAuth();
  const panelRef = useRef<HTMLDivElement>(null);
  const currentRole = user?.role ? String(user.role).toUpperCase() : null;
  const workspaceDestination = getDefaultDestinationForRole(user?.role);

  const workplaces = [
    {
      label: 'BUILD — Student',
      to: !isAuthenticated
        ? '/auth/student/sign-in'
        : currentRole === 'STUDENT'
        ? '/student/dashboard'
        : '',
      disabled: isAuthenticated && currentRole !== 'STUDENT',
    },
    {
      label: 'SUPERVISE — Mentor',
      to: !isAuthenticated
        ? '/auth/mentor/sign-in'
        : currentRole === 'MENTOR'
        ? '/mentor/overview'
        : '',
      disabled: isAuthenticated && currentRole !== 'MENTOR',
    },
    {
      label: 'GOVERN — Admin',
      to: !isAuthenticated
        ? '/auth/admin/sign-in'
        : currentRole === 'ADMIN'
        ? '/admin/overview'
        : '',
      disabled: isAuthenticated && currentRole !== 'ADMIN',
    },
  ];

  // Trap focus and handle Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', handleKey);

    return () => {
      document.body.style.overflow = '';
      document.removeEventListener('keydown', handleKey);
    };
  }, [isOpen, onClose]);

  return (
    <div
      className={cn('gf-mobile-nav', isOpen && 'gf-mobile-nav--open')}
      aria-hidden={!isOpen}
    >
      <div className="gf-mobile-nav__backdrop" onClick={onClose} />

      <div
        className="gf-mobile-nav__panel"
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label="Navigation menu"
      >
        <button
          className="gf-mobile-nav__close"
          onClick={onClose}
          aria-label="Close menu"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>

        {/* Navigation Links */}
        <nav className="gf-mobile-nav__section" aria-label="Pages">
          {NAV_LINKS.map(({ label, to }) => (
            <Link key={to} to={to} className="gf-mobile-nav__link" onClick={onClose}>
              {label}
            </Link>
          ))}
        </nav>

        {/* Workplaces */}
        <div className="gf-mobile-nav__section">
          <span className="gf-mobile-nav__section-label">Workplaces</span>
          {workplaces.map(({ label, to, disabled }) =>
            disabled || !to ? (
              <span
                key={label}
                className="gf-mobile-nav__link gf-mobile-nav__link--disabled"
                aria-disabled="true"
              >
                {label}
              </span>
            ) : (
              <Link key={label} to={to} className="gf-mobile-nav__link" onClick={onClose}>
                {label}
              </Link>
            ),
          )}
        </div>

        {/* Auth Actions */}
        <div className="gf-mobile-nav__auth">
          {isAuthenticated ? (
            <>
              <Button
                as="link"
                to={workspaceDestination}
                variant="secondary"
                fullWidth
                onClick={onClose}
              >
                Workspace
              </Button>
              <Button
                as="button"
                variant="tertiary"
                fullWidth
                onClick={() => {
                  onClose();
                  void signOut();
                }}
              >
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Button
                as="link"
                to="/auth/student/sign-in"
                variant="secondary"
                fullWidth
                onClick={onClose}
              >
                Login
              </Button>
              <Button
                as="link"
                to="/auth/student/register"
                variant="primary"
                fullWidth
                onClick={onClose}
              >
                Sign Up
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
