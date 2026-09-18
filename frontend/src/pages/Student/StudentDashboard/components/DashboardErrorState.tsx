import { Button } from '@/components/ui/Button';

interface DashboardErrorStateProps {
  message?: string;
  onRetry: () => void;
}

export function DashboardErrorState({ message, onRetry }: DashboardErrorStateProps) {
  return (
    <div className="gf-dashboard__error-container" role="alert" aria-live="assertive">
      <div className="gf-dashboard__error-card">
        <div className="gf-dashboard__error-icon-wrapper" aria-hidden="true">
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>

        <h2 className="gf-dashboard__error-title">We couldn't load your workspace</h2>
        <p className="gf-dashboard__error-message">
          {message || 'An unexpected error occurred while communicating with the server. Please try again.'}
        </p>

        <div className="gf-dashboard__error-actions">
          <Button as="button" variant="primary" onClick={onRetry}>
            Try Again
          </Button>
        </div>
      </div>
    </div>
  );
}
