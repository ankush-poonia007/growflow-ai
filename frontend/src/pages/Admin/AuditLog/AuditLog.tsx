import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminAuditLog } from '@/lib/api/client';
import type { AdminAuditLogResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './AuditLog.css';

/**
 * AD25 — Admin Audit Log
 *
 * Dense operational table exposing the authoritative platform event log from domain_events,
 * with search, filtering by actor role and resource type, and paginated navigation.
 */
export function AuditLog() {
  const [data, setData] = useState<AdminAuditLogResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [resourceFilter, setResourceFilter] = useState('ALL');
  const [page, setPage] = useState(0);
  const pageSize = 25;
  const [, startTransition] = useTransition();

  const fetchAudit = async (s: string, r: string, resType: string, p: number) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAuditLog({
        search: s.trim() || undefined,
        actor_role: r !== 'ALL' ? r : undefined,
        resource_type: resType !== 'ALL' ? resType : undefined,
        limit: pageSize,
        offset: p * pageSize,
      });
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve audit log.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit(search, roleFilter, resourceFilter, page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roleFilter, resourceFilter, page]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    setPage(0);
    startTransition(() => {
      fetchAudit(val, roleFilter, resourceFilter, 0);
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'PUBLISHED':
        return <Badge variant="success">Published</Badge>;
      case 'PENDING':
        return <Badge variant="warning">Pending</Badge>;
      case 'FAILED':
        return <Badge variant="danger">Failed</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const totalPages = data ? Math.ceil(data.total / pageSize) : 1;

  return (
    <div className="gf-audit-log">
      <div className="gf-audit-log__breadcrumb">
        <Link to="/admin/security" className="gf-audit-log__back-link">
          ← Back to Security & Audit
        </Link>
      </div>

      <PageHeader
        eyebrow="AUDIT TRAIL"
        title="Platform Audit Log"
        description="Immutable chronological record of platform state transitions, mentor evaluations, and system events."
        actions={
          <Button variant="secondary" size="sm" onClick={() => fetchAudit(search, roleFilter, resourceFilter, page)}>
            Refresh
          </Button>
        }
      />

      {error && (
        <div className="gf-audit-log__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={() => fetchAudit(search, roleFilter, resourceFilter, page)}>
            Retry
          </Button>
        </div>
      )}

      {/* Toolbar & Filters */}
      <div className="gf-audit-log__toolbar">
        <div className="gf-audit-log__search-wrapper">
          <svg className="gf-audit-log__search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="9" cy="9" r="6" />
            <line x1="13.5" y1="13.5" x2="18" y2="18" />
          </svg>
          <input
            type="search"
            placeholder="Search by event type, resource ID, or correlation ID..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="gf-audit-log__search-input"
            aria-label="Search audit log"
          />
        </div>

        <div className="gf-audit-log__filters">
          <select
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value);
              setPage(0);
            }}
            className="gf-audit-log__select"
            aria-label="Filter by actor role"
          >
            <option value="ALL">All Roles</option>
            <option value="STUDENT">Student</option>
            <option value="MENTOR">Mentor</option>
            <option value="ADMIN">Admin</option>
            <option value="SYSTEM">System</option>
          </select>

          <select
            value={resourceFilter}
            onChange={(e) => {
              setResourceFilter(e.target.value);
              setPage(0);
            }}
            className="gf-audit-log__select"
            aria-label="Filter by resource type"
          >
            <option value="ALL">All Resources</option>
            <option value="project">Project</option>
            <option value="group">Group / Cohort</option>
            <option value="user">User</option>
            <option value="task">Task</option>
            <option value="milestone">Milestone</option>
            <option value="blueprint">Blueprint</option>
            <option value="document">Document</option>
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      {loading ? (
        <Card className="gf-audit-log__card">
          <div className="gf-audit-log__skeleton-wrap">
            <Skeleton height="44px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" />
          </div>
        </Card>
      ) : !data || data.events.length === 0 ? (
        <EmptyState
          title="No audit events found"
          description={
            search || roleFilter !== 'ALL' || resourceFilter !== 'ALL'
              ? 'No audit events match your current search or filter criteria.'
              : 'There are currently no recorded domain events in the platform audit trail.'
          }
        />
      ) : (
        <Card className="gf-audit-log__card">
          <div className="gf-audit-log__table-responsive">
            <table className="gf-audit-log__table">
              <thead>
                <tr>
                  <th>Event Action</th>
                  <th>Actor</th>
                  <th>Target Resource</th>
                  <th>Status</th>
                  <th>Correlation ID</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {data.events.map((evt) => (
                  <tr key={evt.id}>
                    <td>
                      <span className="gf-audit-log__event-title">{evt.title}</span>
                      <span className="gf-audit-log__event-desc">{evt.description}</span>
                      <span className="gf-audit-log__event-type">{evt.event_type}</span>
                    </td>
                    <td>
                      <Badge variant="neutral">{evt.actor_role}</Badge>
                      {evt.actor_id && (
                        <span className="gf-audit-log__sub-id">ID: {evt.actor_id.slice(0, 8)}...</span>
                      )}
                    </td>
                    <td>
                      <span className="gf-audit-log__res-type">{evt.resource_type}</span>
                      <span className="gf-audit-log__sub-id">{evt.resource_id.slice(0, 12)}...</span>
                    </td>
                    <td>{getStatusBadge(evt.status)}</td>
                    <td>
                      <span className="gf-audit-log__correlation">
                        {evt.correlation_id ? evt.correlation_id.slice(0, 10) : '—'}
                      </span>
                    </td>
                    <td>
                      <span className="gf-audit-log__time">
                        {new Date(evt.occurred_at).toLocaleString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="gf-audit-log__pagination">
            <span className="gf-audit-log__page-info">
              Showing {data.offset + 1} to {Math.min(data.offset + pageSize, data.total)} of {data.total} events
            </span>
            <div className="gf-audit-log__page-actions">
              <Button
                variant="secondary"
                size="sm"
                disabled={page === 0}
                onClick={() => setPage((prev) => Math.max(0, prev - 1))}
              >
                Previous
              </Button>
              <span className="gf-audit-log__page-number">
                Page {page + 1} of {Math.max(1, totalPages)}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page + 1 >= totalPages}
                onClick={() => setPage((prev) => prev + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
