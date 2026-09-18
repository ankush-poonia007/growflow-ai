import { useEffect, useState, useCallback, useMemo } from 'react';
import { getMentorAtRiskProjects, getMentorGroups } from '@/lib/api/client';
import type { MentorProjectInstanceSummary, GroupResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './AtRiskDirectory.css';

export function AtRiskDirectory() {
  const [projects, setProjects] = useState<MentorProjectInstanceSummary[]>([]);
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [groupFilter, setGroupFilter] = useState('');

  const loadAtRisk = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [data, groupsData] = await Promise.all([
        getMentorAtRiskProjects({
          group_id: groupFilter || undefined,
        }),
        getMentorGroups(),
      ]);
      setProjects(data);
      setGroups(groupsData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve at-risk projects.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [groupFilter]);

  useEffect(() => {
    void loadAtRisk();
  }, [loadAtRisk]);

  const filteredProjects = useMemo(() => {
    if (!search.trim()) return projects;
    const term = search.trim().toLowerCase();
    return projects.filter(
      (p) =>
        p.name.toLowerCase().includes(term) ||
        p.student_name.toLowerCase().includes(term) ||
        p.student_email.toLowerCase().includes(term),
    );
  }, [projects, search]);

  const criticalCount = filteredProjects.filter((p) => p.health === 'CRITICAL').length;
  const warningCount = filteredProjects.filter((p) => p.health === 'WARNING').length;

  return (
    <div className="gf-at-risk-directory" id="mentor-at-risk-directory">
      <PageHeader
        eyebrow="SUPERVISE TRIAGE"
        title="Global At-Risk Projects"
        description="High-priority triage directory showing project instances in WARNING or CRITICAL state across your supervised cohorts."
      />

      <div className="gf-at-risk-directory__stats">
        <div className="gf-at-risk-directory__stat-card" id="stat-total-at-risk">
          <span className="gf-at-risk-directory__stat-label">Total At-Risk</span>
          <span className="gf-at-risk-directory__stat-val">{filteredProjects.length}</span>
        </div>
        <div className="gf-at-risk-directory__stat-card" id="stat-critical">
          <span className="gf-at-risk-directory__stat-label">Critical Standing</span>
          <span className="gf-at-risk-directory__stat-val gf-at-risk-directory__stat-val--critical">
            {criticalCount}
          </span>
        </div>
        <div className="gf-at-risk-directory__stat-card" id="stat-warning">
          <span className="gf-at-risk-directory__stat-label">Warning Standing</span>
          <span className="gf-at-risk-directory__stat-val gf-at-risk-directory__stat-val--warning">
            {warningCount}
          </span>
        </div>
      </div>

      <div className="gf-at-risk-directory__filters">
        <div className="gf-at-risk-directory__search">
          <Input
            id="at-risk-search-input"
            type="search"
            placeholder="Search by project name or student..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          id="at-risk-group-filter"
          className="gf-at-risk-directory__select"
          value={groupFilter}
          onChange={(e) => setGroupFilter(e.target.value)}
        >
          <option value="">All Supervised Cohorts</option>
          {groups.map((grp) => (
            <option key={grp.id} value={grp.id}>
              {grp.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadAtRisk} />
        </div>
      )}

      {loading ? (
        <div className="gf-at-risk-directory__grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="gf-at-risk-card">
              <Skeleton width="60%" height="22px" />
              <Skeleton width="40%" height="16px" />
              <Skeleton width="100%" height="32px" />
              <Skeleton width="100%" height="36px" />
            </div>
          ))}
        </div>
      ) : filteredProjects.length === 0 ? (
        <EmptyState
          title="No projects at risk"
          description={
            search || groupFilter
              ? 'No at-risk projects matched your search criteria.'
              : 'All supervised projects across your cohorts are currently in HEALTHY standing.'
          }
        />
      ) : (
        <div className="gf-at-risk-directory__grid" id="at-risk-grid">
          {filteredProjects.map((proj) => {
            const isCritical = proj.health === 'CRITICAL';
            const cardClass = isCritical
              ? 'gf-at-risk-card--critical'
              : 'gf-at-risk-card--warning';

            return (
              <div
                key={proj.id}
                className={`gf-at-risk-card ${cardClass}`}
                id={`at-risk-card-${proj.id}`}
              >
                <div className="gf-at-risk-card__header">
                  <div>
                    <span className="gf-at-risk-card__title">{proj.name}</span>
                    <div className="gf-at-risk-card__student">
                      {proj.student_name} ({proj.student_email})
                    </div>
                  </div>
                  <Badge variant={isCritical ? 'danger' : 'warning'}>
                    {proj.health}
                  </Badge>
                </div>

                <div className="gf-at-risk-card__meta">
                  <Badge variant="neutral">Phase: {proj.current_phase}</Badge>
                  {proj.group_name && <Badge variant="neutral">{proj.group_name}</Badge>}
                  {proj.source_definition_name && (
                    <Badge variant="accent">
                      {proj.source_definition_name} v{proj.source_definition_version_number ?? 1}
                    </Badge>
                  )}
                </div>

                <div className="gf-at-risk-card__progress">
                  <div className="gf-at-risk-card__progress-label">
                    <span>Progress Lag</span>
                    <strong>{proj.progress_percentage}%</strong>
                  </div>
                  <div className="gf-at-risk-card__bar-track">
                    <div
                      className={
                        isCritical
                          ? 'gf-at-risk-card__bar-fill--critical'
                          : 'gf-at-risk-card__bar-fill--warning'
                      }
                      style={{ width: `${proj.progress_percentage}%` }}
                    />
                  </div>
                </div>

                <div style={{ marginTop: 'auto', paddingTop: '0.5rem' }}>
                  <Button
                    as="link"
                    to={`/mentor/at-risk/${proj.id}`}
                    variant="secondary"
                    size="sm"
                    id={`inspect-at-risk-${proj.id}`}
                    style={{ width: '100%', textAlign: 'center' }}
                  >
                    Inspect At-Risk Detail →
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
export default AtRiskDirectory;
