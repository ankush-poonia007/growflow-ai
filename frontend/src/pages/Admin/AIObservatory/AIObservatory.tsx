import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminAIObservatory } from '@/lib/api/client';
import type { AdminAIObservatoryResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AIObservatory.css';

function formatDate(iso?: string | null): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

/**
 * AD11 — AI Observatory
 *
 * Operational governance dashboard presenting gateway posture, macro KPIs,
 * active generation runs, and recent AI domain activity.
 */
export function AIObservatory() {
  const [data, setData] = useState<AdminAIObservatoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchObservatory = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAIObservatory();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve AI Observatory data.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchObservatory();
  }, []);

  const gateway = data?.gateway;
  const kpis = data?.kpis;
  const activeJobs = data?.active_jobs || [];
  const recentActivity = data?.recent_activity || [];

  return (
    <div className="gf-ai-obs">
      <PageHeader
        eyebrow="AI SUBSYSTEM OBSERVABILITY"
        title="AI Observatory"
        description="Operational governance dashboard providing real-time gateway posture, synthesis velocity, and active execution monitoring."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchObservatory}>
            Refresh
          </Button>
        }
      />

      <AISubNav />

      {error && (
        <div className="gf-ai-obs__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchObservatory}>
            Retry
          </Button>
        </div>
      )}

      {/* Gateway Posture Card */}
      <section className="gf-ai-obs__section" aria-label="AI Gateway Posture">
        <Card className="gf-ai-obs__gateway-card">
          <CardHeader className="gf-ai-obs__gateway-header">
            <div>
              <CardTitle className="gf-ai-obs__gateway-title">AI Provider Gateway Posture</CardTitle>
              <p className="gf-ai-obs__gateway-subtitle">
                Canonical gateway configuration, active credential slots, and execution routing.
              </p>
            </div>
            {loading ? (
              <Skeleton width="100px" height="24px" />
            ) : (
              <Badge variant={gateway?.configured_active_keys ? 'success' : 'warning'}>
                {gateway?.configured_active_keys ? 'Active Credential Pool' : 'No Keys Configured'}
              </Badge>
            )}
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="gf-ai-obs__gateway-grid">
                <Skeleton height="70px" />
                <Skeleton height="70px" />
                <Skeleton height="70px" />
                <Skeleton height="70px" />
              </div>
            ) : (
              <div className="gf-ai-obs__gateway-grid">
                <div className="gf-ai-obs__prop-box">
                  <span className="gf-ai-obs__prop-label">Provider</span>
                  <span className="gf-ai-obs__prop-val">{gateway?.provider || '—'}</span>
                </div>
                <div className="gf-ai-obs__prop-box">
                  <span className="gf-ai-obs__prop-label">Configured Slots</span>
                  <span className="gf-ai-obs__prop-val">
                    {gateway?.configured_active_keys} of {gateway?.total_key_slots} Slots
                  </span>
                </div>
                <div className="gf-ai-obs__prop-box">
                  <span className="gf-ai-obs__prop-label">Default Model</span>
                  <span className="gf-ai-obs__prop-val gf-ai-obs__prop-val--mono">
                    {gateway?.default_model || '—'}
                  </span>
                </div>
                <div className="gf-ai-obs__prop-box">
                  <span className="gf-ai-obs__prop-label">Rotation Strategy</span>
                  <span className="gf-ai-obs__prop-val">{gateway?.rotation_strategy || '—'}</span>
                </div>
                <div className="gf-ai-obs__prop-box gf-ai-obs__prop-box--full">
                  <span className="gf-ai-obs__prop-label">Gateway Base URL</span>
                  <span className="gf-ai-obs__prop-val gf-ai-obs__prop-val--mono">
                    {gateway?.gateway_base_url || '—'}
                  </span>
                </div>
              </div>
            )}
            {gateway?.credential_note && (
              <p className="gf-ai-obs__credential-note">
                <strong>Notice:</strong> {gateway.credential_note}
              </p>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Operational KPI Tiles */}
      <section className="gf-ai-obs__kpi-grid" aria-label="AI Execution KPIs">
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
              label="Total AI Transactions"
              value={kpis?.total_ai_transactions ?? 0}
              subtext="Synthesis runs, mentor chats & change analyses"
            />
            <StatTile
              label="Blueprint Success Rate"
              value={kpis?.success_rate_percent !== null && kpis?.success_rate_percent !== undefined ? `${kpis.success_rate_percent}%` : '—'}
              subtext={`${kpis?.blueprint_jobs_completed ?? 0} passed / ${kpis?.blueprint_jobs_total ?? 0} total jobs`}
            />
            <StatTile
              label="Active Synthesis Jobs"
              value={kpis?.currently_running_jobs ?? 0}
              subtext="Currently executing in pipeline"
            />
            <StatTile
              label="Avg Synthesis Duration"
              value={kpis?.average_duration_seconds !== null && kpis?.average_duration_seconds !== undefined ? `${kpis.average_duration_seconds}s` : '—'}
              subtext="Calculated from completed runs"
            />
          </>
        )}
      </section>

      {/* Active Jobs Section */}
      <section className="gf-ai-obs__section" aria-label="Active Synthesis Jobs">
        <div className="gf-ai-obs__section-head">
          <h2 className="gf-ai-obs__section-title">Active Blueprint Synthesis Jobs</h2>
          <Link to="/admin/ai/executions" className="gf-ai-obs__view-all-link">
            View All Executions →
          </Link>
        </div>

        {loading ? (
          <Skeleton height="160px" />
        ) : activeJobs.length === 0 ? (
          <Card>
            <CardContent className="gf-ai-obs__empty-container">
              <EmptyState
                title="No Active AI Synthesis Jobs"
                description="There are currently no blueprint generation or targeted retry runs executing in the pipeline."
              />
            </CardContent>
          </Card>
        ) : (
          <div className="gf-ai-obs__table-wrapper">
            <table className="gf-ai-obs__table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Project</th>
                  <th>Job Type</th>
                  <th>Status</th>
                  <th>Current Step</th>
                  <th>Progress</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {activeJobs.map((job) => (
                  <tr key={job.id}>
                    <td>
                      <Link to={`/admin/ai/executions/${job.id}`} className="gf-ai-obs__code-link">
                        {job.id.slice(0, 8)}…
                      </Link>
                    </td>
                    <td>{job.project_name}</td>
                    <td>
                      <Badge variant="neutral">{job.job_type}</Badge>
                    </td>
                    <td>
                      <Badge variant="warning">{job.status}</Badge>
                    </td>
                    <td className="gf-ai-obs__mono-cell">{job.current_step || 'INITIALIZING'}</td>
                    <td>
                      <div className="gf-ai-obs__prog-cell">
                        <div className="gf-ai-obs__prog-bar">
                          <div
                            className="gf-ai-obs__prog-fill"
                            style={{ width: `${job.progress_percent}%` }}
                          />
                        </div>
                        <span className="gf-ai-obs__prog-text">{job.progress_percent}%</span>
                      </div>
                    </td>
                    <td>{formatDate(job.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Recent AI Activity */}
      <section className="gf-ai-obs__section" aria-label="Recent AI Activity">
        <div className="gf-ai-obs__section-head">
          <h2 className="gf-ai-obs__section-title">Recent Operational AI Activity</h2>
        </div>

        {loading ? (
          <Skeleton height="200px" />
        ) : recentActivity.length === 0 ? (
          <Card>
            <CardContent className="gf-ai-obs__empty-container">
              <EmptyState
                title="No Recent Activity"
                description="No recent AI operational events or messages have been recorded yet."
              />
            </CardContent>
          </Card>
        ) : (
          <div className="gf-ai-obs__table-wrapper">
            <table className="gf-ai-obs__table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Activity</th>
                  <th>Project</th>
                  <th>Status</th>
                  <th>Correlation</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {recentActivity.map((act) => (
                  <tr key={act.id}>
                    <td>
                      <Badge variant="neutral">{act.activity_type}</Badge>
                    </td>
                    <td>
                      <div className="gf-ai-obs__act-title">{act.title}</div>
                      <div className="gf-ai-obs__act-detail">{act.detail}</div>
                    </td>
                    <td>{act.project_name || '—'}</td>
                    <td>
                      <Badge
                        variant={
                          act.status === 'COMPLETED' || act.status === 'PUBLISHED'
                            ? 'success'
                            : act.status === 'FAILED'
                            ? 'danger'
                            : 'neutral'
                        }
                      >
                        {act.status}
                      </Badge>
                    </td>
                    <td className="gf-ai-obs__mono-cell">
                      {act.correlation_id ? act.correlation_id.slice(0, 8) + '…' : '—'}
                    </td>
                    <td>{formatDate(act.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Operational Notice */}
      <section className="gf-ai-obs__notices" aria-label="Operational Governance Disclosures">
        <Card className="gf-ai-obs__notice-card">
          <CardHeader>
            <CardTitle className="gf-ai-obs__notice-title">Operational Data Boundaries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-ai-obs__notice-grid">
              <div className="gf-ai-obs__notice-item">
                <span className="gf-ai-obs__notice-badge">UNMETERED / NOT PERSISTED</span>
                <p className="gf-ai-obs__notice-text">
                  Per-token telemetry is not persisted in the application database. Volume reflects recorded transactions.
                </p>
              </div>
              <div className="gf-ai-obs__notice-item">
                <span className="gf-ai-obs__notice-badge">NOT PERSISTED</span>
                <p className="gf-ai-obs__notice-text">
                  Dollar cost accounting is managed upstream by OpenRouter. No pricing ledger is simulated.
                </p>
              </div>
              <div className="gf-ai-obs__notice-item">
                <span className="gf-ai-obs__notice-badge">RUNTIME_ONLY</span>
                <p className="gf-ai-obs__notice-text">
                  Key pool rotation posture is tracked in-memory across configured environment slots.
                </p>
              </div>
              <div className="gf-ai-obs__notice-item">
                <span className="gf-ai-obs__notice-badge">UNAVAILABLE</span>
                <p className="gf-ai-obs__notice-text">
                  Provider DNS/TLS latency, TTFT, and packet wire traces are unmetered at the application layer.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
