import { type ReactNode } from 'react';
import { ApiClientError } from '@/lib/api/errors';
import { Button } from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import './InlineErrorState.css';

export interface InlineErrorStateProps {
  error: string | ApiClientError | Error | null | undefined;
  title?: string;
  onRetry?: () => void | Promise<void>;
  retryLabel?: string;
  action?: ReactNode;
  className?: string;
}

/**
 * Format a user-safe, truthful message from any error input.
 * Avoids exposing raw stack traces, API keys, or database errors.
 */
function resolveErrorMessage(error: string | ApiClientError | Error | null | undefined): string {
  if (!error) {
    return 'An unexpected issue occurred. Please try again.';
  }

  if (typeof error === 'string') {
    return error;
  }

  if (error instanceof ApiClientError) {
    if (error.isNetworkError) {
      return 'Unable to reach GrowFlow services. Please check your internet connection and try again.';
    }
    if (error.isRateLimited) {
      return 'Too many requests. Please pause a moment before retrying.';
    }
    if (error.isServerError) {
      return 'GrowFlow service encountered an unexpected problem. Please try again shortly.';
    }
    if (error.isUnauthorized) {
      return 'Your session has expired or requires authentication. Please sign in again.';
    }
    if (error.isForbidden) {
      return 'You do not have permission to access or modify this resource.';
    }
    if (error.isNotFound) {
      return 'The requested resource or workspace could not be found.';
    }
    // Return sanitized message if safe, fallback if empty
    return error.message || 'The requested operation could not be completed.';
  }

  if (error instanceof Error) {
    return error.message || 'An unexpected error occurred.';
  }

  return 'An unexpected issue occurred. Please try again.';
}

/**
 * Canonical GrowFlow InlineErrorState component.
 *
 * Displays a non-intrusive section alert banner adhering to Soft Intelligence tokens.
 * Features:
 * - Direct ApiClientError resolution without string-parsing hacks
 * - Optional scoped retry action (rendered only when onRetry is provided)
 * - Accessible alert semantics (role="alert")
 * - 390px mobile wrap and touch-friendly controls
 */
export function InlineErrorState({
  error,
  title,
  onRetry,
  retryLabel = 'Retry',
  action,
  className,
}: InlineErrorStateProps) {
  const message = resolveErrorMessage(error);

  return (
    <div
      role="alert"
      className={cn('gf-inline-error', className)}
    >
      <div className="gf-inline-error__icon-wrap" aria-hidden="true">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="gf-inline-error__icon"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>

      <div className="gf-inline-error__content">
        {title && <h4 className="gf-inline-error__title">{title}</h4>}
        <p className="gf-inline-error__message">{message}</p>
      </div>

      {(onRetry || action) && (
        <div className="gf-inline-error__actions">
          {onRetry && (
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => void onRetry()}
              className="gf-inline-error__retry-btn"
            >
              {retryLabel}
            </Button>
          )}
          {action}
        </div>
      )}
    </div>
  );
}
