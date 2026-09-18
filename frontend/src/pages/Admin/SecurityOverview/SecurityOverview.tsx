import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminSecurityOverview } from '@/lib/api/client';
import type { AdminSecurityOverview } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import './SecurityOverview.css';

/**
 * AD24 — Admin Security & Audit Overview
 *
 * Provides authoritative user account security posture, role distribution,
 * outbox integrity metrics, and recent canonical domain events.
 */
export function SecurityOverview() {
  const [data, setData] = useState<AdminSecurityOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSecurity = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminSecurityOverview();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve security overview.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSecurity();
  }, []);

  return (
    <div className="gf-sec-overview">
      <PageHeader
        eyebrow="SECURITY & AUDIT"
        title="Security & Audit Governance"
        description="Authoritative platform user posture, account security states, and canonical audit activity."
        actions={
          <div className="gf-sec-overview__actions">
            <Button as="link" to="/admin/security/investigations" variant="secondary" size="sm">
              Governed Inspection
            </Button>
            <Button as="link" to="/admin/security/audit" variant="primary" size="sm">
              View Full Audit Log
            </Button>
          </div>
        }
      />

      {error && (
        <div className="gf-sec-overview__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchSecurity}>
            Retry
          </Button>
        </div>
      )}

      {/* Primary User Posture StatTiles */}
      <section className="gf-sec-overview__stats" aria-label="Security Metrics">
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
              label="Total User Accounts"
              value={data?.user_posture?.total_users ?? 0}
              subtext={`${data?.user_posture?.active_users ?? 0} active in system`}
            />
            <StatTile
              label="Suspended Accounts"
              value={data?.user_posture?.suspended_users ?? 0}
              subtext={
                (data?.user_posture?.suspended_users ?? 0) > 0
                  ? 'Access restricted by administrator'
                  : 'Zero suspended accounts'
              }
            />
            <StatTile
              label="Total Audit Events"
              value={data?.audit_summary?.total_events ?? 0}
              subtext="Immutable records in domain_events"
            />
            <StatTile
              label="Delivery Failures"
              value={data?.audit_summary?.outbox_delivery_failures ?? 0}
              subtext={
                (data?.audit_summary?.outbox_delivery_failures ?? 0) === 0
                  ? 'All transactional events delivered'
                  : 'Requires administrator attention'
              }
            />
          </>
        )}
      </section>

      {/* Role Distribution Grid */}
      <div className="gf-sec-overview__grid">
        <Card className="gf-sec-overview__card">
          <CardHeader>
            <CardTitle>Role Governance Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="gf-sec-overview__skeleton-wrap">
                <Skeleton height="36px" />
                <Skeleton height="36px" />
                <Skeleton height="36px" />
              </div>
            ) : (
              <div className="gf-sec-overview__role-list">
                <div className="gf-sec-overview__role-item">
                  <div className="gf-sec-overview__role-info">
                    <span className="gf-sec-overview__role-name">Administrators</span>
                    <span className="gf-sec-overview__role-desc">Full governance and platform oversight</span>
                  </div>
                  <Badge variant="accent">{data?.user_posture?.admin_count ?? 0}</Badge>
                </div>
                <div className="gf-sec-overview__role-item">
                  <div className="gf-sec-overview__role-info">
                    <span className="gf-sec-overview__role-name">Mentors</span>
                    <span className="gf-sec-overview__role-desc">Supervise cohorts and project definitions</span>
                  </div>
                  <Badge variant="neutral">{data?.user_posture?.mentor_count ?? 0}</Badge>
                </div>
                <div className="gf-sec-overview__role-item">
                  <div className="gf-sec-overview__role-info">
                    <span className="gf-sec-overview__role-name">Students</span>
                    <span className="gf-sec-overview__role-desc">Active learners executing project blueprints</span>
                  </div>
                  <Badge variant="neutral">{data?.user_posture?.student_count ?? 0}</Badge>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Truthful Security Telemetry Card */}
        <Card className="gf-sec-overview__card">
          <CardHeader>
            <CardTitle>Security Architecture Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-sec-overview__telemetry">
              <div className="gf-sec-overview__telemetry-row">
                <span className="gf-sec-overview__telemetry-label">Authentication Engine</span>
                <Badge variant="success">Supabase JWT HS256</Badge>
              </div>
              <div className="gf-sec-overview__telemetry-row">
                <span className="gf-sec-overview__telemetry-label">Access Boundary</span>
                <Badge variant="success">RequireAdmin Guard</Badge>
              </div>
              <div className="gf-sec-overview__telemetry-row">
                <span className="gf-sec-overview__telemetry-label">Data Isolation</span>
                <Badge variant="success">Row-Level Security (RLS)</Badge>
              </div>
              <div className="gf-sec-overview__telemetry-row">
                <span className="gf-sec-overview__telemetry-label">Correlation Tracing</span>
                <Badge variant="success">X-Correlation-ID Active</Badge>
              </div>
              <p className="gf-sec-overview__disclaimer">
                Note: Client authentication and credential handling are delegated to Supabase Auth.
                Network intrusion telemetry, IP address lookups, and suspicious login scoring are not stored in
                the GrowFlow database.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity Table */}
      <Card className="gf-sec-overview__card gf-sec-overview__card--full">
        <CardHeader className="gf-sec-overview__recent-header">
          <CardTitle>Recent Governance-Relevant Events</CardTitle>
          <Link to="/admin/security/audit" className="gf-sec-overview__link-more">
            View All Events in Audit Log →
          </Link>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="gf-sec-overview__skeleton-wrap">
              <Skeleton height="48px" />
              <Skeleton height="48px" />
              <Skeleton height="48px" />
            </div>
          ) : !data?.recent_security_relevant_events || data.recent_security_relevant_events.length === 0 ? (
            <p className="gf-sec-overview__empty-text">No recent domain events recorded.</p>
          ) : (
            <div className="gf-sec-overview__table-responsive">
              <table className="gf-sec-overview__table">
                <thead>
                  <tr>
                    <th>Event</th>
                    <th>Actor Role</th>
                    <th>Resource</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_security_relevant_events.map((evt) => (
                    <tr key={evt.id}>
                      <td>
                        <span className="gf-sec-overview__event-title">{evt.title}</span>
                        <span className="gf-sec-overview__event-type">{evt.event_type}</span>
                      </td>
                      <td>
                        <Badge variant="neutral">{evt.actor_role}</Badge>
                      </td>
                      <td>
                        <span className="gf-sec-overview__resource">
                          {evt.resource_type}: {evt.resource_id.slice(0, 8)}...
                        </span>
                      </td>
                      <td>
                        <Badge variant={evt.status === 'PUBLISHED' ? 'success' : 'warning'}>
                          {evt.status}
                        </Badge>
                      </td>
                      <td>{evt.occurred_at ? new Date(evt.occurred_at).toLocaleString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
