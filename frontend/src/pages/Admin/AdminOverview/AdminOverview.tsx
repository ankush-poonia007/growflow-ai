import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router';
import { getAdminOverview } from '@/lib/api/client';
import type { AdminOverviewResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './AdminOverview.css';

/**
 * AD01 — Admin Overview
 *
 * Central governance dashboard displaying platform-wide metrics derived
 * strictly from authoritative database state.
 */
export function AdminOverview() {
  const [data, setData] = useState<AdminOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminOverview();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load platform overview metrics.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  return (
    <div className="gf-admin-overview">
      <PageHeader
        eyebrow="PLATFORM GOVERNANCE"
        title="Platform Overview"
        description="Authoritative platform monitoring, user governance, and project lifecycle metrics."
        actions={
          <div className="gf-admin-overview__header-actions">
            <Button as="link" to="/admin/mentors" variant="secondary">
              View Mentors
            </Button>
            <Button as="link" to="/admin/students" variant="primary">
              View Students
            </Button>
          </div>
        }
      />

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadOverview} />
        </div>
      )}

      {/* Primary Metrics Grid */}
      <section className="gf-admin-overview__stats" aria-label="Platform Metrics">
        {loading ? (
          <>
            <Skeleton height="110px" />
            <Skeleton height="110px" />
            <Skeleton height="110px" />
            <Skeleton height="110px" />
          </>
        ) : (
          <>
            <StatTile
              label="Registered Mentors"
              value={data?.total_mentors ?? 0}
              subtext={`${data?.active_mentors ?? 0} active accounts`}
            />
            <StatTile
              label="Enrolled Students"
              value={data?.total_students ?? 0}
              subtext={`${data?.active_students ?? 0} active accounts`}
            />
            <StatTile
              label="Active Cohorts"
              value={data?.active_groups ?? 0}
              subtext={`${data?.total_groups ?? 0} total cohorts created`}
            />
            <StatTile
              label="Active Projects"
              value={data?.active_projects ?? 0}
              subtext={`${data?.total_projects ?? 0} total across platform`}
            />
          </>
        )}
      </section>

      {/* Secondary Project Lifecycle & Risk Overview */}
      <section className="gf-admin-overview__secondary" aria-label="Platform Lifecycle & Health">
        <div className="gf-admin-overview__grid">
          {/* Projects Health Card */}
          <Card className="gf-admin-overview__card">
            <CardHeader className="gf-admin-overview__card-header">
              <div className="gf-admin-overview__card-header-inner">
                <CardTitle className="gf-admin-overview__card-title">Project Lifecycle Health</CardTitle>
                <Badge variant={data?.at_risk_projects && data.at_risk_projects > 0 ? 'warning' : 'success'}>
                  {data?.at_risk_projects && data.at_risk_projects > 0
                    ? `${data.at_risk_projects} At Risk`
                    : 'Optimal Health'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="gf-admin-overview__skeleton-stack">
                  <Skeleton height="24px" />
                  <Skeleton height="24px" />
                  <Skeleton height="24px" />
                </div>
              ) : (
                <div className="gf-admin-overview__metric-list">
                  <div className="gf-admin-overview__metric-row">
                    <span className="gf-admin-overview__metric-label">In-Flight (Active)</span>
                    <span className="gf-admin-overview__metric-value">{data?.active_projects ?? 0}</span>
                  </div>
                  <div className="gf-admin-overview__metric-row">
                    <span className="gf-admin-overview__metric-label">Completed Successfully</span>
                    <span className="gf-admin-overview__metric-value gf-admin-overview__metric-value--success">
                      {data?.completed_projects ?? 0}
                    </span>
                  </div>
                  <div className="gf-admin-overview__metric-row">
                    <span className="gf-admin-overview__metric-label">At-Risk Projects</span>
                    <span
                      className={`gf-admin-overview__metric-value ${
                        data?.at_risk_projects && data.at_risk_projects > 0
                          ? 'gf-admin-overview__metric-value--danger'
                          : ''
                      }`}
                    >
                      {data?.at_risk_projects ?? 0}
                    </span>
                  </div>
                  <div className="gf-admin-overview__metric-row">
                    <span className="gf-admin-overview__metric-label">Total Historical Instances</span>
                    <span className="gf-admin-overview__metric-value">{data?.total_projects ?? 0}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Access / Operations Navigation Card */}
          <Card className="gf-admin-overview__card">
            <CardHeader className="gf-admin-overview__card-header">
              <CardTitle className="gf-admin-overview__card-title">People Governance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="gf-admin-overview__quick-links">
                <Link to="/admin/mentors" className="gf-admin-overview__quick-link">
                  <div className="gf-admin-overview__quick-link-icon gf-admin-overview__quick-link-icon--mentor">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
                      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                  </div>
                  <div className="gf-admin-overview__quick-link-content">
                    <span className="gf-admin-overview__quick-link-title">Mentor Directory (AD02)</span>
                    <span className="gf-admin-overview__quick-link-subtitle">
                      Inspect {data?.total_mentors ?? 0} mentors, organizations, and assigned cohorts
                    </span>
                  </div>
                  <svg className="gf-admin-overview__quick-link-chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M6 12l4-4-4-4" />
                  </svg>
                </Link>

                <Link to="/admin/students" className="gf-admin-overview__quick-link">
                  <div className="gf-admin-overview__quick-link-icon gf-admin-overview__quick-link-icon--student">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                  </div>
                  <div className="gf-admin-overview__quick-link-content">
                    <span className="gf-admin-overview__quick-link-title">Student Directory (AD04)</span>
                    <span className="gf-admin-overview__quick-link-subtitle">
                      Inspect {data?.total_students ?? 0} students, tracks, colleges, and active projects
                    </span>
                  </div>
                  <svg className="gf-admin-overview__quick-link-chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M6 12l4-4-4-4" />
                  </svg>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
