import { useEffect, useRef, useContext } from 'react';
import { Link, useLocation } from 'react-router';
import { cn } from '@/utils/cn';
import { AuthContext } from '@/auth/AuthContext';
import { Button } from '@/components/ui/Button';
import './MobileWorkspaceDrawer.css';

export type WorkplaceType = 'BUILD' | 'SUPERVISE' | 'GOVERN';

export interface MobileWorkspaceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  workplace?: WorkplaceType;
}

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
}

const STUDENT_NAV_ITEMS: NavItem[] = [
  {
    label: 'Dashboard',
    to: '/student/dashboard',
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        width="20"
        height="20"
        aria-hidden="true"
      >
        <rect x="3" y="3" width="7" height="9" rx="1.5" />
        <rect x="14" y="3" width="7" height="5" rx="1.5" />
        <rect x="14" y="12" width="7" height="9" rx="1.5" />
        <rect x="3" y="16" width="7" height="5" rx="1.5" />
      </svg>
    ),
  },
  {
    label: 'Projects',
    to: '/student/projects',
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        width="20"
        height="20"
        aria-hidden="true"
      >
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
      </svg>
    ),
  },
  {
    label: 'Mentor Projects',
    to: '/student/projects/mentor-catalog',
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        width="20"
        height="20"
        aria-hidden="true"
      >
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        <path d="M9 10h6" />
        <path d="M12 7v6" />
      </svg>
    ),
  },
  {
    label: 'My Groups',
    to: '/student/groups',
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        width="20"
        height="20"
        aria-hidden="true"
      >
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
];

const MENTOR_NAV_ITEMS: NavItem[] = [
  {
    label: 'Overview',
    to: '/mentor/overview',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <rect x="3" y="3" width="7" height="9" rx="1.5" />
        <rect x="14" y="3" width="7" height="5" rx="1.5" />
        <rect x="14" y="12" width="7" height="9" rx="1.5" />
        <rect x="3" y="16" width="7" height="5" rx="1.5" />
      </svg>
    ),
  },
  {
    label: 'Groups',
    to: '/mentor/groups',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    label: 'Definitions',
    to: '/mentor/projects',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    ),
  },
  {
    label: 'Students',
    to: '/mentor/students',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    label: 'Project Instances',
    to: '/mentor/project-instances',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
        <line x1="8" y1="21" x2="16" y2="21" />
        <line x1="12" y1="17" x2="12" y2="21" />
      </svg>
    ),
  },
  {
    label: 'At Risk',
    to: '/mentor/at-risk',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
  },
  {
    label: 'Help Requests',
    to: '/mentor/help-requests',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
  },
  {
    label: 'Activity',
    to: '/mentor/activity',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    label: 'AI Mentor',
    to: '/mentor/ai',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
  },
];

const ADMIN_NAV_ITEMS: NavItem[] = [
  {
    label: 'Overview',
    to: '/admin/overview',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <rect x="3" y="3" width="7" height="9" rx="1.5" />
        <rect x="14" y="3" width="7" height="5" rx="1.5" />
        <rect x="14" y="12" width="7" height="9" rx="1.5" />
        <rect x="3" y="16" width="7" height="5" rx="1.5" />
      </svg>
    ),
  },
  {
    label: 'Mentors',
    to: '/admin/mentors',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    label: 'Students',
    to: '/admin/students',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    label: 'Groups',
    to: '/admin/groups',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        <line x1="9" y1="7" x2="15" y2="7" />
        <line x1="9" y1="11" x2="13" y2="11" />
      </svg>
    ),
  },
  {
    label: 'Projects',
    to: '/admin/projects',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
      </svg>
    ),
  },
  {
    label: 'Definitions',
    to: '/admin/definitions',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <polygon points="12 2 2 7 12 12 22 7 12 2" />
        <polyline points="2 17 12 22 22 17" />
        <polyline points="2 12 12 17 22 12" />
      </svg>
    ),
  },
  {
    label: 'Instances',
    to: '/admin/instances',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="20" height="20" aria-hidden="true">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
];

export function MobileWorkspaceDrawer({
  isOpen,
  onClose,
  workplace = 'BUILD',
}: MobileWorkspaceDrawerProps) {
  const location = useLocation();
  const auth = useContext(AuthContext);
  const user = auth?.user;
  const signOut = auth?.signOut || (() => Promise.resolve());
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Lock body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      closeBtnRef.current?.focus();
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Close when route changes
  useEffect(() => {
    onClose();
  }, [location.pathname, onClose]);

  // Determine workplace config
  let navItems: NavItem[] = STUDENT_NAV_ITEMS;
  let profileRoute = '/profile';
  let settingsRoute = '/settings';
  let ariaLabel = 'Student Workspace Menu';

  if (workplace === 'SUPERVISE') {
    navItems = MENTOR_NAV_ITEMS;
    profileRoute = '/mentor/profile';
    settingsRoute = '/mentor/settings';
    ariaLabel = 'Mentor Workspace Menu';
  } else if (workplace === 'GOVERN') {
    navItems = ADMIN_NAV_ITEMS;
    profileRoute = '/admin/profile';
    settingsRoute = '/admin/settings';
    ariaLabel = 'Admin Workspace Menu';
  }

  const isRouteActive = (to: string) => {
    if (workplace === 'BUILD') {
      if (to === '/student/dashboard') {
        return location.pathname === '/student/dashboard';
      }
      if (to === '/student/projects/mentor-catalog') {
        return location.pathname.startsWith('/student/projects/mentor-catalog');
      }
      if (to === '/student/projects') {
        return (
          location.pathname.startsWith('/student/projects') &&
          !location.pathname.startsWith('/student/projects/mentor-catalog')
        );
      }
      return location.pathname.startsWith(to);
    }

    if (workplace === 'SUPERVISE') {
      if (to === '/mentor/groups') {
        return location.pathname === '/mentor/groups' || location.pathname === '/mentor/groups/new';
      }
      if (to === '/mentor/projects') {
        return (
          (location.pathname === '/mentor/projects' ||
            location.pathname.startsWith('/mentor/projects/new') ||
            /^\/mentor\/projects\/[^/]+/.test(location.pathname)) &&
          !location.pathname.startsWith('/mentor/projects/instances')
        );
      }
      if (to === '/mentor/students') {
        return location.pathname.startsWith('/mentor/students');
      }
      if (to === '/mentor/project-instances') {
        return (
          location.pathname.startsWith('/mentor/project-instances') ||
          location.pathname.startsWith('/mentor/projects/instances')
        );
      }
      if (to === '/mentor/at-risk') {
        return location.pathname.startsWith('/mentor/at-risk');
      }
      if (to === '/mentor/help-requests') {
        return location.pathname.startsWith('/mentor/help-requests');
      }
      return location.pathname === to;
    }

    if (workplace === 'GOVERN') {
      if (to === '/admin/overview') {
        return location.pathname === '/admin/overview';
      }
      if (to === '/admin/mentors') {
        return location.pathname.startsWith('/admin/mentors');
      }
      if (to === '/admin/students') {
        return location.pathname.startsWith('/admin/students');
      }
      if (to === '/admin/groups') {
        return location.pathname.startsWith('/admin/groups');
      }
      if (to === '/admin/projects') {
        return location.pathname === '/admin/projects';
      }
      if (to === '/admin/definitions') {
        return location.pathname.startsWith('/admin/definitions');
      }
      if (to === '/admin/instances') {
        return location.pathname.startsWith('/admin/instances');
      }
      return location.pathname.startsWith(to);
    }

    return location.pathname.startsWith(to);
  };

  // Authoritative identity fallback: fullName.trim() -> email -> "—"
  const displayName = user?.fullName?.trim() || user?.email?.trim() || '—';

  return (
    <div
      className={cn('gf-mobile-drawer', isOpen && 'gf-mobile-drawer--open')}
      role="dialog"
      aria-modal="true"
      aria-label={ariaLabel}
    >
      <div className="gf-mobile-drawer__backdrop" onClick={onClose} aria-hidden="true" />

      <div className="gf-mobile-drawer__panel">
        <div className="gf-mobile-drawer__header">
          <div className="gf-mobile-drawer__title-group">
            <span className="gf-mobile-drawer__tag">{workplace}</span>
            <h2 className="gf-mobile-drawer__title">Workspace</h2>
          </div>

          <button
            ref={closeBtnRef}
            type="button"
            className="gf-mobile-drawer__close-btn"
            onClick={onClose}
            aria-label="Close workspace menu"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              width="20"
              height="20"
              aria-hidden="true"
            >
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="gf-mobile-drawer__nav" aria-label="Mobile workspace navigation">
          {navItems.map((item) => {
            const active = isRouteActive(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn('gf-mobile-drawer__item', active && 'gf-mobile-drawer__item--active')}
                aria-current={active ? 'page' : undefined}
                onClick={onClose}
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            );
          })}

          <div className="gf-mobile-drawer__divider" role="separator" />

          <Link
            to={profileRoute}
            className={cn('gf-mobile-drawer__item', location.pathname.startsWith(profileRoute) && 'gf-mobile-drawer__item--active')}
            aria-current={location.pathname.startsWith(profileRoute) ? 'page' : undefined}
            onClick={onClose}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="20"
              height="20"
              aria-hidden="true"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <span>Profile</span>
          </Link>

          <Link
            to={settingsRoute}
            className={cn('gf-mobile-drawer__item', location.pathname.startsWith(settingsRoute) && 'gf-mobile-drawer__item--active')}
            aria-current={location.pathname.startsWith(settingsRoute) ? 'page' : undefined}
            onClick={onClose}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="20"
              height="20"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            <span>Settings</span>
          </Link>
        </nav>

        <div className="gf-mobile-drawer__footer">
          <div className="gf-mobile-drawer__user">
            Signed in as <strong>{displayName}</strong>
          </div>
          <Button
            as="button"
            variant="secondary"
            size="sm"
            onClick={() => {
              onClose();
              void signOut();
            }}
          >
            Sign Out
          </Button>
        </div>
      </div>
    </div>
  );
}
