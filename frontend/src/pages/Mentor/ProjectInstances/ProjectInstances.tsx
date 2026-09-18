import { useEffect, useState, useCallback } from 'react';
import { getMentorProjectInstances, getMentorGroups } from '@/lib/api/client';
import type { MentorProjectInstanceSummary, GroupResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './ProjectInstances.css';

export function ProjectInstances() {
  const [projects, setProjects] = useState<MentorProjectInstanceSummary[]>([]);
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [phaseFilter, setPhaseFilter] = useState('');
  const [healthFilter, setHealthFilter] = useState('');
  const [groupFilter, setGroupFilter] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [projsData, groupsData] = await Promise.all([
        getMentorProjectInstances({
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

  const healthyCount = projects.filter((p) => p.health === 'HEALTHY').length;
  const warningCount = projects.filter((p) => p.health === 'WARNING').length;
  const criticalCount = projects.filter((p) => p.health === 'CRITICAL').length;

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
    <div className="gf-project-instances-page" id="mentor-project-instances-page">
      <PageHeader
        eyebrow="SUPERVISE MONITORING"
        title="Project Instances Supervision"
        description="Live operational monitoring of all supervised student project instances. Track phase distribution, health conditions, and progress."
      />

      <div className="gf-project-instances-page__metrics">
        <div className="gf-project-instances-page__metric-card" id="metric-total-instances">
          <span className="gf-project-instances-page__metric-title">Total Monitored</span>
          <span className="gf-project-instances-page__metric-val">{projects.length}</span>
        </div>
        <div className="gf-project-instances-page__metric-card" id="metric-healthy-instances">
          <span className="gf-project-instances-page__metric-title">Healthy</span>
          <span className="gf-project-instances-page__metric-val gf-project-instances-page__metric-val--healthy">
            {healthyCount}
          </span>
        </div>
        <div className="gf-project-instances-page__metric-card" id="metric-warning-instances">
          <span className="gf-project-instances-page__metric-title">Warning</span>
          <span className="gf-project-instances-page__metric-val gf-project-instances-page__metric-val--warning">
            {warningCount}
          </span>
        </div>
        <div className="gf-project-instances-page__metric-card" id="metric-critical-instances">
          <span className="gf-project-instances-page__metric-title">Critical</span>
          <span className="gf-project-instances-page__metric-val gf-project-instances-page__metric-val--critical">
            {criticalCount}
          </span>
        </div>
      </div>

      <div className="gf-project-instances-page__filters">
        <div className="gf-project-instances-page__search">
          <Input
            id="instances-search-input"
            type="search"
            placeholder="Search by project name or student..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          id="instances-phase-filter"
          className="gf-project-instances-page__select"
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
          id="instances-health-filter"
          className="gf-project-instances-page__select"
          value={healthFilter}
          onChange={(e) => setHealthFilter(e.target.value)}
        >
          <option value="">All Health</option>
          <option value="HEALTHY">Healthy</option>
          <option value="WARNING">Warning</option>
          <option value="CRITICAL">Critical</option>
        </select>

        <select
          id="instances-group-filter"
          className="gf-project-instances-page__select"
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
        <div className="gf-project-instances-page__grid">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="gf-monitoring-card">
              <Skeleton width="60%" height="22px" />
              <Skeleton width="40%" height="16px" />
              <Skeleton width="100%" height="32px" />
              <Skeleton width="100%" height="36px" />
            </div>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          title="No project instances"
          description={
            search || phaseFilter || healthFilter || groupFilter
              ? 'No project instances matched your filters.'
              : 'There are no student project instances under your supervision.'
          }
        />
      ) : (
        <div className="gf-project-instances-page__grid" id="project-instances-grid">
          {projects.map((proj) => {
            const cardHealthClass =
              proj.health === 'CRITICAL'
                ? 'gf-monitoring-card--critical'
                : proj.health === 'WARNING'
                ? 'gf-monitoring-card--warning'
                : 'gf-monitoring-card--healthy';

            const barFillClass =
              proj.health === 'CRITICAL'
                ? 'gf-monitoring-card__bar-fill--critical'
                : proj.health === 'WARNING'
                ? 'gf-monitoring-card__bar-fill--warning'
                : '';

            return (
              <div
                key={proj.id}
                className={`gf-monitoring-card ${cardHealthClass}`}
                id={`monitoring-card-${proj.id}`}
              >
                <div className="gf-monitoring-card__header">
                  <div>
                    <span className="gf-monitoring-card__title">{proj.name}</span>
                    <div className="gf-monitoring-card__student">
                      {proj.student_name} ({proj.student_email})
                    </div>
                  </div>
                  {getHealthBadge(proj.health)}
                </div>

                <div className="gf-monitoring-card__badges">
                  <Badge variant="neutral">{proj.current_phase}</Badge>
                  {proj.group_name && <Badge variant="neutral">{proj.group_name}</Badge>}
                  {proj.source_definition_name && (
                    <Badge variant="accent">
                      {proj.source_definition_name} v{proj.source_definition_version_number ?? 1}
                    </Badge>
                  )}
                </div>

                <div className="gf-monitoring-card__progress">
                  <div className="gf-monitoring-card__progress-label">
                    <span>Progress</span>
                    <strong>{proj.progress_percentage}%</strong>
                  </div>
                  <div className="gf-monitoring-card__bar-track">
                    <div
                      className={`gf-monitoring-card__bar-fill ${barFillClass}`}
                      style={{ width: `${proj.progress_percentage}%` }}
                    />
                  </div>
                </div>

                <div style={{ marginTop: 'auto', paddingTop: '0.5rem' }}>
                  <Button
                    as="link"
                    to={`/mentor/project-instances/${proj.id}`}
                    variant="secondary"
                    size="sm"
                    id={`view-instance-${proj.id}`}
                    style={{ width: '100%', textAlign: 'center' }}
                  >
                    Inspect Project Instance →
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
export default ProjectInstances;
