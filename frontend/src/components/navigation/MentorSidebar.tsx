import { useContext, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router';
import { cn } from '@/utils/cn';
import { AuthContext } from '@/auth/AuthContext';
import './MentorSidebar.css';

export interface MentorSidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  className?: string;
}

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
}

const PRIMARY_MENTOR_NAV: NavItem[] = [
  {
    label: 'Overview',
    to: '/mentor/overview',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
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
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
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
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
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
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
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
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
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
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
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
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
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
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    label: 'AI Mentor',
    to: '/mentor/ai',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18" aria-hidden="true">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
  },
];

function getInitials(name?: string, email?: string): string {
  if (name && name.trim()) {
    const cleaned = name.trim().replace(/^(dr\.?|prof\.?|mr\.?|mrs\.?|ms\.?)\s+/i, '');
    const parts = cleaned.split(/\s+/);
    const first = parts[0];
    const last = parts.length > 1 ? parts[parts.length - 1] : undefined;
    if (first && last) {
      return (first.charAt(0) + last.charAt(0)).toUpperCase();
    }
    if (first) {
      return first.slice(0, 2).toUpperCase();
    }
  }
  if (email && email.trim()) {
    const username = email.trim().split('@')[0] || '';
    const parts = username.split(/[._-]/);
    if (parts.length >= 2 && parts[0] && parts[1]) {
      return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
    }
    if (username) {
      return username.slice(0, 2).toUpperCase();
    }
  }
  return 'ME';
}

export function MentorSidebar({ isCollapsed, onToggleCollapse, className }: MentorSidebarProps) {
  const [isHoverExpanded, setIsHoverExpanded] = useState(false);
  const location = useLocation();
  const params = useParams<{ groupId?: string }>();
  const auth = useContext(AuthContext);
  const user = auth?.user;

  const initials = getInitials(user?.fullName, user?.email);
  const displayName = user?.fullName?.trim() || user?.email?.trim() || '—';
  const roleLabel =
    user?.role === 'MENTOR'
      ? 'Mentor Account'
      : user?.role
      ? `${user.role.charAt(0) + user.role.slice(1).toLowerCase()} Account`
      : 'Account';

  // Extract groupId from route if matching /mentor/groups/:groupId
  const groupMatch = location.pathname.match(/^\/mentor\/groups\/([^/]+)/);
  const matchedGroupId = groupMatch && groupMatch[1] !== 'new' ? groupMatch[1] : params.groupId;

  const isRouteActive = (to: string, exact = false) => {
    if (exact) {
      return location.pathname === to;
    }
    return location.pathname === to || location.pathname.startsWith(to + '/');
  };

  // Effective collapsed state: collapsed unless temporarily hover-expanded
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
    // If clicking outside an active navigation link/button, expand sidebar permanently
    if (!interactive) {
      onToggleCollapse();
      setIsHoverExpanded(false);
    }
  };

  return (
    <aside
      className={cn(
        'gf-mentor-sidebar',
        effectivelyCollapsed && 'gf-mentor-sidebar--collapsed',
        isHoverExpanded && 'gf-mentor-sidebar--hover-expanded',
        className
      )}
      aria-label="Mentor Supervise Navigation"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleSidebarClick}
    >
      <div className="gf-mentor-sidebar__header">
        <span className="gf-mentor-sidebar__workspace-tag">SUPERVISE</span>
        {!effectivelyCollapsed && <span className="gf-mentor-sidebar__workspace-role">Mentor Workplace</span>}
      </div>

      <nav className="gf-mentor-sidebar__nav" aria-label="Mentor workplace navigation">
        {!effectivelyCollapsed && (
          <div className="gf-mentor-sidebar__nav-section-title" aria-hidden="true">
            Workspace
          </div>
        )}
        {PRIMARY_MENTOR_NAV.map((item) => {
          let active = false;
          if (item.to === '/mentor/groups') {
            active = location.pathname === '/mentor/groups' || location.pathname === '/mentor/groups/new';
          } else if (item.to === '/mentor/projects') {
            active =
              (location.pathname === '/mentor/projects' ||
                location.pathname.startsWith('/mentor/projects/new') ||
                /^\/mentor\/projects\/[^/]+/.test(location.pathname)) &&
              !location.pathname.startsWith('/mentor/projects/instances');
          } else if (item.to === '/mentor/students') {
            active = isRouteActive('/mentor/students');
          } else if (item.to === '/mentor/project-instances') {
            active =
              isRouteActive('/mentor/project-instances') ||
              isRouteActive('/mentor/projects/instances');
          } else if (item.to === '/mentor/at-risk') {
            active = isRouteActive('/mentor/at-risk');
          } else if (item.to === '/mentor/help-requests') {
            active = isRouteActive('/mentor/help-requests');
          } else {
            active = location.pathname === item.to;
          }

          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn('gf-mentor-sidebar__item', active && 'gf-mentor-sidebar__item--active')}
              aria-current={active ? 'page' : undefined}
              title={effectivelyCollapsed ? item.label : undefined}
            >
              <span className="gf-mentor-sidebar__icon">{item.icon}</span>
              <span className="gf-mentor-sidebar__label">{item.label}</span>
            </Link>
          );
        })}

        {/* Contextual Group Subnavigation */}
        {matchedGroupId && (
          <div className="gf-mentor-sidebar__subnav">
            {!effectivelyCollapsed && (
              <div className="gf-mentor-sidebar__subnav-header">
                <span className="gf-mentor-sidebar__subnav-title">Active Group</span>
                <Link to="/mentor/groups" className="gf-mentor-sidebar__subnav-back" title="All Groups">
                  &larr; All
                </Link>
              </div>
            )}

            <Link
              to={`/mentor/groups/${matchedGroupId}`}
              className={cn(
                'gf-mentor-sidebar__subitem',
                location.pathname === `/mentor/groups/${matchedGroupId}` && 'gf-mentor-sidebar__subitem--active'
              )}
              aria-current={location.pathname === `/mentor/groups/${matchedGroupId}` ? 'page' : undefined}
              title={effectivelyCollapsed ? 'Workspace' : undefined}
            >
              <span className="gf-mentor-sidebar__subicon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                  <polyline points="9 22 9 12 15 12 15 22" />
                </svg>
              </span>
              <span className="gf-mentor-sidebar__label">Workspace</span>
            </Link>

            <Link
              to={`/mentor/groups/${matchedGroupId}/students`}
              className={cn(
                'gf-mentor-sidebar__subitem',
                isRouteActive(`/mentor/groups/${matchedGroupId}/students`) && 'gf-mentor-sidebar__subitem--active'
              )}
              aria-current={isRouteActive(`/mentor/groups/${matchedGroupId}/students`) ? 'page' : undefined}
              title={effectivelyCollapsed ? 'Students' : undefined}
            >
              <span className="gf-mentor-sidebar__subicon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                </svg>
              </span>
              <span className="gf-mentor-sidebar__label">Students</span>
            </Link>

            <Link
              to={`/mentor/groups/${matchedGroupId}/projects`}
              className={cn(
                'gf-mentor-sidebar__subitem',
                isRouteActive(`/mentor/groups/${matchedGroupId}/projects`) && 'gf-mentor-sidebar__subitem--active'
              )}
              aria-current={isRouteActive(`/mentor/groups/${matchedGroupId}/projects`) ? 'page' : undefined}
              title={effectivelyCollapsed ? 'Projects' : undefined}
            >
              <span className="gf-mentor-sidebar__subicon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                </svg>
              </span>
              <span className="gf-mentor-sidebar__label">Projects</span>
            </Link>

            <Link
              to={`/mentor/groups/${matchedGroupId}/at-risk`}
              className={cn(
                'gf-mentor-sidebar__subitem',
                'gf-mentor-sidebar__subitem--at-risk',
                isRouteActive(`/mentor/groups/${matchedGroupId}/at-risk`) && 'gf-mentor-sidebar__subitem--active'
              )}
              aria-current={isRouteActive(`/mentor/groups/${matchedGroupId}/at-risk`) ? 'page' : undefined}
              title={effectivelyCollapsed ? 'At-Risk Triage' : undefined}
            >
              <span className="gf-mentor-sidebar__subicon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </span>
              <span className="gf-mentor-sidebar__label">At-Risk</span>
            </Link>
          </div>
        )}
      </nav>

      {/* Flexible Spacer */}
      <div className="gf-mentor-sidebar__spacer" />

      {/* Bottom Profile & Settings Block */}
      <div className="gf-mentor-sidebar__bottom">
        <div className="gf-mentor-sidebar__profile-block">
          <Link
            to="/mentor/profile"
            className={cn(
              'gf-mentor-sidebar__profile-link',
              isRouteActive('/mentor/profile') && 'gf-mentor-sidebar__profile-link--active'
            )}
            title={effectivelyCollapsed ? `${displayName} (Profile)` : undefined}
            aria-label="Mentor Profile"
          >
            <div className="gf-mentor-sidebar__avatar" aria-hidden="true">
              {user?.avatarUrl ? (
                <img
                  src={user.avatarUrl}
                  alt={displayName}
                  className="gf-mentor-sidebar__avatar-img"
                />
              ) : (
                initials
              )}
            </div>
            {!effectivelyCollapsed && (
              <div className="gf-mentor-sidebar__profile-info">
                <span className="gf-mentor-sidebar__profile-name">
                  {displayName}
                </span>
                <span className="gf-mentor-sidebar__profile-role">{roleLabel}</span>
              </div>
            )}
          </Link>

          <Link
            to="/mentor/settings"
            className={cn(
              'gf-mentor-sidebar__settings-btn',
              isRouteActive('/mentor/settings') && 'gf-mentor-sidebar__settings-btn--active'
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
          className="gf-mentor-sidebar__collapse-btn"
          onClick={onToggleCollapse}
          aria-expanded={!isCollapsed}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <span className="gf-mentor-sidebar__icon">
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
