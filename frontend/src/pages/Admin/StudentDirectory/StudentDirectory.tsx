import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminStudents } from '@/lib/api/client';
import type { AdminStudentSummary } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './StudentDirectory.css';

/**
 * AD04 — Student Directory
 *
 * Governance view for all enrolled students across the platform, including
 * learning track distribution and active project health counts.
 */
export function StudentDirectory() {
  const [students, setStudents] = useState<AdminStudentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [trackFilter, setTrackFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [, startTransition] = useTransition();

  const fetchStudents = async (s: string, trk: string, st: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminStudents({
        search: s.trim() || undefined,
        track: trk || undefined,
        status: st || undefined,
      });
      setStudents(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve student directory.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents(search, trackFilter, statusFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trackFilter, statusFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    startTransition(() => {
      fetchStudents(val, trackFilter, statusFilter);
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
    <div className="gf-student-directory">
      <PageHeader
        eyebrow="PEOPLE GOVERNANCE"
        title="Student Directory"
        description="Inspect enrolled students, institutional affiliations, learning tracks, and project progress."
      />

      {error && (
        <div className="gf-student-directory__alert" role="alert">
          <span>{error}</span>
          <Button
            variant="tertiary"
            size="sm"
            onClick={() => fetchStudents(search, trackFilter, statusFilter)}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="gf-student-directory__toolbar">
        <div className="gf-student-directory__search-wrapper">
          <svg className="gf-student-directory__search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="9" cy="9" r="6" />
            <line x1="13.5" y1="13.5" x2="18" y2="18" />
          </svg>
          <input
            type="search"
            placeholder="Search by student name, email, college, or branch..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="gf-student-directory__search-input"
            aria-label="Search students"
          />
        </div>

        <div className="gf-student-directory__filters">
          <select
            value={trackFilter}
            onChange={(e) => setTrackFilter(e.target.value)}
            className="gf-student-directory__select"
            aria-label="Filter by learning track"
          >
            <option value="">All Learning Tracks</option>
            <option value="Full-Stack Web Development">Full-Stack Development</option>
            <option value="Artificial Intelligence / Machine Learning">AI / Machine Learning</option>
            <option value="Cloud Architecture">Cloud Architecture</option>
            <option value="Data Engineering">Data Engineering</option>
            <option value="Mobile Development">Mobile Development</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="gf-student-directory__select"
            aria-label="Filter by account status"
          >
            <option value="">All Account Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="SUSPENDED">Suspended</option>
          </select>
        </div>
      </div>

      {/* Students Data Table / Cards */}
      <div className="gf-student-directory__content">
        {loading ? (
          <div className="gf-student-directory__skeleton-stack">
            <Skeleton height="72px" />
            <Skeleton height="72px" />
            <Skeleton height="72px" />
            <Skeleton height="72px" />
          </div>
        ) : students.length === 0 ? (
          <EmptyState
            title="No students found"
            description={
              search || trackFilter || statusFilter
                ? 'No students match the active search or filter criteria.'
                : 'No students have been enrolled on the platform yet.'
            }
            action={
              (search || trackFilter || statusFilter) && (
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSearch('');
                    setTrackFilter('');
                    setStatusFilter('');
                    fetchStudents('', '', '');
                  }}
                >
                  Clear Filters
                </Button>
              )
            }
          />
        ) : (
          <Card className="gf-student-directory__card">
            <div className="gf-student-directory__table-responsive">
              <table className="gf-student-directory__table">
                <thead>
                  <tr>
                    <th scope="col">Student</th>
                    <th scope="col">Institution</th>
                    <th scope="col">Learning Track</th>
                    <th scope="col">Status</th>
                    <th scope="col">Cohorts</th>
                    <th scope="col">Projects</th>
                    <th scope="col" className="gf-student-directory__th-actions">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s) => (
                    <tr key={s.id} className="gf-student-directory__row">
                      <td className="gf-student-directory__cell-user">
                        <div className="gf-student-directory__avatar">
                          {s.full_name?.slice(0, 2).toUpperCase() || 'ST'}
                        </div>
                        <div className="gf-student-directory__user-meta">
                          <span className="gf-student-directory__user-name">{s.full_name}</span>
                          <span className="gf-student-directory__user-email">{s.email}</span>
                        </div>
                      </td>
                      <td>
                        <div className="gf-student-directory__institution">
                          <span>{s.college || 'College not provided'}</span>
                          {s.branch && (
                            <span className="gf-student-directory__branch">{s.branch}</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="gf-student-directory__track">
                          <span>{s.primary_track || 'General Track'}</span>
                          {s.year_of_study && (
                            <span className="gf-student-directory__year">Year {s.year_of_study}</span>
                          )}
                        </div>
                      </td>
                      <td>{getStatusBadge(s.status)}</td>
                      <td>
                        <span className="gf-student-directory__stat-pill">
                          {s.group_count} cohorts
                        </span>
                      </td>
                      <td>
                        <div className="gf-student-directory__project-badges">
                          <span className="gf-student-directory__stat-pill">
                            {s.active_project_count} active
                          </span>
                          {s.at_risk_project_count > 0 && (
                            <span className="gf-student-directory__risk-badge">
                              {s.at_risk_project_count} at risk
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="gf-student-directory__cell-actions">
                        <Link
                          to={`/admin/students/${s.id}`}
                          className="gf-student-directory__action-link"
                          aria-label={`View governance details for ${s.full_name}`}
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
