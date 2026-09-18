import { Skeleton } from '@/components/ui/Skeleton';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';

export function ProjectsLoadingSkeleton() {
  return (
    <div className="gf-projects-skeleton" aria-label="Loading projects..." role="status">
      {/* Header Skeleton */}
      <div className="gf-projects-skeleton__header">
        <Skeleton variant="text" width={140} height={14} style={{ marginBottom: '8px' }} />
        <Skeleton variant="text" width={260} height={32} style={{ marginBottom: '8px' }} />
        <Skeleton variant="text" width={420} height={16} />
      </div>

      {/* Summary Skeleton */}
      <div className="gf-projects-skeleton__summary">
        <Skeleton variant="rect" width="100%" height={40} style={{ borderRadius: '6px' }} />
      </div>

      {/* Filter Bar Skeleton */}
      <div className="gf-projects-skeleton__filters">
        <Skeleton variant="rect" width="100%" height={44} style={{ borderRadius: '8px' }} />
      </div>

      {/* Cards Skeletons */}
      <div className="gf-projects-skeleton__list">
        {[1, 2, 3].map((idx) => (
          <Card key={idx} variant="bordered" className="gf-projects-skeleton__card">
            <CardHeader>
              <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                <div>
                  <Skeleton variant="text" width={160} height={12} style={{ marginBottom: '8px' }} />
                  <Skeleton variant="text" width={280} height={24} />
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Skeleton variant="rect" width={70} height={24} style={{ borderRadius: '9999px' }} />
                  <Skeleton variant="rect" width={70} height={24} style={{ borderRadius: '9999px' }} />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Skeleton variant="rect" width="100%" height={8} style={{ borderRadius: '4px', marginBottom: '16px' }} />
              <Skeleton variant="text" width="80%" height={14} style={{ marginBottom: '12px' }} />
              <div style={{ display: 'flex', gap: '24px' }}>
                <Skeleton variant="text" width={100} height={14} />
                <Skeleton variant="text" width={100} height={14} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
