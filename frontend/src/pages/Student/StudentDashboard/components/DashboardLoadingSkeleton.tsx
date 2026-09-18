import { Skeleton } from '@/components/ui/Skeleton';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';

export function DashboardLoadingSkeleton() {
  return (
    <div className="gf-dashboard__loading-container" aria-label="Loading workspace..." role="status">
      {/* Welcome Skeleton */}
      <div className="gf-dashboard__welcome-skeleton">
        <Skeleton variant="text" width={120} height={14} style={{ marginBottom: '12px' }} />
        <Skeleton variant="text" width={320} height={32} style={{ marginBottom: '12px' }} />
        <Skeleton variant="text" width={480} height={16} />
      </div>

      {/* Primary Current Work Skeleton */}
      <Card variant="bordered" className="gf-dashboard__current-work-skeleton">
        <CardHeader>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <Skeleton variant="text" width={140} height={14} style={{ marginBottom: '8px' }} />
              <Skeleton variant="text" width={280} height={26} />
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <Skeleton variant="rect" width={70} height={24} style={{ borderRadius: '9999px' }} />
              <Skeleton variant="rect" width={70} height={24} style={{ borderRadius: '9999px' }} />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <Skeleton variant="text" width={120} height={14} />
              <Skeleton variant="text" width={40} height={14} />
            </div>
            <Skeleton variant="rect" width="100%" height={8} style={{ borderRadius: '4px' }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <Skeleton variant="text" width={90} height={12} style={{ marginBottom: '6px' }} />
              <Skeleton variant="text" width={140} height={16} />
            </div>
            <div>
              <Skeleton variant="text" width={90} height={12} style={{ marginBottom: '6px' }} />
              <Skeleton variant="text" width={120} height={16} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Two Column Grid Skeleton */}
      <div className="gf-dashboard__split-grid">
        <Card variant="bordered">
          <CardHeader>
            <Skeleton variant="text" width={120} height={14} style={{ marginBottom: '8px' }} />
            <Skeleton variant="text" width={200} height={20} />
          </CardHeader>
          <CardContent>
            <Skeleton variant="rect" width="100%" height={100} style={{ borderRadius: '8px' }} />
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardHeader>
            <Skeleton variant="text" width={120} height={14} style={{ marginBottom: '8px' }} />
            <Skeleton variant="text" width={220} height={20} />
          </CardHeader>
          <CardContent>
            <Skeleton variant="text" width="100%" height={14} style={{ marginBottom: '8px' }} />
            <Skeleton variant="text" width="80%" height={14} style={{ marginBottom: '16px' }} />
            <Skeleton variant="rect" width="100%" height={64} style={{ borderRadius: '6px' }} />
          </CardContent>
        </Card>
      </div>

      {/* Recent Changes Skeleton */}
      <Card variant="bordered">
        <CardHeader>
          <Skeleton variant="text" width={100} height={14} style={{ marginBottom: '8px' }} />
          <Skeleton variant="text" width={180} height={20} />
        </CardHeader>
        <CardContent>
          <Skeleton variant="rect" width="100%" height={48} style={{ borderRadius: '6px' }} />
        </CardContent>
      </Card>
    </div>
  );
}
