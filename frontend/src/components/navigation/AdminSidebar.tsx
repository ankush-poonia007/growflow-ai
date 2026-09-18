import { useContext, useState } from 'react';
import { Link, useLocation } from 'react-router';
import { cn } from '@/utils/cn';
import { AuthContext } from '@/auth/AuthContext';
import './AdminSidebar.css';

export interface AdminSidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  className?: string;
}

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
}

const ADMIN_NAV_ITEMS: NavItem[] = [
  {
    label: 'Overview',
    to: '/admin/overview',
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
    label: 'Mentors',
    to: '/admin/mentors',
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
  {
    label: 'Groups',
    to: '/admin/groups',
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
        <line x1="9" y1="7" x2="15" y2="7" />
        <line x1="9" y1="11" x2="13" y2="11" />
      </svg>
    ),
  },
  {
    label: 'Projects',
    to: '/admin/projects',
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
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
      </svg>
    ),
  },
  {
    label: 'Definitions',
    to: '/admin/definitions',
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
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    label: 'AI Observatory',
    to: '/admin/ai',
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
        <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" />
      </svg>
    ),
  },
  {
    label: 'System Health',
    to: '/admin/system-health',
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
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
    ),
  },
  {
    label: 'Security & Audit',
    to: '/admin/security',
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
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
      </svg>
    ),
  },
  {
    label: 'Documents & RAG',
    to: '/admin/documents',
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
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    ),
  },
  {
    label: 'Platform Analytics',
    to: '/admin/analytics',
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
        <line x1="18" y1="20" x2="18" y2="10" />
        <line x1="12" y1="20" x2="12" y2="4" />
        <line x1="6" y1="20" x2="6" y2="14" />
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
  return 'AD';
}

export function AdminSidebar({ isCollapsed, onToggleCollapse, className }: AdminSidebarProps) {
  const [isHoverExpanded, setIsHoverExpanded] = useState(false);
  const location = useLocation();
  const auth = useContext(AuthContext);
  const user = auth?.user;

  const initials = getInitials(user?.fullName, user?.email);
  const displayName = user?.fullName?.trim() || user?.email?.trim() || '—';

  const isRouteActive = (to: string) => {
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
    if (to === '/admin/ai') {
      return location.pathname.startsWith('/admin/ai');
    }
    if (to === '/admin/system-health') {
      return location.pathname.startsWith('/admin/system-health');
    }
    if (to === '/admin/security') {
      return location.pathname.startsWith('/admin/security');
    }
    if (to === '/admin/documents') {
      return location.pathname.startsWith('/admin/documents');
    }
    if (to === '/admin/analytics') {
      return location.pathname.startsWith('/admin/analytics');
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
        'gf-admin-sidebar',
        effectivelyCollapsed && 'gf-admin-sidebar--collapsed',
        isHoverExpanded && 'gf-admin-sidebar--hover-expanded',
        className
      )}
      aria-label="Admin Governance Navigation"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleSidebarClick}
    >
      <div className="gf-admin-sidebar__header">
        <span className="gf-admin-sidebar__workspace-tag">GOVERN</span>
        {!effectivelyCollapsed && (
          <span className="gf-admin-sidebar__workspace-role">Admin Workplace</span>
        )}
      </div>

      <nav className="gf-admin-sidebar__nav" aria-label="Governance navigation">
        {!effectivelyCollapsed && (
          <div className="gf-admin-sidebar__nav-section-title" aria-hidden="true">
            Governance
          </div>
        )}
        {ADMIN_NAV_ITEMS.map((item) => {
          const active = isRouteActive(item.to);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn('gf-admin-sidebar__item', active && 'gf-admin-sidebar__item--active')}
              aria-current={active ? 'page' : undefined}
              title={effectivelyCollapsed ? item.label : undefined}
            >
              <span className="gf-admin-sidebar__icon">{item.icon}</span>
              <span className="gf-admin-sidebar__label">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Flexible Spacer */}
      <div className="gf-admin-sidebar__spacer" />

      {/* Bottom Profile & Settings Section */}
      <div className="gf-admin-sidebar__bottom">
        <div className="gf-admin-sidebar__profile-block">
          <Link
            to="/admin/profile"
            className={cn(
              'gf-admin-sidebar__profile-link',
              location.pathname.startsWith('/admin/profile') && 'gf-admin-sidebar__profile-link--active'
            )}
            title={effectivelyCollapsed ? `${displayName} (Profile)` : undefined}
            aria-label="Admin Profile"
          >
            <div className="gf-admin-sidebar__avatar" aria-hidden="true">
              {initials}
            </div>
            {!effectivelyCollapsed && (
              <div className="gf-admin-sidebar__profile-info">
                <span className="gf-admin-sidebar__profile-name">{displayName}</span>
                <span className="gf-admin-sidebar__profile-role">Admin Account</span>
              </div>
            )}
          </Link>

          <Link
            to="/admin/settings"
            className={cn(
              'gf-admin-sidebar__settings-btn',
              location.pathname.startsWith('/admin/settings') && 'gf-admin-sidebar__settings-btn--active'
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
          className="gf-admin-sidebar__collapse-btn"
          onClick={onToggleCollapse}
          aria-expanded={!isCollapsed}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <span className="gf-admin-sidebar__icon">
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
