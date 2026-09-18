import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminGroups } from '@/lib/api/client';
import type { AdminGroupSummary } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupsDirectory.css';

/**
 * AD06 — Groups Directory
 *
 * Governance overview of all platform cohorts, supervising mentors,
 * and student/project enrollment metrics.
 */
export function GroupsDirectory() {
  const [groups, setGroups] = useState<AdminGroupSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [, startTransition] = useTransition();

  const fetchGroups = async (s: string, st: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminGroups({
        search: s.trim() || undefined,
        status: st !== 'ALL' ? st : undefined,
      });
      setGroups(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve groups directory.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups(search, statusFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    startTransition(() => {
      fetchGroups(val, statusFilter);
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return <Badge variant="success">Active</Badge>;
      case 'ARCHIVED':
        return <Badge variant="neutral">Archived</Badge>;
      case 'PAUSED':
        return <Badge variant="warning">Paused</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="gf-groups-directory">
      <PageHeader
        eyebrow="RESOURCE GOVERNANCE"
        title="Groups Directory"
        description="Inspect platform cohorts, supervising mentors, and student enrollment volumes."
      />

      {error && (
        <div className="gf-groups-directory__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={() => fetchGroups(search, statusFilter)}>
            Retry
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="gf-groups-directory__toolbar">
        <div className="gf-groups-directory__search-wrapper">
          <svg className="gf-groups-directory__search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="9" cy="9" r="6" />
            <line x1="13.5" y1="13.5" x2="18" y2="18" />
          </svg>
          <input
            type="search"
            placeholder="Search by cohort name, join code, or mentor..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="gf-groups-directory__search-input"
            aria-label="Search cohorts"
          />
        </div>

        <div className="gf-groups-directory__filters">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="gf-groups-directory__select"
            aria-label="Filter by status"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>
      </div>

      {/* Directory Content */}
      {loading ? (
        <Card className="gf-groups-directory__card">
          <div className="gf-groups-directory__skeleton-wrap">
            <Skeleton height="40px" className="gf-mb-3" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" />
          </div>
        </Card>
      ) : groups.length === 0 ? (
        <EmptyState
          title="No cohorts found"
          description={
            search || statusFilter !== 'ALL'
              ? 'No groups match your current filter criteria.'
              : 'There are currently no cohorts registered on the platform.'
          }
        />
      ) : (
        <Card className="gf-groups-directory__card">
          <div className="gf-groups-directory__table-responsive">
            <table className="gf-groups-directory__table">
              <thead>
                <tr>
                  <th scope="col">Cohort Name</th>
                  <th scope="col">Join Code</th>
                  <th scope="col">Supervising Mentor</th>
                  <th scope="col">Enrolled Students</th>
                  <th scope="col">Projects</th>
                  <th scope="col">Status</th>
                  <th scope="col">Created Date</th>
                  <th scope="col"><span className="gf-sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {groups.map((group) => (
                  <tr key={group.id}>
                    <td>
                      <div className="gf-groups-directory__group-name-cell">
                        <Link
                          to={`/admin/groups/${group.id}`}
                          className="gf-groups-directory__group-link"
                        >
                          {group.name}
                        </Link>
                      </div>
                    </td>
                    <td>
                      <code className="gf-groups-directory__join-code">{group.join_code}</code>
                    </td>
                    <td>
                      <div className="gf-groups-directory__mentor-cell">
                        <span className="gf-groups-directory__mentor-name">{group.mentor_name}</span>
                        <span className="gf-groups-directory__mentor-email">{group.mentor_email}</span>
                      </div>
                    </td>
                    <td>
                      <span className="gf-groups-directory__count-badge">
                        {group.student_count} student{group.student_count === 1 ? '' : 's'}
                      </span>
                    </td>
                    <td>
                      <span className="gf-groups-directory__count-badge">
                        {group.project_count} project{group.project_count === 1 ? '' : 's'}
                      </span>
                    </td>
                    <td>{getStatusBadge(group.status)}</td>
                    <td>
                      <span className="gf-groups-directory__date">
                        {group.created_at ? new Date(group.created_at).toLocaleDateString() : 'N/A'}
                      </span>
                    </td>
                    <td className="gf-groups-directory__actions">
                      <Button
                        as="link"
                        to={`/admin/groups/${group.id}`}
                        variant="secondary"
                        size="sm"
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
