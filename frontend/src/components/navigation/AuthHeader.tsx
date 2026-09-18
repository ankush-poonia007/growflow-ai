import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router';
import { GrowFlowBrand } from '@/components/ui/Logo';
import { Button } from '@/components/ui/Button';
import { WorkplaceSelector } from './WorkplaceSelector';
import { GlobalSearchModal } from './GlobalSearchModal';
import { NotificationsPopover } from './NotificationsPopover';
import { useAuth } from '@/auth/useAuth';
import { useNotifications } from '@/hooks/useNotifications';
import './AuthHeader.css';

export interface AuthHeaderProps {
  onToggleMobileNav: () => void;
  isMobileNavOpen: boolean;
  workplace?: 'BUILD' | 'SUPERVISE' | 'GOVERN';
}

export function AuthHeader({
  onToggleMobileNav,
  isMobileNavOpen,
  workplace = 'BUILD',
}: AuthHeaderProps) {
  const { user, isRoleResolving, signOut } = useAuth();

  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  const notificationsRef = useRef<HTMLDivElement>(null);

  const {
    notifications,
    unreadCount,
    isLoading: isNotifsLoading,
    error: notifsError,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
  } = useNotifications();

  // Authoritative role from backend session identity; never fabricate or default to STUDENT
  const roleLabel = user?.role || (isRoleResolving ? 'Verifying...' : '');
  const displayName = user?.fullName?.trim() || user?.email?.trim() || '';

  // Global Keydown Listeners (Escape and Ctrl/Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      } else if (e.key === 'Escape') {
        setIsSearchOpen(false);
        setIsNotificationsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Outside click handler for notifications
  useEffect(() => {
    if (!isNotificationsOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (
        notificationsRef.current &&
        !notificationsRef.current.contains(e.target as Node)
      ) {
        setIsNotificationsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isNotificationsOpen]);

  const handleToggleNotifications = () => {
    if (!isNotificationsOpen) {
      fetchNotifications();
    }
    setIsNotificationsOpen((prev) => !prev);
  };

  return (
    <>
      <header className="gf-auth-header" role="banner">
        <div className="gf-auth-header__inner">
          <div className="gf-auth-header__left">
            <button
              type="button"
              className="gf-auth-header__hamburger"
              onClick={onToggleMobileNav}
              aria-label={isMobileNavOpen ? 'Close workspace menu' : 'Open workspace menu'}
              aria-expanded={isMobileNavOpen}
            >
              {isMobileNavOpen ? (
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
              ) : (
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
                  <path d="M3 12h18M3 6h18M3 18h18" />
                </svg>
              )}
            </button>

            {/* GrowFlow Brand links to public Landing page per Batch 3 specification */}
            <Link to="/" aria-label="GrowFlow Home" className="gf-auth-header__brand-link">
              <GrowFlowBrand />
            </Link>

            <span className="gf-auth-header__context-tag">{workplace}</span>
          </div>

          <div className="gf-auth-header__actions">
            {/* Search trigger */}
            <button
              type="button"
              className="gf-auth-header__icon-btn"
              onClick={() => setIsSearchOpen(true)}
              aria-label="Search workspace"
              title="Search workspace (Ctrl+K)"
              aria-haspopup="dialog"
              aria-expanded={isSearchOpen}
            >
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
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </button>

            {/* Notifications trigger container */}
            <div className="gf-auth-header__notifications-container" ref={notificationsRef}>
              <div className="gf-auth-header__bell-wrapper">
                <button
                  type="button"
                  className="gf-auth-header__icon-btn"
                  onClick={handleToggleNotifications}
                  aria-label={unreadCount > 0 ? `Notifications (${unreadCount} unread)` : 'Notifications'}
                  title="Notifications"
                  aria-haspopup="dialog"
                  aria-expanded={isNotificationsOpen}
                >
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
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                  </svg>
                </button>
                {unreadCount > 0 && (
                  <span className="gf-auth-header__unread-dot" aria-hidden="true">
                    {unreadCount > 99 ? '99+' : unreadCount}
                  </span>
                )}
              </div>

              {/* Real Notifications Popover */}
              <NotificationsPopover
                isOpen={isNotificationsOpen}
                onClose={() => setIsNotificationsOpen(false)}
                notifications={notifications}
                unreadCount={unreadCount}
                isLoading={isNotifsLoading}
                error={notifsError}
                onMarkAsRead={markAsRead}
                onMarkAllAsRead={markAllAsRead}
                onRefresh={fetchNotifications}
              />
            </div>

            <WorkplaceSelector />

            {/* User badge */}
            <div className="gf-auth-header__user" title={user?.email || undefined}>
              {displayName && <span className="gf-auth-header__user-name">{displayName}</span>}
              {roleLabel && <span className="gf-auth-header__user-role">{roleLabel}</span>}
            </div>

            <Button
              as="button"
              variant="tertiary"
              size="sm"
              onClick={() => void signOut()}
              className="gf-auth-header__signout-btn"
            >
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Real Global Search Modal */}
      <GlobalSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        workplace={workplace}
      />
    </>
  );
}
