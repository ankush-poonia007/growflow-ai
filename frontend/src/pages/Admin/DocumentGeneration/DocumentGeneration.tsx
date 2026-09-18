import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminGenerationJobs } from '@/lib/api/client';
import type { AdminGenerationJobsResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './DocumentGeneration.css';

/**
 * Format duration in seconds to readable string or N/A.
 */
function formatDuration(seconds?: number | null): string {
  if (seconds === null || seconds === undefined) return 'N/A';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const remSec = Math.round(seconds % 60);
  return `${mins}m ${remSec}s`;
}

/**
 * Format ISO datetime string to localized date/time.
 */
function formatDateTime(iso?: string | null): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString('en-US', {
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
 * AD23 — Document Generation Runs
 *
 * Operational governance monitoring canonical blueprint_jobs generation workloads,
 * step progress, duration calculations, and sanitized runtime failures.
 */
export function DocumentGeneration() {
  const [data, setData] = useState<AdminGenerationJobsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [jobTypeFilter, setJobTypeFilter] = useState('ALL');
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const fetchJobs = async (st: string, jt: string, p: number) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminGenerationJobs({
        status: st !== 'ALL' ? st : undefined,
        job_type: jt !== 'ALL' ? jt : undefined,
        limit: pageSize,
        offset: p * pageSize,
      });
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve generation jobs.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(statusFilter, jobTypeFilter, page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, jobTypeFilter, page]);

  const getStatusBadge = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED':
        return <Badge variant="success">Completed</Badge>;
      case 'RUNNING':
        return <Badge variant="warning">Running</Badge>;
      case 'FAILED':
        return <Badge variant="danger">Failed</Badge>;
      case 'PENDING':
        return <Badge variant="neutral">Pending</Badge>;
      case 'CANCELLED':
        return <Badge variant="neutral">Cancelled</Badge>;
      default:
        return <Badge variant="neutral">{status || 'Unknown'}</Badge>;
    }
  };

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;
  const summary = data?.summary;

  return (
    <div className="gf-doc-gen">
      <div className="gf-doc-gen__breadcrumb">
        <Link to="/admin/documents" className="gf-doc-gen__back-link">
          ← Back to Documents & Knowledge
        </Link>
      </div>

      <PageHeader
        eyebrow="SYNTHESIS WORKLOADS"
        title="Document Generation Runs"
        description="Authoritative audit of blueprint synthesis jobs, generation progress, and sanitized execution diagnostics."
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={() => fetchJobs(statusFilter, jobTypeFilter, page)}
          >
            Refresh Runs
          </Button>
        }
      />

      {error && (
        <div className="gf-doc-gen__alert" role="alert">
          <span>{error}</span>
          <Button
            variant="tertiary"
            size="sm"
            onClick={() => fetchJobs(statusFilter, jobTypeFilter, page)}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Summary Metrics */}
      <div className="gf-doc-gen__summary-grid">
        <StatTile
          label="Total Workloads"
          value={loading && !data ? '—' : (summary?.total_jobs ?? 0)}
          subtext="Canonical generation runs"
        />
        <StatTile
          label="Completed"
          value={loading && !data ? '—' : (summary?.completed_jobs ?? 0)}
          subtext="Successfully synthesized"
        />
        <StatTile
          label="Running / Pending"
          value={
            loading && !data
              ? '—'
              : (summary?.running_jobs ?? 0) + (summary?.pending_jobs ?? 0)
          }
          subtext="Active execution queue"
        />
        <StatTile
          label="Failed"
          value={loading && !data ? '—' : (summary?.failed_jobs ?? 0)}
          subtext="Workload execution errors"
        />
        <StatTile
          label="Avg Duration"
          value={
            loading && !data
              ? '—'
              : formatDuration(summary?.average_duration_seconds)
          }
          subtext="From completed runs"
        />
      </div>

      {/* Filters Toolbar */}
      <Card className="gf-doc-gen__filter-card">
        <div className="gf-doc-gen__filters">
          <div className="gf-doc-gen__filter-group">
            <label htmlFor="gen-status" className="gf-doc-gen__filter-label">
              Status
            </label>
            <select
              id="gen-status"
              className="gf-doc-gen__select"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(0);
              }}
            >
              <option value="ALL">All Statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="RUNNING">Running</option>
              <option value="FAILED">Failed</option>
              <option value="PENDING">Pending</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>

          <div className="gf-doc-gen__filter-group">
            <label htmlFor="gen-type" className="gf-doc-gen__filter-label">
              Workload Type
            </label>
            <select
              id="gen-type"
              className="gf-doc-gen__select"
              value={jobTypeFilter}
              onChange={(e) => {
                setJobTypeFilter(e.target.value);
                setPage(0);
              }}
            >
              <option value="ALL">All Types</option>
              <option value="FULL_BLUEPRINT">Full Blueprint</option>
              <option value="SYSTEM_ARCHITECTURE">System Architecture</option>
              <option value="API_SPEC">API Specification</option>
              <option value="DATA_MODEL">Data Model</option>
              <option value="TASKS_AND_ROADMAP">Tasks & Roadmap</option>
              <option value="RISK_REGISTER">Risk Register</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Jobs Table */}
      <Card className="gf-doc-gen__table-card">
        {loading && !data ? (
          <div className="gf-doc-gen__loading">
            <Skeleton height="40px" className="mb-2" />
            <Skeleton height="56px" className="mb-2" />
            <Skeleton height="56px" className="mb-2" />
            <Skeleton height="56px" className="mb-2" />
            <Skeleton height="56px" />
          </div>
        ) : !data?.jobs || data.jobs.length === 0 ? (
          <EmptyState
            title="No Generation Runs"
            description={
              statusFilter !== 'ALL' || jobTypeFilter !== 'ALL'
                ? 'No generation workloads match the selected filters.'
                : 'No blueprint generation runs have been recorded in the platform.'
            }
          />
        ) : (
          <div className="gf-table-container">
            <table className="gf-table gf-doc-gen__table" aria-label="Document Generation Runs">
              <thead>
                <tr>
                  <th scope="col">Job ID / Step</th>
                  <th scope="col">Project</th>
                  <th scope="col">Job Type</th>
                  <th scope="col">Target Output</th>
                  <th scope="col">Status</th>
                  <th scope="col">Progress</th>
                  <th scope="col">Duration</th>
                  <th scope="col">Started</th>
                  <th scope="col">Completed</th>
                </tr>
              </thead>
              <tbody>
                {data.jobs.map((job) => (
                  <tr key={job.id}>
                    <td>
                      <div className="gf-doc-gen__job-cell">
                        <code className="gf-doc-gen__job-id">{job.id.slice(0, 8)}</code>
                        {job.current_step && (
                          <span className="gf-doc-gen__step">{job.current_step}</span>
                        )}
                        {job.error && (
                          <span className="gf-doc-gen__error" title={job.error}>
                            Error: {job.error}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="gf-doc-gen__project-name">
                        {job.project_name || '—'}
                      </span>
                    </td>
                    <td>
                      <Badge variant="neutral">{job.job_type || 'GENERATION'}</Badge>
                    </td>
                    <td>
                      <span className="gf-doc-gen__output">
                        {job.target_output || 'blueprint.md'}
                      </span>
                    </td>
                    <td>{getStatusBadge(job.status)}</td>
                    <td>
                      <div className="gf-doc-gen__progress-cell">
                        <div className="gf-doc-gen__progress-bar">
                          <div
                            className="gf-doc-gen__progress-fill"
                            style={{ width: `${Math.min(100, Math.max(0, job.progress_percent))}%` }}
                          />
                        </div>
                        <span className="gf-doc-gen__progress-val">
                          {job.progress_percent}%
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="gf-doc-gen__duration">
                        {formatDuration(job.duration_seconds)}
                      </span>
                    </td>
                    <td>
                      <span className="gf-doc-gen__date">{formatDateTime(job.started_at)}</span>
                    </td>
                    <td>
                      <span className="gf-doc-gen__date">{formatDateTime(job.completed_at)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Toolbar */}
        {data && data.total > 0 && (
          <div className="gf-doc-gen__pagination">
            <span className="gf-doc-gen__pagination-info">
              Showing {data.offset + 1} to {Math.min(data.offset + data.limit, data.total)} of{' '}
              {data.total} workloads
            </span>
            <div className="gf-doc-gen__pagination-controls">
              <Button
                variant="secondary"
                size="sm"
                disabled={page === 0 || loading}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
              >
                Previous
              </Button>
              <span className="gf-doc-gen__page-indicator">
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
          </div>
        )}
      </Card>
    </div>
  );
}
