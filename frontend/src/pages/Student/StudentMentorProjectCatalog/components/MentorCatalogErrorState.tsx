import { Button } from '@/components/ui/Button';

interface MentorCatalogErrorStateProps {
  error?: string | null;
  onRetry: () => void;
}

export function MentorCatalogErrorState({ error, onRetry }: MentorCatalogErrorStateProps) {
  // Determine user-facing calm message based on error text / status code hints
  const getErrorMessage = (err?: string | null) => {
    if (!err) return "We couldn't load mentor projects right now. Please try again.";
    const lower = err.toLowerCase();
    if (lower.includes('401') || lower.includes('unauthorized') || lower.includes('session')) {
      return 'Your session has expired. Please sign in again.';
    }
    if (lower.includes('403') || lower.includes('forbidden') || lower.includes('permission')) {
      return "You don't have permission to browse mentor projects.";
    }
    if (lower.includes('404') || lower.includes('not found')) {
      return 'Mentor projects are currently unavailable.';
    }
    if (lower.includes('429') || lower.includes('rate limit') || lower.includes('too many')) {
      return 'Too many requests. Please wait a moment and try again.';
    }
    if (lower.includes('network') || lower.includes('failed to fetch') || lower.includes('connection')) {
      return "We couldn't reach GrowFlow. Check your connection and try again.";
    }
    if (lower.includes('500') || lower.includes('502') || lower.includes('503') || lower.includes('server')) {
      return "We couldn't load mentor projects right now. Please try again.";
    }
    return err;
  };

  return (
    <div className="gf-mentor-error" role="alert" aria-live="assertive">
      <div className="gf-mentor-error__card">
        <div className="gf-mentor-error__icon-wrap" aria-hidden="true">
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

        <h2 className="gf-mentor-error__title">We couldn't load mentor projects</h2>
        <p className="gf-mentor-error__message">{getErrorMessage(error)}</p>

        <div className="gf-mentor-error__actions">
          <Button type="button" variant="primary" onClick={onRetry}>
            Try Again
          </Button>
        </div>
      </div>
    </div>
  );
}
