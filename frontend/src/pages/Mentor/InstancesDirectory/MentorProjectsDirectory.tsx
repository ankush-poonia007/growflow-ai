import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router';
import { getMentorProjects, getMentorGroups } from '@/lib/api/client';
import type { MentorProjectInstanceSummary, GroupResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './MentorProjectsDirectory.css';

export function MentorProjectsDirectory() {
  const [projects, setProjects] = useState<MentorProjectInstanceSummary[]>([]);
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [phaseFilter, setPhaseFilter] = useState('');
  const [healthFilter, setHealthFilter] = useState('');
  const [groupFilter, setGroupFilter] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [projsData, groupsData] = await Promise.all([
        getMentorProjects({
          search: search.trim() || undefined,
          phase: phaseFilter || undefined,
          health: healthFilter || undefined,
          group_id: groupFilter || undefined,
        }),
        getMentorGroups(),
      ]);
      setProjects(projsData);
      setGroups(groupsData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve project instances.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [search, phaseFilter, healthFilter, groupFilter]);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadData();
    }, 200);
    return () => {
      clearTimeout(timer);
    };
  }, [loadData]);

  const getHealthBadge = (health: string) => {
    switch (health) {
      case 'CRITICAL':
        return <Badge variant="danger">CRITICAL</Badge>;
      case 'WARNING':
        return <Badge variant="warning">WARNING</Badge>;
      case 'HEALTHY':
      default:
        return <Badge variant="success">HEALTHY</Badge>;
    }
  };

  return (
    <div className="gf-mentor-projects-dir" id="mentor-projects-instances-directory">
      <PageHeader
        eyebrow="SUPERVISE DIRECTORY"
        title="Student Project Instances"
        description="Cross-cohort directory of all supervised student project instances. Read-only supervision view."
      />

      <div className="gf-mentor-projects-dir__filters">
        <div className="gf-mentor-projects-dir__search">
          <Input
            id="projects-search-input"
            type="search"
            placeholder="Search by project name or student..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          id="projects-phase-filter"
          className="gf-mentor-projects-dir__select"
          value={phaseFilter}
          onChange={(e) => setPhaseFilter(e.target.value)}
        >
          <option value="">All Phases</option>
          <option value="IDEA">Idea</option>
          <option value="ASSESSMENT">Assessment</option>
          <option value="BLUEPRINT">Blueprint</option>
          <option value="PLANNING">Planning</option>
          <option value="IMPLEMENTATION">Implementation</option>
          <option value="TESTING">Testing</option>
          <option value="DEPLOYMENT">Deployment</option>
          <option value="COMPLETED">Completed</option>
        </select>

        <select
          id="projects-health-filter"
          className="gf-mentor-projects-dir__select"
          value={healthFilter}
          onChange={(e) => setHealthFilter(e.target.value)}
        >
          <option value="">All Health</option>
          <option value="HEALTHY">Healthy</option>
          <option value="WARNING">Warning</option>
          <option value="CRITICAL">Critical</option>
        </select>

        <select
          id="projects-group-filter"
          className="gf-mentor-projects-dir__select"
          value={groupFilter}
          onChange={(e) => setGroupFilter(e.target.value)}
        >
          <option value="">All Cohorts</option>
          {groups.map((grp) => (
            <option key={grp.id} value={grp.id}>
              {grp.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadData} />
        </div>
      )}

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} width="100%" height="56px" style={{ borderRadius: '8px' }} />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          title="No project instances found"
          description={
            search || phaseFilter || healthFilter || groupFilter
              ? 'No project instances matched your filter criteria.'
              : 'No student project instances are currently supervised under your account.'
          }
        />
      ) : (
        <div className="gf-mentor-projects-dir__table-wrapper">
          <table className="gf-mentor-projects-dir__table" id="projects-instances-table">
            <thead>
              <tr>
                <th>Project Name</th>
                <th>Student</th>
                <th>Cohort</th>
                <th>Phase</th>
                <th>Health</th>
                <th>Progress</th>
                <th>Template / Version</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id} id={`project-row-${p.id}`}>
                  <td>
                    <Link
                      to={`/mentor/project-instances/${p.id}`}
                      className="gf-mentor-projects-dir__proj-link"
                      id={`project-link-${p.id}`}
                    >
                      {p.name}
                    </Link>
                  </td>
                  <td>
                    <div>{p.student_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--gf-text-secondary)' }}>
                      {p.student_email}
                    </div>
                  </td>
                  <td>{p.group_name || '—'}</td>
                  <td>
                    <Badge variant="neutral">{p.current_phase}</Badge>
                  </td>
                  <td>{getHealthBadge(p.health)}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.8125rem' }}>{p.progress_percentage}%</span>
                      <div
                        style={{
                          width: '60px',
                          height: '5px',
                          background: 'var(--gf-color-secondary, #F2F2EE)',
                          border: '1px solid var(--gf-color-border-subtle, #E5E5DF)',
                          borderRadius: '3px',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            width: `${p.progress_percentage}%`,
                            height: '100%',
                            background: 'var(--gf-color-accent, #6F7F63)',
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td>
                    {p.source_definition_name ? (
                      <span style={{ fontSize: '0.8125rem' }}>
                        {p.source_definition_name}{' '}
                        <strong>v{p.source_definition_version_number ?? 1}</strong>
                      </span>
                    ) : (
                      <span style={{ color: 'var(--gf-text-secondary)', fontSize: '0.8125rem' }}>
                        Custom Project
                      </span>
                    )}
                  </td>
                  <td>
                    <Button
                      as="link"
                      to={`/mentor/project-instances/${p.id}`}
                      variant="secondary"
                      size="sm"
                      id={`inspect-btn-${p.id}`}
                    >
                      Inspect
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
export default MentorProjectsDirectory;
