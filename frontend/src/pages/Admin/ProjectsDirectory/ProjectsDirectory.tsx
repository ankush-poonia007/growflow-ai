import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminProjects } from '@/lib/api/client';
import type { AdminProjectSummary } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './ProjectsDirectory.css';

/**
 * AD08 — Projects Directory
 *
 * Governance directory of platform student project instances.
 * Navigates to the canonical project instance monitoring detail route /admin/instances/:projectId.
 */
export function ProjectsDirectory() {
  const [projects, setProjects] = useState<AdminProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [phaseFilter, setPhaseFilter] = useState('ALL');
  const [healthFilter, setHealthFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [, startTransition] = useTransition();

  const fetchProjects = async (s: string, ph: string, hl: string, st: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminProjects({
        search: s.trim() || undefined,
        phase: ph !== 'ALL' ? ph : undefined,
        health: hl !== 'ALL' ? hl : undefined,
        status: st !== 'ALL' ? st : undefined,
      });
      setProjects(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve projects directory.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects(search, phaseFilter, healthFilter, statusFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phaseFilter, healthFilter, statusFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    startTransition(() => {
      fetchProjects(val, phaseFilter, healthFilter, statusFilter);
    });
  };

  const getHealthBadge = (health?: string | null) => {
    switch (health?.toUpperCase()) {
      case 'HEALTHY':
        return <Badge variant="success">Healthy</Badge>;
      case 'WARNING':
      case 'NEEDS_ATTENTION':
        return <Badge variant="warning">Warning</Badge>;
      case 'CRITICAL':
      case 'AT_RISK':
        return <Badge variant="danger">Critical</Badge>;
      default:
        return <Badge variant="neutral">{health ?? 'UNKNOWN'}</Badge>;
    }
  };

  return (
    <div className="gf-projects-directory">
      <PageHeader
        eyebrow="RESOURCE GOVERNANCE"
        title="Projects Directory"
        description="Inspect student project instances across all platform cohorts with lifecycle progression and operational health."
      />

      {error && (
        <div className="gf-projects-directory__alert" role="alert">
          <span>{error}</span>
          <Button
            variant="tertiary"
            size="sm"
            onClick={() => fetchProjects(search, phaseFilter, healthFilter, statusFilter)}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Toolbar & Filter Controls */}
      <div className="gf-projects-directory__toolbar">
        <div className="gf-projects-directory__search-wrapper">
          <svg className="gf-projects-directory__search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="9" cy="9" r="6" />
            <line x1="13.5" y1="13.5" x2="18" y2="18" />
          </svg>
          <input
            type="search"
            placeholder="Search by project name, student, mentor, or cohort..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="gf-projects-directory__search-input"
            aria-label="Search projects"
          />
        </div>

        <div className="gf-projects-directory__filters">
          <select
            value={phaseFilter}
            onChange={(e) => setPhaseFilter(e.target.value)}
            className="gf-projects-directory__select"
            aria-label="Filter by lifecycle phase"
          >
            <option value="ALL">All Phases</option>
            <option value="IDEA">Idea</option>
            <option value="ASSESSMENT">Assessment</option>
            <option value="DRAFTING">Drafting</option>
            <option value="ARCHITECTURE">Architecture</option>
            <option value="IMPLEMENTATION">Implementation</option>
            <option value="TESTING">Testing</option>
            <option value="DEPLOYMENT">Deployment</option>
            <option value="EVALUATION">Evaluation</option>
            <option value="COMPLETION">Completion</option>
          </select>

          <select
            value={healthFilter}
            onChange={(e) => setHealthFilter(e.target.value)}
            className="gf-projects-directory__select"
            aria-label="Filter by health"
          >
            <option value="ALL">All Health</option>
            <option value="HEALTHY">Healthy</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="gf-projects-directory__select"
            aria-label="Filter by status"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="COMPLETED">Completed</option>
            <option value="PAUSED">Paused</option>
          </select>
        </div>
      </div>

      {/* Projects Table */}
      {loading ? (
        <Card className="gf-projects-directory__card">
          <div className="gf-projects-directory__skeleton-wrap">
            <Skeleton height="40px" className="gf-mb-3" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" />
          </div>
        </Card>
      ) : projects.length === 0 ? (
        <EmptyState
          title="No projects found"
          description={
            search || phaseFilter !== 'ALL' || healthFilter !== 'ALL' || statusFilter !== 'ALL'
              ? 'No project instances match your current filter parameters.'
              : 'There are currently no student project instances registered on the platform.'
          }
        />
      ) : (
        <Card className="gf-projects-directory__card">
          <div className="gf-projects-directory__table-responsive">
            <table className="gf-projects-directory__table">
              <thead>
                <tr>
                  <th scope="col">Project Instance</th>
                  <th scope="col">Student Owner</th>
                  <th scope="col">Cohort / Supervisor</th>
                  <th scope="col">Lifecycle Phase</th>
                  <th scope="col">Health</th>
                  <th scope="col">Progress</th>
                  <th scope="col">Status</th>
                  <th scope="col">Updated</th>
                  <th scope="col"><span className="gf-sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {projects.map((proj) => (
                  <tr key={proj.id}>
                    <td>
                      <div className="gf-projects-directory__title-cell">
                        <Link
                          to={`/admin/instances/${proj.id}`}
                          className="gf-projects-directory__title-link"
                        >
                          {proj.name}
                        </Link>
                        {proj.source_definition_name && (
                          <span className="gf-projects-directory__def-pill" title="Source Template">
                            Template: {proj.source_definition_name}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="gf-projects-directory__student-cell">
                        <Link
                          to={`/admin/students/${proj.student_id}`}
                          className="gf-projects-directory__sub-link"
                        >
                          {proj.student_name}
                        </Link>
                        <span className="gf-projects-directory__email">{proj.student_email}</span>
                      </div>
                    </td>
                    <td>
                      <div className="gf-projects-directory__cohort-cell">
                        {proj.group_id ? (
                          <Link
                            to={`/admin/groups/${proj.group_id}`}
                            className="gf-projects-directory__sub-link"
                          >
                            {proj.group_name || 'Cohort'}
                          </Link>
                        ) : (
                          <span className="gf-projects-directory__muted">Independent</span>
                        )}
                        {proj.mentor_name && (
                          <span className="gf-projects-directory__mentor-sub">
                            Mentor: {proj.mentor_name}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="gf-projects-directory__phase-badge">
                        {proj.current_phase.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>{getHealthBadge(proj.health)}</td>
                    <td>
                      <div className="gf-projects-directory__progress-wrap">
                        <div
                          className="gf-projects-directory__progress-bar"
                          style={{ width: `${Math.min(100, Math.max(0, proj.progress_percentage))}%` }}
                        />
                        <span className="gf-projects-directory__progress-val">{proj.progress_percentage}%</span>
                      </div>
                    </td>
                    <td>
                      <Badge variant={proj.status === 'ACTIVE' ? 'success' : 'neutral'}>
                        {proj.status}
                      </Badge>
                    </td>
                    <td>
                      <span className="gf-projects-directory__date">
                        {proj.updated_at ? new Date(proj.updated_at).toLocaleDateString() : 'N/A'}
                      </span>
                    </td>
                    <td className="gf-projects-directory__actions">
                      <Button
                        as="link"
                        to={`/admin/instances/${proj.id}`}
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
