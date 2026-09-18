import { useContext, useState } from 'react';
import { Link, useLocation } from 'react-router';
import { cn } from '@/utils/cn';
import { AuthContext } from '@/auth/AuthContext';
import './Sidebar.css';

export interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  className?: string;
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
        width="18"
        height="18"
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
        width="18"
        height="18"
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
        width="18"
        height="18"
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
        width="18"
        height="18"
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

function getInitials(name?: string, email?: string): string {
  if (name && name.trim()) {
    const parts = name.trim().split(/\s+/);
    const first = parts[0];
    const second = parts[1];
    if (parts.length >= 2 && first && second) {
      return (first.charAt(0) + second.charAt(0)).toUpperCase();
    }
    if (first) {
      return first.slice(0, 2).toUpperCase();
    }
  }
  if (email) {
    return email.slice(0, 2).toUpperCase();
  }
  return 'ST';
}

export function Sidebar({ isCollapsed, onToggleCollapse, className }: SidebarProps) {
  const [isHoverExpanded, setIsHoverExpanded] = useState(false);
  const location = useLocation();
  const auth = useContext(AuthContext);
  const user = auth?.user;

  const initials = getInitials(user?.fullName, user?.email);
  const displayName = user?.fullName?.trim() || user?.email?.trim() || '—';

  const isRouteActive = (to: string) => {
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
  };

  // Effective collapsed state: collapsed unless hover-expanded
  const effectivelyCollapsed = isCollapsed && !isHoverExpanded;

  const handleMouseEnter = () => {
    if (isCollapsed) {
      setIsHoverExpanded(true);
    }
  };

  const handleMouseLeave = () => {
    setIsHoverExpanded(false);
  };

  const handleSidebarClick = (e: React.MouseEvent) => {
    if (!isCollapsed) return;
    const target = e.target as HTMLElement;
    const interactive = target.closest('a, button');
    if (!interactive) {
      onToggleCollapse();
      setIsHoverExpanded(false);
    }
  };

  return (
    <aside
      className={cn(
        'gf-sidebar',
        effectivelyCollapsed && 'gf-sidebar--collapsed',
        isHoverExpanded && 'gf-sidebar--hover-expanded',
        className
      )}
      aria-label="Student Workspace Navigation"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleSidebarClick}
    >
      <div className="gf-sidebar__header">
        <span className="gf-sidebar__workspace-tag">BUILD</span>
        {!effectivelyCollapsed && <span className="gf-sidebar__workspace-role">Student Workplace</span>}
      </div>

      <nav className="gf-sidebar__nav" aria-label="Main workplace navigation">
        {!effectivelyCollapsed && (
          <div className="gf-sidebar__nav-section-title" aria-hidden="true">
            Workspace
          </div>
        )}
        {STUDENT_NAV_ITEMS.map((item) => {
          const active = isRouteActive(item.to);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn('gf-sidebar__item', active && 'gf-sidebar__item--active')}
              aria-current={active ? 'page' : undefined}
              title={effectivelyCollapsed ? item.label : undefined}
            >
              <span className="gf-sidebar__icon">{item.icon}</span>
              <span className="gf-sidebar__label">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Flexible Spacer */}
      <div className="gf-sidebar__spacer" />

      {/* Bottom Profile & Settings Block */}
      <div className="gf-sidebar__bottom">
        <div className="gf-sidebar__profile-block">
          <Link
            to="/profile"
            className={cn(
              'gf-sidebar__profile-link',
              isRouteActive('/profile') && 'gf-sidebar__profile-link--active'
            )}
            title={effectivelyCollapsed ? `${displayName} (Profile)` : undefined}
            aria-label="Student Profile"
          >
            <div className="gf-sidebar__avatar" aria-hidden="true">
              {initials}
            </div>
            {!effectivelyCollapsed && (
              <div className="gf-sidebar__profile-info">
                <span className="gf-sidebar__profile-name">{displayName}</span>
                <span className="gf-sidebar__profile-role">Student Account</span>
              </div>
            )}
          </Link>

          <Link
            to="/settings"
            className={cn(
              'gf-sidebar__settings-btn',
              isRouteActive('/settings') && 'gf-sidebar__settings-btn--active'
            )}
            title="Workspace Settings"
            aria-label="Workspace Settings"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="18"
              height="18"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
          </Link>
        </div>

        <button
          type="button"
          className="gf-sidebar__collapse-btn"
          onClick={onToggleCollapse}
          aria-expanded={!isCollapsed}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <span className="gf-sidebar__icon">
            {effectivelyCollapsed ? (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                width="16"
                height="16"
                aria-hidden="true"
              >
                <path d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            ) : (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                width="16"
                height="16"
                aria-hidden="true"
              >
                <path d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            )}
          </span>
          {!effectivelyCollapsed && <span>Collapse sidebar</span>}
        </button>
      </div>
    </aside>
  );
}

