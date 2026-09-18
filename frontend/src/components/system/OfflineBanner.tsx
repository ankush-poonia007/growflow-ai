import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { cn } from '@/utils/cn';
import './OfflineBanner.css';

export interface OfflineBannerProps {
  className?: string;
  message?: string;
}

/**
 * Canonical GrowFlow OfflineBanner component.
 *
 * Renders an accessible, calm notification bar when the browser loses network connection.
 * Disappears automatically when network connectivity is re-established.
 */
export function OfflineBanner({ className, message }: OfflineBannerProps) {
  const isOnline = useOnlineStatus();

  if (isOnline) {
    return null;
  }

  return (
    <aside
      role="status"
      aria-live="polite"
      aria-label="Offline status banner"
      className={cn('gf-offline-banner', className)}
    >
      <div className="gf-offline-banner__container">
        <div className="gf-offline-banner__icon" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="1" y1="1" x2="23" y2="23" />
            <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55" />
            <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39" />
            <path d="M10.71 5.05A16 16 0 0 1 22.58 9" />
            <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88" />
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
            <line x1="12" y1="20" x2="12.01" y2="20" />
          </svg>
        </div>
        <div className="gf-offline-banner__text">
          <strong className="gf-offline-banner__title">Connection Lost</strong>
          <span className="gf-offline-banner__desc">
            {message || 'You are currently offline. Operations and syncing are paused until connectivity returns.'}
          </span>
        </div>
      </div>
    </aside>
  );
}
