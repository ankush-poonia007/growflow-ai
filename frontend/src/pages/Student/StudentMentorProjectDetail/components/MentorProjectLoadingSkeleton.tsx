import { Skeleton } from '@/components/ui/Skeleton';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';

export function MentorProjectLoadingSkeleton() {
  return (
    <div className="gf-detail-skeleton" aria-label="Loading mentor project details..." aria-busy="true">
      {/* Header Skeleton */}
      <div className="gf-detail-skeleton__header">
        <Skeleton width="180px" height="20px" />
        <div className="gf-detail-skeleton__badges">
          <Skeleton width="110px" height="24px" style={{ borderRadius: 'var(--gf-radius-full)' }} />
          <Skeleton width="90px" height="24px" style={{ borderRadius: 'var(--gf-radius-full)' }} />
          <Skeleton width="70px" height="24px" style={{ borderRadius: 'var(--gf-radius-full)' }} />
        </div>
        <Skeleton width="60%" height="36px" />
        <Skeleton width="40%" height="18px" />
      </div>

      {/* Main Content & Sidebar Grid */}
      <div className="gf-detail-layout">
        {/* Main Column */}
        <div className="gf-detail-layout__main">
          {/* Overview Skeleton */}
          <Card variant="bordered" className="gf-detail-section">
            <CardHeader className="gf-detail-section__header">
              <Skeleton width="220px" height="24px" />
            </CardHeader>
            <CardContent className="gf-detail-section__content">
              <div className="gf-detail-skeleton__block">
                <Skeleton width="120px" height="16px" />
                <Skeleton width="100%" height="48px" />
              </div>
              <div className="gf-detail-skeleton__block">
                <Skeleton width="160px" height="16px" />
                <Skeleton width="100%" height="48px" />
              </div>
              <div className="gf-detail-skeleton__block">
                <Skeleton width="140px" height="16px" />
                <Skeleton width="100%" height="72px" />
              </div>
            </CardContent>
          </Card>

          {/* Technology Skeleton */}
          <Card variant="bordered" className="gf-detail-section">
            <CardHeader className="gf-detail-section__header">
              <Skeleton width="180px" height="24px" />
            </CardHeader>
            <CardContent className="gf-detail-section__content">
              <div className="gf-detail-skeleton__chips">
                <Skeleton width="100px" height="32px" style={{ borderRadius: 'var(--gf-radius-sm)' }} />
                <Skeleton width="120px" height="32px" style={{ borderRadius: 'var(--gf-radius-sm)' }} />
                <Skeleton width="90px" height="32px" style={{ borderRadius: 'var(--gf-radius-sm)' }} />
                <Skeleton width="110px" height="32px" style={{ borderRadius: 'var(--gf-radius-sm)' }} />
              </div>
            </CardContent>
          </Card>

          {/* Constraints & Assumptions Skeleton */}
          <div className="gf-detail-dual-grid">
            <Card variant="bordered" className="gf-detail-section">
              <CardHeader className="gf-detail-section__header">
                <Skeleton width="150px" height="20px" />
              </CardHeader>
              <CardContent className="gf-detail-section__content">
                <Skeleton width="100%" height="40px" />
              </CardContent>
            </Card>
            <Card variant="bordered" className="gf-detail-section">
              <CardHeader className="gf-detail-section__header">
                <Skeleton width="180px" height="20px" />
              </CardHeader>
              <CardContent className="gf-detail-section__content">
                <Skeleton width="100%" height="40px" />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Sidebar Column */}
        <div className="gf-detail-layout__sidebar">
          {/* Selection Panel Skeleton */}
          <Card variant="bordered" className="gf-detail-selection-card">
            <CardHeader className="gf-detail-selection-card__header">
              <Skeleton width="40px" height="40px" style={{ borderRadius: 'var(--gf-radius-md)' }} />
              <Skeleton width="200px" height="24px" />
            </CardHeader>
            <CardContent className="gf-detail-selection-card__content">
              <Skeleton width="100%" height="40px" />
              <Skeleton width="100%" height="44px" style={{ borderRadius: 'var(--gf-radius-md)' }} />
            </CardContent>
          </Card>

          {/* Metadata Skeleton */}
          <Card variant="bordered" className="gf-detail-sidebar-card">
            <CardHeader className="gf-detail-sidebar-card__header">
              <Skeleton width="140px" height="20px" />
            </CardHeader>
            <CardContent className="gf-detail-sidebar-card__content">
              <div className="gf-detail-skeleton__meta">
                <Skeleton width="100%" height="24px" />
                <Skeleton width="100%" height="24px" />
                <Skeleton width="100%" height="24px" />
                <Skeleton width="100%" height="24px" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
