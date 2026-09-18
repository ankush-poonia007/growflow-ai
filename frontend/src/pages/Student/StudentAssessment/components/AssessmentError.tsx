import { Button } from '@/components/ui';

interface AssessmentErrorProps {
  projectId: string;
  error: string;
  onRetry: () => void;
}

export function AssessmentError({ projectId, error, onRetry }: AssessmentErrorProps) {
  return (
    <div className="gf-assessment" role="alert" aria-live="assertive">
      <div
        style={{
          backgroundColor: 'var(--gf-surface, #ffffff)',
          border: '1px solid var(--gf-border, #e5e5e0)',
          borderRadius: '12px',
          padding: '2.5rem 2rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          gap: '1.25rem',
          maxWidth: '640px',
          margin: '2rem auto',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            backgroundColor: '#fee2e2',
            color: '#b91c1c',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          aria-hidden="true"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
          <h2
            style={{
              fontSize: '1.25rem',
              fontWeight: 700,
              color: 'var(--gf-text-primary, #1c1c1a)',
              margin: 0,
            }}
          >
            Unable to Load Assessment
          </h2>
          <p
            style={{
              fontSize: '0.875rem',
              color: 'var(--gf-text-secondary, #5a5a57)',
              maxWidth: '480px',
              margin: 0,
            }}
          >
            {error || 'An unexpected error occurred while communicating with the assessment service.'}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
          <Button variant="primary" size="md" onClick={onRetry} id="assessment-error-retry-btn">
            Try Again
          </Button>
          <Button
            as="link"
            to={`/student/projects/${projectId}/profile`}
            variant="secondary"
            size="md"
            id="assessment-error-back-btn"
          >
            Return to Project Profile
          </Button>
        </div>
      </div>
    </div>
  );
}
