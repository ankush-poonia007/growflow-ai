import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminAIUsage } from '@/lib/api/client';
import type { AdminAIUsageResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AIUsage.css';

/**
 * AD12 — AI Usage
 *
 * Truthful execution volume, time trend, capability distributions, and project allocations.
 * Per-token and dollar pricing ledgers are truthfully disclosed as unmetered.
 */
export function AIUsage() {
  const [data, setData] = useState<AdminAIUsageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsage = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAIUsage();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve AI usage data.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsage();
  }, []);

  const overall = data?.overall_volume;
  const timeTrend = data?.time_trend || [];
  const capabilities = data?.capability_breakdown || [];
  const projects = data?.project_distribution || [];
  const outcomes = data?.outcome_distribution || {};

  return (
    <div className="gf-ai-usage">
      <PageHeader
        eyebrow="CAPACITY & VELOCITY"
        title="AI Execution Usage"
        description="Canonical AI transaction volumes, time-series trends, capability breakdowns, and project distributions."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchUsage}>
            Refresh
          </Button>
        }
      />

      <AISubNav />

      {error && (
        <div className="gf-ai-usage__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchUsage}>
            Retry
          </Button>
        </div>
      )}

      {/* Authoritative Unmetered Disclosure */}
      <section className="gf-ai-usage__banner" aria-label="Metering Policy">
        <div className="gf-ai-usage__banner-content">
          <div className="gf-ai-usage__banner-badges">
            <span className="gf-ai-usage__meter-pill">TOKEN METERING: UNMETERED / NOT PERSISTED</span>
            <span className="gf-ai-usage__meter-pill">RATE-LIMIT TELEMETRY: NOT PERSISTED</span>
          </div>
          <p className="gf-ai-usage__banner-desc">
            GrowFlow records canonical transactional AI runs (synthesis jobs, assistant messages, and change impact analyses). Upstream provider tokens and dollar billing are managed directly in OpenRouter.
          </p>
        </div>
      </section>

      {/* KPI Overview Tiles */}
      <section className="gf-ai-usage__kpi-grid" aria-label="Volume Overview">
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
              label="Total Transactions"
              value={overall?.total_recorded_transactions ?? 0}
              subtext="Across all platform AI capabilities"
            />
            <StatTile
              label="Blueprint Synthesis Runs"
              value={overall?.blueprint_synthesis_jobs ?? 0}
              subtext="Full generation & targeted repairs"
            />
            <StatTile
              label="AI Mentor Assistant Chats"
              value={overall?.ai_mentor_messages ?? 0}
              subtext="Direct student assistant responses"
            />
            <StatTile
              label="Project Change Analyses"
              value={overall?.project_change_analyses ?? 0}
              subtext="Proposal impact evaluations"
            />
          </>
        )}
      </section>

      {/* 2-Column: Capability Breakdown + Outcome Distribution */}
      <div className="gf-ai-usage__grid-2col">
        {/* Capability Breakdown */}
        <Card className="gf-ai-usage__card">
          <CardHeader>
            <CardTitle>Capability Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="160px" />
            ) : capabilities.length === 0 ? (
              <p className="gf-ai-usage__muted-text">No capability transactions recorded.</p>
            ) : (
              <ul className="gf-ai-usage__bar-list">
                {capabilities.map((cap) => (
                  <li key={cap.capability_key} className="gf-ai-usage__bar-item">
                    <div className="gf-ai-usage__bar-meta">
                      <span className="gf-ai-usage__bar-label">{cap.label}</span>
                      <span className="gf-ai-usage__bar-value">
                        {cap.count} ({cap.percentage}%)
                      </span>
                    </div>
                    <div className="gf-ai-usage__bar-track">
                      <div
                        className="gf-ai-usage__bar-fill"
                        style={{ width: `${cap.percentage}%` }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Outcome Distribution */}
        <Card className="gf-ai-usage__card">
          <CardHeader>
            <CardTitle>Execution Outcomes</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="160px" />
            ) : Object.keys(outcomes).length === 0 ? (
              <p className="gf-ai-usage__muted-text">No execution status outcomes recorded.</p>
            ) : (
              <div className="gf-ai-usage__outcomes-grid">
                {Object.entries(outcomes).map(([status, count]) => (
                  <div key={status} className="gf-ai-usage__outcome-box">
                    <span className="gf-ai-usage__outcome-label">{status}</span>
                    <span className="gf-ai-usage__outcome-count">{count}</span>
                    <Badge
                      variant={
                        status === 'COMPLETED'
                          ? 'success'
                          : status === 'FAILED'
                          ? 'danger'
                          : status === 'RUNNING'
                          ? 'warning'
                          : 'neutral'
                      }
                    >
                      {status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Time Trend Section */}
      <section className="gf-ai-usage__section" aria-label="Usage Time Trend">
        <Card>
          <CardHeader>
            <CardTitle>Daily Transaction Activity (Last 14 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="180px" />
            ) : timeTrend.length === 0 ? (
              <p className="gf-ai-usage__muted-text">No time-series transaction data in period.</p>
            ) : (
              <div className="gf-ai-usage__table-wrapper">
                <table className="gf-ai-usage__table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Blueprint Synthesis Jobs</th>
                      <th>AI Mentor Assistant Chats</th>
                      <th>Total Daily Transactions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {timeTrend.map((bucket) => (
                      <tr key={bucket.date}>
                        <td className="gf-ai-usage__mono-cell">{bucket.date}</td>
                        <td>{bucket.blueprint_jobs_count}</td>
                        <td>{bucket.mentor_messages_count}</td>
                        <td>
                          <strong>{bucket.total_count}</strong>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Project Distribution Section */}
      <section className="gf-ai-usage__section" aria-label="Project Distribution">
        <Card>
          <CardHeader>
            <CardTitle>Project Allocation (Top 10 Projects)</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="200px" />
            ) : projects.length === 0 ? (
              <EmptyState
                title="No Project Activity"
                description="No projects have generated AI synthesis jobs or mentor chats yet."
              />
            ) : (
              <div className="gf-ai-usage__table-wrapper">
                <table className="gf-ai-usage__table">
                  <thead>
                    <tr>
                      <th>Project</th>
                      <th>Synthesis Runs</th>
                      <th>Mentor Messages</th>
                      <th>Total Transactions</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projects.map((proj) => (
                      <tr key={proj.project_id}>
                        <td>
                          <strong>{proj.project_name}</strong>
                          <div className="gf-ai-usage__mono-cell">{proj.project_id.slice(0, 8)}…</div>
                        </td>
                        <td>{proj.synthesis_jobs_count}</td>
                        <td>{proj.mentor_messages_count}</td>
                        <td>
                          <strong>{proj.total_transactions}</strong>
                        </td>
                        <td>
                          <Link
                            to={`/admin/instances/${proj.project_id}`}
                            className="gf-ai-usage__link"
                          >
                            View Instance →
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
