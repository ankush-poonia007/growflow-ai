import { Link } from 'react-router';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ApiClientError } from '@/lib/api/errors';

interface MentorProjectSelectionPanelProps {
  onSelect: () => void;
  isSelecting: boolean;
  selectionError: Error | null;
  onClearError?: () => void;
}

export function MentorProjectSelectionPanel({
  onSelect,
  isSelecting,
  selectionError,
  onClearError,
}: MentorProjectSelectionPanelProps) {
  const isDuplicate =
    selectionError instanceof ApiClientError &&
    (selectionError.status === 409 || selectionError.code === 'PROJECT_ALREADY_SELECTED');

  return (
    <Card as="section" className="gf-detail-selection-card" variant="bordered" aria-labelledby="sidebar-selection-title">
      <CardHeader className="gf-detail-selection-card__header">
        <div className="gf-detail-selection-card__icon-wrap" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="22"
            height="22"
          >
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
        </div>
        <CardTitle as="h2" id="sidebar-selection-title" className="gf-detail-selection-card__title">
          Ready to take on this project?
        </CardTitle>
      </CardHeader>

      <CardContent className="gf-detail-selection-card__content">
        <p className="gf-detail-selection-card__copy">
          Selecting this project creates your Student Project from the currently published Mentor definition.
        </p>

        {/* 409 Duplicate Selection State */}
        {isDuplicate && (
          <div className="gf-selection-duplicate-banner" role="alert" aria-live="polite">
            <div className="gf-selection-duplicate-banner__header">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                width="18"
                height="18"
                className="gf-selection-duplicate-banner__icon"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <h3 className="gf-selection-duplicate-banner__title">
                You've already selected this Mentor Project
              </h3>
            </div>
            <p className="gf-selection-duplicate-banner__message">
              An active student project instance for this definition already exists in your workspace.
            </p>
            <div className="gf-selection-duplicate-banner__actions">
              <Link to="/student/projects" className="gf-btn gf-btn--primary gf-btn--sm">
                View in My Projects
              </Link>
              <Link to="/student/projects/mentor-catalog" className="gf-btn gf-btn--secondary gf-btn--sm">
                Browse Mentor Catalog
              </Link>
            </div>
          </div>
        )}

        {/* Generic Selection Error State */}
        {selectionError && !isDuplicate && (
          <div className="gf-selection-error-banner" role="alert" aria-live="assertive">
            <p className="gf-selection-error-banner__message">
              {selectionError.message || 'Unable to select project. Please try again.'}
            </p>
            {onClearError && (
              <button
                type="button"
                className="gf-selection-error-banner__dismiss"
                onClick={onClearError}
                aria-label="Dismiss error"
              >
                &times;
              </button>
            )}
          </div>
        )}

        {/* Primary Selection Action Button */}
        {!isDuplicate && (
          <Button
            type="button"
            variant="primary"
            className="gf-detail-selection-card__cta"
            onClick={onSelect}
            disabled={isSelecting}
            aria-busy={isSelecting}
            aria-live="polite"
          >
            {isSelecting ? (
              <span className="gf-btn__loading-content">
                <span className="gf-btn__spinner" aria-hidden="true" />
                <span>Creating Project...</span>
              </span>
            ) : (
              <span>Select Project</span>
            )}
          </Button>
        )}

        <div className="gf-detail-selection-card__footer-note">
          <span>Official mentor blueprint • Phase: IDEA • Initial progress: 0%</span>
        </div>
      </CardContent>
    </Card>
  );
}
