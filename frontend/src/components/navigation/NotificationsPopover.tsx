import { useNavigate } from 'react-router';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import type { NotificationItem } from '@/lib/api/types';
import './NotificationsPopover.css';

export interface NotificationsPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: NotificationItem[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
  onMarkAsRead: (id: string) => Promise<void>;
  onMarkAllAsRead: () => Promise<void>;
  onRefresh?: () => Promise<void>;
}

function formatRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSec < 60) return 'Just now';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    if (diffSec < 604800) return `${Math.floor(diffSec / 86400)}d ago`;
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
}

export function NotificationsPopover({
  isOpen,
  onClose,
  notifications,
  unreadCount,
  isLoading,
  error,
  onMarkAsRead,
  onMarkAllAsRead,
  onRefresh,
}: NotificationsPopoverProps) {
  const navigate = useNavigate();
  const isOnline = useOnlineStatus();

  if (!isOpen) return null;

  const handleItemClick = async (n: NotificationItem) => {
    if (!n.is_read) {
      try {
        await onMarkAsRead(n.id);
      } catch {
        // Continue navigation even if read marking fails
      }
    }
    if (n.link) {
      navigate(n.link);
      onClose();
    }
  };

  const handleMarkAll = async () => {
    try {
      await onMarkAllAsRead();
    } catch {
      // Handled in hook
    }
  };

  return (
    <div
      className="gf-notifications-popover"
      role="dialog"
      aria-label="Notifications"
      aria-modal="false"
    >
      {/* Header */}
      <div className="gf-notifications-popover__header">
        <div className="gf-notifications-popover__title-wrap">
          <h3 className="gf-notifications-popover__title">Notifications</h3>
          {unreadCount > 0 && (
            <span className="gf-notifications-popover__unread-badge">
              {unreadCount} New
            </span>
          )}
        </div>
        <div className="gf-notifications-popover__actions">
          {unreadCount > 0 && (
            <button
              type="button"
              className="gf-notifications-popover__mark-all-btn"
              onClick={handleMarkAll}
              disabled={!isOnline}
              aria-label="Mark all notifications as read"
            >
              Mark all read
            </button>
          )}
          <button
            type="button"
            className="gf-notifications-popover__close"
            onClick={onClose}
            aria-label="Close notifications"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="gf-notifications-popover__body">
        {/* Loading State */}
        {isLoading && (
          <div className="gf-notifications-loading">
            <LoadingSpinner size="md" label="Loading notifications..." />
          </div>
        )}

        {/* Error State */}
        {!isLoading && error && (
          <div className="gf-notifications-error">
            <InlineErrorState
              error={error}
              title="Unable to load notifications"
              onRetry={onRefresh}
              retryLabel="Retry"
            />
          </div>
        )}

        {/* Truthful Empty State */}
        {!isLoading && !error && notifications.length === 0 && (
          <EmptyState
            compact
            title="You're all caught up"
            description="No notifications right now. System alerts, mentor notes, and Blueprint updates will appear here."
            icon={
              <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" strokeWidth="1.5" fill="none">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            }
          />
        )}

        {/* Notifications List */}
        {!isLoading && !error && notifications.length > 0 && (
          <ul className="gf-notifications-list" role="list" aria-label="Notifications list">
            {notifications.map((n) => (
              <li key={n.id}>
                <button
                  type="button"
                  className={`gf-notification-item ${!n.is_read ? 'gf-notification-item--unread' : ''}`}
                  onClick={() => handleItemClick(n)}
                  aria-label={`${n.title}: ${n.message}${!n.is_read ? ' (Unread)' : ''}`}
                >
                  {!n.is_read && <span className="gf-notification-item__dot" aria-hidden="true" />}
                  <div className="gf-notification-item__content">
                    <div className="gf-notification-item__header">
                      <h4 className="gf-notification-item__title">{n.title}</h4>
                      <span className="gf-notification-item__time">
                        {formatRelativeTime(n.created_at)}
                      </span>
                    </div>
                    <p className="gf-notification-item__message">{n.message}</p>
                    <div className="gf-notification-item__footer">
                      <span className="gf-notification-item__type">{n.category}</span>
                      {n.actor_role && (
                        <span className="gf-notification-item__type">{n.actor_role}</span>
                      )}
                    </div>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
