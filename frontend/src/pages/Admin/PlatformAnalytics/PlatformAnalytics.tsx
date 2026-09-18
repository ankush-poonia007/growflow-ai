import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminAnalytics } from '@/lib/api/client';
import type { AdminPlatformAnalyticsResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import './PlatformAnalytics.css';

/**
 * Distribution List Component rendering key-value counts with relative proportional bars.
 */
function DistributionBlock({
  title,
  data,
}: {
  title: string;
  data?: Record<string, number>;
}) {
  const entries = Object.entries(data || {});
  const total = entries.reduce((acc, [, val]) => acc + val, 0);

  return (
    <Card className="gf-analytics__dist-card">
      <CardHeader className="gf-analytics__dist-header">
        <CardTitle className="gf-analytics__dist-title">{title}</CardTitle>
        <span className="gf-analytics__dist-total">{total} Total</span>
      </CardHeader>
      <CardContent className="gf-analytics__dist-content">
        {entries.length === 0 ? (
          <span className="gf-analytics__dist-empty">No distribution records</span>
        ) : (
          <ul className="gf-analytics__dist-list">
            {entries.map(([key, count]) => {
              const pct = total > 0 ? Math.round((count / total) * 100) : 0;
              return (
                <li key={key} className="gf-analytics__dist-item">
                  <div className="gf-analytics__dist-meta">
                    <span className="gf-analytics__dist-key">{key}</span>
                    <span className="gf-analytics__dist-count">
                      {count} ({pct}%)
                    </span>
                  </div>
                  <div className="gf-analytics__meter-bg">
                    <div
                      className="gf-analytics__meter-fill"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * AD28 — Platform Analytics
 *
 * Macro telemetry dashboard synthesizing database-level aggregates across projects,
 * users, tasks, generation runs, deliverables, and domain events.
 */
export function PlatformAnalytics() {
  const [data, setData] = useState<AdminPlatformAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAnalytics();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve platform analytics.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const overview = data?.overview;

  return (
    <div className="gf-analytics">
      <PageHeader
        eyebrow="MACRO TELEMETRY"
        title="Platform Analytics"
        description="Comprehensive system velocity, population metrics, and operational distributions derived strictly from canonical database records."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchAnalytics}>
            Refresh Analytics
          </Button>
        }
      />

      {error && (
        <div className="gf-analytics__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchAnalytics}>
            Retry
          </Button>
        </div>
      )}

      {/* Dimensional Deep-Dive Navigation */}
      <div className="gf-analytics__dimensions-nav">
        <span className="gf-analytics__dimensions-label">Dimensional Deep Dives:</span>
        <div className="gf-analytics__dimensions-links">
          <Link to="/admin/analytics/projects" className="gf-analytics__dim-link">
            Projects Telemetry →
          </Link>
          <Link to="/admin/analytics/users" className="gf-analytics__dim-link">
            User Demographics →
          </Link>
          <Link to="/admin/analytics/documents" className="gf-analytics__dim-link">
            Deliverable Corpus →
          </Link>
          <Link to="/admin/analytics/activity" className="gf-analytics__dim-link">
            Event Velocity →
          </Link>
        </div>
      </div>

      {/* Primary Macro Stat Tiles */}
      <div className="gf-analytics__overview-grid">
        <StatTile
          label="Total Users"
          value={loading && !data ? '—' : (overview?.total_users ?? 0)}
          subtext={
            overview
              ? `${overview.total_students} students, ${overview.total_mentors} mentors`
              : 'Canonical registered accounts'
          }
        />
        <StatTile
          label="Active Cohorts"
          value={loading && !data ? '—' : (overview?.total_groups ?? 0)}
          subtext="Institutional student groups"
        />
        <StatTile
          label="Total Projects"
          value={loading && !data ? '—' : (overview?.total_projects ?? 0)}
          subtext={
            overview
              ? `${overview.active_projects} active, ${overview.at_risk_projects} at risk`
              : 'Project workspace instances'
          }
        />
        <StatTile
          label="Deliverables"
          value={loading && !data ? '—' : (overview?.total_documents ?? 0)}
          subtext="Blueprints, specs, & readmes"
        />
        <StatTile
          label="Generation Runs"
          value={loading && !data ? '—' : (overview?.total_generation_jobs ?? 0)}
          subtext="Synthesis pipeline workloads"
        />
        <StatTile
          label="Domain Events"
          value={loading && !data ? '—' : (overview?.total_domain_events ?? 0)}
          subtext="Authoritative audit trail entries"
        />
      </div>

      {/* Canonical Distributions Grid */}
      <div className="gf-analytics__section-header">
        <h2 className="gf-analytics__section-title">Canonical Distributions</h2>
        <Badge variant="neutral">Live Database Aggregates</Badge>
      </div>

      {loading && !data ? (
        <div className="gf-analytics__loading-grid">
          <Skeleton height="200px" />
          <Skeleton height="200px" />
          <Skeleton height="200px" />
          <Skeleton height="200px" />
          <Skeleton height="200px" />
          <Skeleton height="200px" />
        </div>
      ) : data ? (
        <div className="gf-analytics__distributions-grid">
          <DistributionBlock
            title="Project Lifecycle Phases"
            data={data.project_phase_distribution}
          />
          <DistributionBlock
            title="Project Health Classifications"
            data={data.project_health_distribution}
          />
          <DistributionBlock
            title="Task Execution Statuses"
            data={data.task_status_distribution}
          />
          <DistributionBlock
            title="User Account Statuses"
            data={data.user_status_distribution}
          />
          <DistributionBlock
            title="Generation Job Outcomes"
            data={data.generation_job_distribution}
          />
          <DistributionBlock
            title="Deliverable Document Types"
            data={data.document_type_distribution}
          />
          <DistributionBlock
            title="Help Request Statuses"
            data={data.help_request_distribution}
          />
          <DistributionBlock
            title="Top Event Activity Types"
            data={data.event_type_distribution}
          />
        </div>
      ) : null}
    </div>
  );
}
