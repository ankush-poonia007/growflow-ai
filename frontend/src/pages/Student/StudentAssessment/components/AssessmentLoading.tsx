import { Skeleton } from '@/components/ui';

export function AssessmentLoading() {
  return (
    <div
      className="gf-assessment"
      role="status"
      aria-live="polite"
      aria-label="Loading technical assessment..."
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <Skeleton height="24px" width="160px" />
        <Skeleton height="40px" width="380px" />
      </div>

      <div
        style={{
          backgroundColor: 'var(--gf-surface, #ffffff)',
          border: '1px solid var(--gf-border, #e5e5e0)',
          borderRadius: '12px',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem',
        }}
      >
        <Skeleton height="20px" width="220px" />
        <Skeleton height="32px" width="80%" />
        <Skeleton height="18px" width="60%" />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
          <Skeleton height="56px" width="100%" />
          <Skeleton height="56px" width="100%" />
          <Skeleton height="56px" width="100%" />
          <Skeleton height="56px" width="100%" />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem' }}>
          <Skeleton height="42px" width="120px" />
          <Skeleton height="42px" width="140px" />
        </div>
      </div>
    </div>
  );
}
