import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminSystemHealth } from '@/lib/api/client';
import type { AdminSystemHealthResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import './SystemHealth.css';

/**
 * AD19 — Admin System Health
 *
 * Real-time operational governance instrument monitoring core runtime availability,
 * database connectivity, AI key availability, and outbox event delivery.
 */
export function SystemHealth() {
  const [data, setData] = useState<AdminSystemHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminSystemHealth();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve platform system health.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'OPERATIONAL':
        return <Badge variant="success">Operational</Badge>;
      case 'CONFIGURED':
        return <Badge variant="neutral">Configured</Badge>;
      case 'DEGRADED':
        return <Badge variant="warning">Degraded</Badge>;
      case 'CRITICAL':
        return <Badge variant="danger">Critical</Badge>;
      case 'UNAVAILABLE':
        return <Badge variant="danger">Unavailable</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="gf-sys-health">
      <PageHeader
        eyebrow="SYSTEM OBSERVABILITY"
        title="System Health"
        description="Real-time operational status, database connectivity, and messaging health across platform subsystems."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchHealth}>
            Refresh Status
          </Button>
        }
      />

      {error && (
        <div className="gf-sys-health__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchHealth}>
            Retry
          </Button>
        </div>
      )}

      {/* KPI Overview Tiles */}
      <section className="gf-sys-health__kpi-grid" aria-label="System Metrics">
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
              label="Overall System Status"
              value={data?.overall_status ?? 'UNKNOWN'}
              subtext={`Environment: ${data?.environment ?? 'development'} • v${data?.version ?? '0.1.0'}`}
            />
            <StatTile
              label="Database State"
              value={data?.metrics?.db_connected ? 'Connected' : 'Disconnected'}
              subtext={`Pool size: ${data?.metrics?.db_pool_size ?? 5} connections`}
            />
            <StatTile
              label="Active AI Keys"
              value={data?.metrics?.active_ai_keys ?? 0}
              subtext="OpenRouter provider keys configured"
            />
            <StatTile
              label="Outbox Delivery"
              value={data?.metrics?.outbox_failed === 0 ? 'Normal' : `${data?.metrics?.outbox_failed} Failed`}
              subtext={`${data?.metrics?.outbox_pending ?? 0} pending • ${data?.metrics?.outbox_published ?? 0} published`}
            />
          </>
        )}
      </section>

      {/* Subsystem Inspection Grid */}
      <section className="gf-sys-health__subsystems" aria-label="Subsystems">
        <h2 className="gf-sys-health__section-title">Core Subsystems</h2>
        <div className="gf-sys-health__grid">
          {loading ? (
            <>
              <Skeleton height="140px" />
              <Skeleton height="140px" />
              <Skeleton height="140px" />
              <Skeleton height="140px" />
            </>
          ) : (
            data?.subsystems.map((subsystem) => (
              <Card key={subsystem.id} className="gf-sys-health__card">
                <CardHeader className="gf-sys-health__card-header">
                  <div>
                    <CardTitle className="gf-sys-health__card-title">{subsystem.name}</CardTitle>
                    <span className="gf-sys-health__category-tag">{subsystem.type}</span>
                  </div>
                  {getStatusBadge(subsystem.status)}
                </CardHeader>
                <CardContent className="gf-sys-health__card-content">
                  <p className="gf-sys-health__details">{subsystem.details}</p>
                  <div className="gf-sys-health__card-footer">
                    <Link
                      to={`/admin/system-health/${subsystem.id}`}
                      className="gf-sys-health__inspect-link"
                    >
                      Inspect Component →
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
