import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminMentors } from '@/lib/api/client';
import type { AdminMentorSummary } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorDirectory.css';

/**
 * AD02 — Mentor Directory
 *
 * Governance view for all registered platform mentors, their organizations,
 * account statuses, and cohort assignment volumes.
 */
export function MentorDirectory() {
  const [mentors, setMentors] = useState<AdminMentorSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [, startTransition] = useTransition();

  const fetchMentors = async (s: string, st: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminMentors({
        search: s.trim() || undefined,
        status: st || undefined,
      });
      setMentors(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve mentor directory.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMentors(search, statusFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    startTransition(() => {
      fetchMentors(val, statusFilter);
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return <Badge variant="success">Active</Badge>;
      case 'SUSPENDED':
        return <Badge variant="danger">Suspended</Badge>;
      case 'INACTIVE':
        return <Badge variant="neutral">Inactive</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="gf-mentor-directory">
      <PageHeader
        eyebrow="PEOPLE GOVERNANCE"
        title="Mentor Directory"
        description="Inspect registered mentors, organizational affiliations, and supervised cohort metrics."
      />

      {error && (
        <div className="gf-mentor-directory__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={() => fetchMentors(search, statusFilter)}>
            Retry
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="gf-mentor-directory__toolbar">
        <div className="gf-mentor-directory__search-wrapper">
          <svg className="gf-mentor-directory__search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="9" cy="9" r="6" />
            <line x1="13.5" y1="13.5" x2="18" y2="18" />
          </svg>
          <input
            type="search"
            placeholder="Search by mentor name, email, or specialization..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="gf-mentor-directory__search-input"
            aria-label="Search mentors"
          />
        </div>

        <div className="gf-mentor-directory__filters">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="gf-mentor-directory__select"
            aria-label="Filter by account status"
          >
            <option value="">All Account Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="SUSPENDED">Suspended</option>
          </select>
        </div>
      </div>

      {/* Mentors Data Table / Cards */}
      <div className="gf-mentor-directory__content">
        {loading ? (
          <div className="gf-mentor-directory__skeleton-stack">
            <Skeleton height="72px" />
            <Skeleton height="72px" />
            <Skeleton height="72px" />
            <Skeleton height="72px" />
          </div>
        ) : mentors.length === 0 ? (
          <EmptyState
            title="No mentors found"
            description={
              search || statusFilter
                ? 'No mentors match the active search or filter criteria.'
                : 'No mentors have been registered on the platform yet.'
            }
            action={
              (search || statusFilter) && (
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSearch('');
                    setStatusFilter('');
                    fetchMentors('', '');
                  }}
                >
                  Clear Filters
                </Button>
              )
            }
          />
        ) : (
          <Card className="gf-mentor-directory__card">
            <div className="gf-mentor-directory__table-responsive">
              <table className="gf-mentor-directory__table">
                <thead>
                  <tr>
                    <th scope="col">Mentor</th>
                    <th scope="col">Affiliation</th>
                    <th scope="col">Specialization</th>
                    <th scope="col">Status</th>
                    <th scope="col">Cohorts</th>
                    <th scope="col">Students</th>
                    <th scope="col" className="gf-mentor-directory__th-actions">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {mentors.map((m) => (
                    <tr key={m.id} className="gf-mentor-directory__row">
                      <td className="gf-mentor-directory__cell-user">
                        <div className="gf-mentor-directory__avatar">
                          {m.full_name?.slice(0, 2).toUpperCase() || 'ME'}
                        </div>
                        <div className="gf-mentor-directory__user-meta">
                          <span className="gf-mentor-directory__user-name">{m.full_name}</span>
                          <span className="gf-mentor-directory__user-email">{m.email}</span>
                        </div>
                      </td>
                      <td>
                        <div className="gf-mentor-directory__affiliation">
                          <span>{m.designation || 'Mentor'}</span>
                          {m.organization && (
                            <span className="gf-mentor-directory__org">{m.organization}</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className="gf-mentor-directory__specialization">
                          {m.specialization || 'General Engineering'}
                        </span>
                      </td>
                      <td>{getStatusBadge(m.status)}</td>
                      <td>
                        <span className="gf-mentor-directory__stat-pill">
                          {m.group_count} cohorts
                        </span>
                      </td>
                      <td>
                        <span className="gf-mentor-directory__stat-pill">
                          {m.student_count} students
                        </span>
                      </td>
                      <td className="gf-mentor-directory__cell-actions">
                        <Link
                          to={`/admin/mentors/${m.id}`}
                          className="gf-mentor-directory__action-link"
                          aria-label={`View governance details for ${m.full_name}`}
                        >
                          View Detail →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
