import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminAIExecutions } from '@/lib/api/client';
import type { AdminAIExecutionsResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AIExecutions.css';

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
 * AD13 — Agent Executions
 *
 * Canonical execution inventory tracking blueprint generation runs,
 * targeted repair passes, pipeline lifecycle stages, and execution durations.
 */
export function AIExecutions() {
  const [data, setData] = useState<AdminAIExecutionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [jobTypeFilter, setJobTypeFilter] = useState('ALL');
  const [page, setPage] = useState(0);
  const pageSize = 25;
  const [, startTransition] = useTransition();

  const fetchExecutions = async (status: string, jobType: string, p: number) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAIExecutions({
        status: status === 'ALL' ? undefined : status,
        job_type: jobType === 'ALL' ? undefined : jobType,
        limit: pageSize,
        offset: p * pageSize,
      });
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve AI executions.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions(statusFilter, jobTypeFilter, page);
  }, [statusFilter, jobTypeFilter, page]);

  const handleStatusChange = (newStatus: string) => {
    startTransition(() => {
      setStatusFilter(newStatus);
      setPage(0);
    });
  };

  const handleJobTypeChange = (newType: string) => {
    startTransition(() => {
      setJobTypeFilter(newType);
      setPage(0);
    });
  };

  const summary = data?.summary;
  const executions = data?.executions || [];
  const total = data?.total || 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="gf-ai-execs">
      <PageHeader
        eyebrow="EXECUTION LIFECYCLE"
        title="Agent Executions"
        description="Authoritative ledger of blueprint synthesis jobs, targeted repairs, and pipeline transitions."
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={() => fetchExecutions(statusFilter, jobTypeFilter, page)}
          >
            Refresh
          </Button>
        }
      />

      <AISubNav />

      {error && (
        <div className="gf-ai-execs__alert" role="alert">
          <span>{error}</span>
          <Button
            variant="tertiary"
            size="sm"
            onClick={() => fetchExecutions(statusFilter, jobTypeFilter, page)}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Execution Summary Tiles */}
      <section className="gf-ai-execs__kpi-grid" aria-label="Executions Summary">
        {loading && !data ? (
          <>
            <Skeleton height="100px" />
            <Skeleton height="100px" />
            <Skeleton height="100px" />
            <Skeleton height="100px" />
          </>
        ) : (
          <>
            <StatTile label="Total Executions" value={summary?.total ?? 0} />
            <StatTile label="Completed Runs" value={summary?.completed ?? 0} />
            <StatTile label="Failed Runs" value={summary?.failed ?? 0} />
            <StatTile label="Active / Running" value={summary?.running ?? 0} />
          </>
        )}
      </section>

      {/* Filters Bar */}
      <section className="gf-ai-execs__controls" aria-label="Execution Filters">
        <div className="gf-ai-execs__filters">
          <div className="gf-ai-execs__filter-group">
            <label htmlFor="status-filter" className="gf-ai-execs__filter-label">
              Status:
            </label>
            <select
              id="status-filter"
              className="gf-ai-execs__select"
              value={statusFilter}
              onChange={(e) => handleStatusChange(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="FAILED">Failed</option>
              <option value="RUNNING">Running</option>
              <option value="PENDING">Pending</option>
            </select>
          </div>

          <div className="gf-ai-execs__filter-group">
            <label htmlFor="type-filter" className="gf-ai-execs__filter-label">
              Type:
            </label>
            <select
              id="type-filter"
              className="gf-ai-execs__select"
              value={jobTypeFilter}
              onChange={(e) => handleJobTypeChange(e.target.value)}
            >
              <option value="ALL">All Types</option>
              <option value="FULL_GENERATION">Full Generation</option>
              <option value="TARGETED_RETRY">Targeted Retry</option>
            </select>
          </div>
        </div>

        <div className="gf-ai-execs__pagination-info">
          Showing {executions.length > 0 ? page * pageSize + 1 : 0}–
          {Math.min((page + 1) * pageSize, total)} of {total} runs
        </div>
      </section>

      {/* Executions Table */}
      <section className="gf-ai-execs__table-section" aria-label="Executions Inventory">
        {loading ? (
          <Skeleton height="320px" />
        ) : executions.length === 0 ? (
          <Card>
            <CardContent className="gf-ai-execs__empty">
              <EmptyState
                title="No Executions Found"
                description="No canonical AI executions match the selected filter criteria."
              />
            </CardContent>
          </Card>
        ) : (
          <div className="gf-ai-execs__table-wrapper">
            <table className="gf-ai-execs__table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Project</th>
                  <th>Job Type</th>
                  <th>Status</th>
                  <th>Current Step</th>
                  <th>Progress</th>
                  <th>Duration</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {executions.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <Link
                        to={`/admin/ai/executions/${item.id}`}
                        className="gf-ai-execs__code-link"
                      >
                        {item.id.slice(0, 8)}…
                      </Link>
                    </td>
                    <td>
                      <strong>{item.project_name}</strong>
                    </td>
                    <td>
                      <Badge variant="neutral">{item.job_type}</Badge>
                      {item.target_output && (
                        <span className="gf-ai-execs__target-tag"> ({item.target_output})</span>
                      )}
                    </td>
                    <td>
                      <Badge
                        variant={
                          item.status === 'COMPLETED'
                            ? 'success'
                            : item.status === 'FAILED'
                            ? 'danger'
                            : item.status === 'RUNNING'
                            ? 'warning'
                            : 'neutral'
                        }
                      >
                        {item.status}
                      </Badge>
                    </td>
                    <td className="gf-ai-execs__mono-cell">
                      {item.current_step || (item.status === 'COMPLETED' ? 'COMPLETED' : '—')}
                    </td>
                    <td>
                      <div className="gf-ai-execs__prog-cell">
                        <div className="gf-ai-execs__prog-bar">
                          <div
                            className="gf-ai-execs__prog-fill"
                            style={{ width: `${item.progress_percent}%` }}
                          />
                        </div>
                        <span className="gf-ai-execs__prog-text">{item.progress_percent}%</span>
                      </div>
                    </td>
                    <td>{item.duration_seconds !== null ? `${item.duration_seconds}s` : '—'}</td>
                    <td>{formatDate(item.created_at)}</td>
                    <td>
                      <Link
                        to={`/admin/ai/executions/${item.id}`}
                        className="gf-ai-execs__action-link"
                      >
                        Trace →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="gf-ai-execs__pagination">
            <Button
              variant="secondary"
              size="sm"
              disabled={page === 0 || loading}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
            >
              Previous
            </Button>
            <span className="gf-ai-execs__page-indicator">
              Page {page + 1} of {totalPages}
            </span>
            <Button
              variant="secondary"
              size="sm"
              disabled={page >= totalPages - 1 || loading}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        )}
      </section>
    </div>
  );
}
