import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';

interface ProjectProfileErrorProps {
  error: Error | string | null;
  onRetry?: () => void;
}

export function ProjectProfileError({ error, onRetry }: ProjectProfileErrorProps) {
  const errorMessage = typeof error === 'string' ? error : error?.message || '';
  const isNotFound =
    errorMessage.toLowerCase().includes('not found') ||
    errorMessage.includes('404') ||
    errorMessage.includes('PROJECT_NOT_FOUND');

  const isForbidden =
    errorMessage.toLowerCase().includes('denied') ||
    errorMessage.toLowerCase().includes('forbidden') ||
    errorMessage.includes('403') ||
    errorMessage.includes('AUTH_FORBIDDEN_RESOURCE');

  const isMalformed =
    errorMessage.toLowerCase().includes('validation') ||
    errorMessage.toLowerCase().includes('uuid') ||
    errorMessage.includes('422');

  if (isNotFound) {
    return (
      <div className="gf-profile-error-container" role="alert">
        <EmptyState
          title="Project Not Found"
          description="The requested project could not be found. It may have been removed or the URL may be incorrect."
          icon={
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          }
          action={
            <Button as="link" to="/student/projects" variant="primary">
              Return to My Projects
            </Button>
          }
        />
      </div>
    );
  }

  if (isForbidden) {
    return (
      <div className="gf-profile-error-container" role="alert">
        <EmptyState
          title="Access Restricted"
          description="You do not have permission to view or manage this project instance. Project profiles are strictly isolated to their student owner."
          icon={
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          }
          action={
            <Button as="link" to="/student/projects" variant="primary">
              Return to My Projects
            </Button>
          }
        />
      </div>
    );
  }

  if (isMalformed) {
    return (
      <div className="gf-profile-error-container" role="alert">
        <EmptyState
          title="Invalid Project Identifier"
          description="The project identifier in the URL is invalid. Please navigate from your projects collection."
          icon={
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
          }
          action={
            <Button as="link" to="/student/projects" variant="primary">
              Return to My Projects
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div className="gf-profile-error-container" role="alert">
      <EmptyState
        title="Unable to Load Project Profile"
        description={
          errorMessage ||
          'A connection issue occurred while retrieving your project profile. Please try again.'
        }
        icon={
          <svg
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
            <line x1="12" y1="2" x2="12" y2="12" />
          </svg>
        }
        action={
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
            {onRetry && (
              <Button as="button" variant="primary" onClick={onRetry}>
                Retry Loading
              </Button>
            )}
            <Button as="link" to="/student/projects" variant="secondary">
              Return to Projects
            </Button>
          </div>
        }
      />
    </div>
  );
}
