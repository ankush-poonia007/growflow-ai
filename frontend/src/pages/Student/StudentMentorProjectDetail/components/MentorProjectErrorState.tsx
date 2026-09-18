import { Link } from 'react-router';
import { ApiClientError } from '@/lib/api/errors';
import { Button } from '@/components/ui/Button';

interface MentorProjectErrorStateProps {
  error: Error | null;
  onRetry: () => void;
}

export function MentorProjectErrorState({ error, onRetry }: MentorProjectErrorStateProps) {
  const isNotFound =
    !error ||
    (error instanceof ApiClientError
      ? error.status === 404 || error.code === 'PROJECT_DEFINITION_NOT_FOUND'
      : error?.message?.toLowerCase().includes('not found'));

  const isForbidden =
    error instanceof ApiClientError ? error.status === 403 || error.code.startsWith('AUTH_FORBIDDEN') : false;

  // 404 Calm Unavailable State (does not leak draft/archived/internal state)
  if (isNotFound) {
    return (
      <div className="gf-detail-error" role="region" aria-label="Project unavailable">
        <div className="gf-detail-error__card">
          <div className="gf-detail-error__icon-wrap" aria-hidden="true">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="28"
              height="28"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <h2 className="gf-detail-error__title">Mentor Project Not Available</h2>
          <p className="gf-detail-error__message">
            This mentor project is not currently available for discovery or selection.
          </p>
          <div className="gf-detail-error__actions">
            <Link to="/student/projects/mentor-catalog" className="gf-btn gf-btn--primary">
              Back to Mentor Projects
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 403 Access Restricted State
  if (isForbidden) {
    return (
      <div className="gf-detail-error" role="region" aria-label="Access restricted">
        <div className="gf-detail-error__card">
          <div className="gf-detail-error__icon-wrap gf-detail-error__icon-wrap--warning" aria-hidden="true">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="28"
              height="28"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
          <h2 className="gf-detail-error__title">Access Restricted</h2>
          <p className="gf-detail-error__message">
            You do not have permission to view this mentor project definition.
          </p>
          <div className="gf-detail-error__actions">
            <Link to="/student/projects/mentor-catalog" className="gf-btn gf-btn--primary">
              Back to Mentor Projects
            </Link>
            <Link to="/student/dashboard" className="gf-btn gf-btn--secondary">
              Go to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Generic / Network / 5xx Server Error State
  const errorMessage =
    error instanceof ApiClientError && error.isNetworkError
      ? 'Unable to connect to GrowFlow services. Please check your internet connection.'
      : error?.message || 'An unexpected error occurred while loading this mentor project.';

  return (
    <div className="gf-detail-error" role="alert" aria-live="assertive">
      <div className="gf-detail-error__card">
        <div className="gf-detail-error__icon-wrap gf-detail-error__icon-wrap--error" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="28"
            height="28"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <h2 className="gf-detail-error__title">Unable to Load Project Definition</h2>
        <p className="gf-detail-error__message">{errorMessage}</p>
        <div className="gf-detail-error__actions">
          <Button type="button" variant="primary" onClick={onRetry}>
            Retry Loading
          </Button>
          <Link to="/student/projects/mentor-catalog" className="gf-btn gf-btn--secondary">
            Back to Mentor Projects
          </Link>
        </div>
      </div>
    </div>
  );
}
