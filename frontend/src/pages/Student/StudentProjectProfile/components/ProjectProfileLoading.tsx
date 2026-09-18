import { Skeleton } from '@/components/ui/Skeleton';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';

export function ProjectProfileLoading() {
  return (
    <div className="gf-profile-loading" aria-label="Loading project profile..." role="status">
      {/* Breadcrumb & Header Skeleton */}
      <div className="gf-profile-loading__header">
        <Skeleton width="180px" height="18px" variant="text" />
        <div className="gf-profile-loading__title-row">
          <div>
            <Skeleton width="120px" height="20px" variant="rect" style={{ marginBottom: '8px' }} />
            <Skeleton width="340px" height="36px" variant="text" />
          </div>
          <Skeleton width="140px" height="40px" variant="rect" />
        </div>
        <div className="gf-profile-loading__badges-row">
          <Skeleton width="90px" height="24px" variant="rect" />
          <Skeleton width="80px" height="24px" variant="rect" />
          <Skeleton width="85px" height="24px" variant="rect" />
        </div>
      </div>

      {/* Identity Card Skeleton */}
      <Card variant="bordered" className="gf-profile-section">
        <CardHeader>
          <Skeleton width="220px" height="24px" variant="text" style={{ marginBottom: '6px' }} />
          <Skeleton width="380px" height="16px" variant="text" />
        </CardHeader>
        <CardContent>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <Skeleton width="100%" height="80px" variant="rect" />
            <Skeleton width="100%" height="80px" variant="rect" />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <Skeleton width="100%" height="70px" variant="rect" />
              <Skeleton width="100%" height="70px" variant="rect" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Provenance Card Skeleton */}
      <Card variant="bordered" className="gf-profile-section">
        <CardHeader>
          <Skeleton width="180px" height="24px" variant="text" style={{ marginBottom: '6px' }} />
          <Skeleton width="300px" height="16px" variant="text" />
        </CardHeader>
        <CardContent>
          <Skeleton width="100%" height="90px" variant="rect" />
        </CardContent>
      </Card>

      {/* System State Skeleton */}
      <Card variant="bordered" className="gf-profile-section">
        <CardHeader>
          <Skeleton width="240px" height="24px" variant="text" style={{ marginBottom: '6px' }} />
          <Skeleton width="420px" height="16px" variant="text" />
        </CardHeader>
        <CardContent>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
            <Skeleton width="100%" height="75px" variant="rect" />
            <Skeleton width="100%" height="75px" variant="rect" />
            <Skeleton width="100%" height="75px" variant="rect" />
            <Skeleton width="100%" height="75px" variant="rect" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
