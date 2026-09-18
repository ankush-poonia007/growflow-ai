import { Button } from '@/components/ui/Button';
import { ApiClientError } from '@/lib/api/errors';
import './SystemStates.css';

export interface NetworkErrorStateProps {
  error?: Error | ApiClientError | null;
  onRetry?: () => void;
  isOffline?: boolean;
  title?: string;
  message?: string;
  className?: string;
}

/**
 * SYS06 — Network / API Failure System State Component.
 *
 * Distinguishes:
 * - Offline / client network disconnection (navigator.onLine === false or status === 0)
 * - Timeout / unreachable gateway requests
 * - Server / API failure (5xx HTTP status codes)
 * - Generic request failure
 *
 * Provides safe retry capability when supported by the calling workflow.
 */
export function NetworkErrorState({
  error,
  onRetry,
  isOffline: propIsOffline,
  title: propTitle,
  message: propMessage,
  className = '',
}: NetworkErrorStateProps) {
  // Check if browser is offline or error indicates connection drop
  const isBrowserOffline =
    typeof navigator !== 'undefined' && typeof navigator.onLine === 'boolean'
      ? !navigator.onLine
      : false;

  const isNetworkDrop =
    propIsOffline ||
    isBrowserOffline ||
    (error instanceof ApiClientError && error.isNetworkError);

  const isTimeout =
    (error instanceof ApiClientError && error.code === 'TIMEOUT') ||
    Boolean(error?.message?.toLowerCase().includes('timeout'));

  const isServerFailure =
    error instanceof ApiClientError && error.isServerError;

  // Determine presentation details
  let badgeLabel = 'Connection Issue';
  let badgeVariant = 'warning';
  let title = propTitle || 'Unable to Communicate with Server';
  let description =
    propMessage ||
    'GrowFlow encountered a communication issue while reaching the platform service.';

  if (isNetworkDrop) {
    badgeLabel = 'Network Offline';
    badgeVariant = 'warning';
    title = propTitle || 'Network Connection Unavailable';
    description =
      propMessage ||
      'GrowFlow is unable to establish an internet connection. Please verify your network connection and try again.';
  } else if (isTimeout) {
    badgeLabel = 'Gateway Timeout';
    badgeVariant = 'warning';
    title = propTitle || 'Request Timed Out';
    description =
      propMessage ||
      'The service took longer than expected to respond. The network may be experiencing latency.';
  } else if (isServerFailure) {
    const status = error instanceof ApiClientError ? error.status : 500;
    badgeLabel = `Service Notice (${status})`;
    badgeVariant = 'danger';
    title = propTitle || 'Service Temporarily Unavailable';
    description =
      propMessage ||
      'The backend service is temporarily experiencing an issue. Your workspace data remains safe.';
  }

  return (
    <div
      className={`gf-system-card ${className}`.trim()}
      role="alert"
      aria-live="polite"
    >
      <span className={`gf-system-badge gf-system-badge--${badgeVariant}`}>
        {badgeLabel}
      </span>

      <h2 className="gf-system-title">{title}</h2>
      <p className="gf-system-desc">{description}</p>

      {onRetry && (
        <div className="gf-system-actions">
          <Button variant="primary" onClick={onRetry}>
            Try Again
          </Button>
        </div>
      )}
    </div>
  );
}
