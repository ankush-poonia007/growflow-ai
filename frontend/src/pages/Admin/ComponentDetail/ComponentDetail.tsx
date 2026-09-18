import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminComponentDetail } from '@/lib/api/client';
import type { AdminSubsystemDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import './ComponentDetail.css';

/**
 * AD20 — Admin Component Detail
 *
 * Detailed diagnostic inspection for a specific subsystem, exposing safe
 * configuration flags, real-time diagnostic checks, and recent transactional failures.
 */
export function ComponentDetail() {
  const { component } = useParams<{ component: string }>();
  const [data, setData] = useState<AdminSubsystemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = async () => {
    if (!component) return;
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminComponentDetail(component);
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve component details.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [component]);

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'OPERATIONAL':
        return <Badge variant="success">Operational</Badge>;
      case 'CONFIGURED':
        return <Badge variant="neutral">Configured</Badge>;
      case 'DEGRADED':
        return <Badge variant="warning">Degraded</Badge>;
      case 'CRITICAL':
      case 'UNAVAILABLE':
        return <Badge variant="danger">Critical</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="gf-comp-detail">
      <div className="gf-comp-detail__breadcrumb">
        <Link to="/admin/system-health" className="gf-comp-detail__back-link">
          ← Back to System Health
        </Link>
      </div>

      {error ? (
        <div className="gf-comp-detail__alert" role="alert">
          <span>{error}</span>
          <Button as="link" to="/admin/system-health" variant="secondary" size="sm">
            Return to Health Overview
          </Button>
        </div>
      ) : loading ? (
        <div className="gf-comp-detail__skeleton">
          <Skeleton height="80px" />
          <Skeleton height="200px" />
          <Skeleton height="200px" />
        </div>
      ) : data ? (
        <>
          <PageHeader
            eyebrow="SUBSYSTEM GOVERNANCE"
            title={data.name}
            description={`Component: ${data.id} • Category: ${data.type} • Checked at: ${new Date(data.checked_at).toLocaleTimeString()}`}
            actions={
              <div className="gf-comp-detail__header-actions">
                {getStatusBadge(data.status)}
                <Button variant="secondary" size="sm" onClick={fetchDetail}>
                  Refresh
                </Button>
              </div>
            }
          />

          <div className="gf-comp-detail__grid">
            {/* Configuration Signals Card */}
            <Card className="gf-comp-detail__card">
              <CardHeader>
                <CardTitle>Safe Configuration Signals</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="gf-comp-detail__dl">
                  {Object.entries(data.configuration).map(([key, val]) => (
                    <div key={key} className="gf-comp-detail__dl-row">
                      <dt className="gf-comp-detail__dt">{key.replace(/_/g, ' ')}</dt>
                      <dd className="gf-comp-detail__dd">
                        {typeof val === 'boolean' ? (
                          val ? (
                            <Badge variant="success">True</Badge>
                          ) : (
                            <Badge variant="neutral">False</Badge>
                          )
                        ) : (
                          String(val ?? '—')
                        )}
                      </dd>
                    </div>
                  ))}
                </dl>
              </CardContent>
            </Card>

            {/* Diagnostic Signals Card */}
            <Card className="gf-comp-detail__card">
              <CardHeader>
                <CardTitle>Diagnostic Telemetry</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="gf-comp-detail__dl">
                  {Object.entries(data.diagnostics).map(([key, val]) => (
                    <div key={key} className="gf-comp-detail__dl-row">
                      <dt className="gf-comp-detail__dt">{key.replace(/_/g, ' ')}</dt>
                      <dd className="gf-comp-detail__dd">
                        {typeof val === 'boolean' ? (
                          val ? (
                            <Badge variant="success">Confirmed</Badge>
                          ) : (
                            <Badge variant="danger">Unconfirmed</Badge>
                          )
                        ) : (
                          String(val ?? '—')
                        )}
                      </dd>
                    </div>
                  ))}
                </dl>
              </CardContent>
            </Card>
          </div>

          {/* Recent Failures Card */}
          <Card className="gf-comp-detail__card gf-comp-detail__card--full">
            <CardHeader>
              <CardTitle>Recent Event Failures</CardTitle>
            </CardHeader>
            <CardContent>
              {data.recent_failures && data.recent_failures.length > 0 ? (
                <div className="gf-comp-detail__table-responsive">
                  <table className="gf-comp-detail__table">
                    <thead>
                      <tr>
                        <th>Event Type</th>
                        <th>Error Diagnostic</th>
                        <th>Attempts</th>
                        <th>Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.recent_failures.map((f) => (
                        <tr key={f.id}>
                          <td className="gf-comp-detail__cell-bold">{f.event_type}</td>
                          <td className="gf-comp-detail__cell-error">{f.error}</td>
                          <td>{f.attempt_count ?? 1}</td>
                          <td>{f.occurred_at ? new Date(f.occurred_at).toLocaleString() : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="gf-comp-detail__empty-failures">
                  <Badge variant="success">Clean</Badge>
                  <span>No recent delivery failures recorded for this subsystem.</span>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}
