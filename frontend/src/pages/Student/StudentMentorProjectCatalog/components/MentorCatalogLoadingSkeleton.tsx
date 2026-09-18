import { Skeleton } from '@/components/ui/Skeleton';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';

export function MentorCatalogLoadingSkeleton() {
  return (
    <div className="gf-mentor-skeleton" aria-label="Loading mentor project catalog..." role="status">
      {/* Header Skeleton */}
      <div className="gf-mentor-skeleton__header">
        <Skeleton variant="text" width={130} height={14} style={{ marginBottom: '8px' }} />
        <Skeleton variant="text" width={240} height={32} style={{ marginBottom: '8px' }} />
        <Skeleton variant="text" width={480} height={16} style={{ marginBottom: '16px' }} />
        <Skeleton variant="rect" width="100%" height={48} style={{ borderRadius: '8px' }} />
      </div>

      {/* Filter Bar Skeleton */}
      <div className="gf-mentor-skeleton__filters">
        <Skeleton variant="rect" width="100%" height={44} style={{ borderRadius: '8px' }} />
      </div>

      {/* Summary Bar Skeleton */}
      <div className="gf-mentor-skeleton__summary">
        <Skeleton variant="rect" width="100%" height={36} style={{ borderRadius: '6px' }} />
      </div>

      {/* Cards Skeletons */}
      <div className="gf-mentor-skeleton__grid">
        {[1, 2, 3, 4].map((idx) => (
          <Card key={idx} variant="bordered" className="gf-mentor-skeleton__card">
            <CardHeader>
              <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginBottom: '12px' }}>
                <Skeleton variant="rect" width={110} height={20} style={{ borderRadius: '9999px' }} />
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Skeleton variant="rect" width={75} height={20} style={{ borderRadius: '9999px' }} />
                  <Skeleton variant="rect" width={65} height={20} style={{ borderRadius: '9999px' }} />
                </div>
              </div>
              <Skeleton variant="text" width="75%" height={24} />
            </CardHeader>
            <CardContent>
              <Skeleton variant="text" width="100%" height={14} style={{ marginBottom: '8px' }} />
              <Skeleton variant="text" width="85%" height={14} style={{ marginBottom: '16px' }} />
              <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
                <Skeleton variant="rect" width={60} height={22} style={{ borderRadius: '4px' }} />
                <Skeleton variant="rect" width={70} height={22} style={{ borderRadius: '4px' }} />
                <Skeleton variant="rect" width={55} height={22} style={{ borderRadius: '4px' }} />
              </div>
              <Skeleton variant="rect" width="100%" height={28} style={{ borderRadius: '4px' }} />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
