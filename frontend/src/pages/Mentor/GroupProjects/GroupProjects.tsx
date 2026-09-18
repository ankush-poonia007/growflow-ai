import { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorGroup, getGroupProjects } from '@/lib/api/client';
import type { GroupResponse, ProjectResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupProjects.css';

export function GroupProjects() {
  const { groupId } = useParams<{ groupId: string }>();
  const [group, setGroup] = useState<GroupResponse | null>(null);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [search, setSearch] = useState('');
  const [phaseFilter, setPhaseFilter] = useState('ALL');
  const [healthFilter, setHealthFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!groupId) return;
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [gRes, pRes] = await Promise.all([
          getMentorGroup(groupId!),
          getGroupProjects(groupId!),
        ]);
        if (mounted) {
          setGroup(gRes);
          setProjects(pRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to load group projects.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadData();
    return () => {
      mounted = false;
    };
  }, [groupId]);

  const filteredProjects = projects.filter((p) => {
    const q = search.toLowerCase().trim();
    const matchesSearch =
      !q ||
      p.name.toLowerCase().includes(q) ||
      (p.problem && p.problem.toLowerCase().includes(q));

    const matchesPhase = phaseFilter === 'ALL' || p.current_phase === phaseFilter;
    const matchesHealth = healthFilter === 'ALL' || p.health === healthFilter;

    return matchesSearch && matchesPhase && matchesHealth;
  });

  const getHealthVariant = (health: string): 'success' | 'accent' | 'warning' | 'danger' | 'neutral' => {
    switch (health) {
      case 'HEALTHY':
        return 'success';
      case 'ATTENTION':
        return 'accent';
      case 'WARNING':
      case 'AT_RISK':
        return 'warning';
      case 'CRITICAL':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  return (
    <div className="gf-group-projects">
      <PageHeader
        eyebrow="COHORT PROJECTS"
        title="Group Projects"
        description={`Student projects associated with ${group ? group.name : 'this group'}.`}
        breadcrumbs={[
          { label: 'Groups', to: '/mentor/groups' },
          {
            label: group?.name || 'Cohort',
            to: groupId ? `/mentor/groups/${groupId}` : undefined,
          },
          { label: 'Projects' },
        ]}
      />

      {error && (
        <div className="gf-group-projects__error" role="alert">
          {error}
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="gf-group-projects__toolbar">
        <div className="gf-group-projects__search">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search projects by name or problem..."
            aria-label="Filter cohort projects"
          />
        </div>

        <div className="gf-group-projects__filters">
          <label htmlFor="phase-filter-select" className="gf-group-projects__filter-label">
            Phase:
          </label>
          <select
            id="phase-filter-select"
            className="gf-group-projects__select"
            value={phaseFilter}
            onChange={(e) => setPhaseFilter(e.target.value)}
            aria-label="Filter by phase"
          >
            <option value="ALL">All Phases</option>
            <option value="IDEA">Idea</option>
            <option value="DISCOVERY">Discovery</option>
            <option value="ARCHITECTURE">Architecture</option>
            <option value="BLUEPRINT">Blueprint</option>
            <option value="IMPLEMENTATION">Implementation</option>
            <option value="REVIEW">Review</option>
            <option value="COMPLETE">Complete</option>
          </select>

          <label htmlFor="health-filter-select" className="gf-group-projects__filter-label">
            Health:
          </label>
          <select
            id="health-filter-select"
            className="gf-group-projects__select"
            value={healthFilter}
            onChange={(e) => setHealthFilter(e.target.value)}
            aria-label="Filter by health"
          >
            <option value="ALL">All Health</option>
            <option value="HEALTHY">Healthy</option>
            <option value="WARNING">Warning</option>
            <option value="ATTENTION">Attention</option>
            <option value="AT_RISK">At Risk</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="gf-group-projects__grid">
          <Skeleton height="160px" />
          <Skeleton height="160px" />
          <Skeleton height="160px" />
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          title="No Projects in Cohort"
          description="None of the enrolled students have created or linked projects to this group yet."
        />
      ) : filteredProjects.length === 0 ? (
        <EmptyState
          title="No Projects Match Filter"
          description="Adjust your search query or dropdown filters to view projects."
        />
      ) : (
        <div className="gf-group-projects__grid" role="feed" aria-label="Projects list">
          {filteredProjects.map((p) => (
            <Card key={p.id} className="gf-group-projects__card">
              <div className="gf-group-projects__card-header">
                <div className="gf-group-projects__card-title-wrap">
                  <h3 className="gf-group-projects__title">{p.name}</h3>
                  <div className="gf-group-projects__badges">
                    <Badge variant={getHealthVariant(p.health)}>
                      {p.health}
                    </Badge>
                    <Badge variant="neutral">
                      {p.current_phase}
                    </Badge>
                  </div>
                </div>
              </div>

              {p.problem && (
                <p className="gf-group-projects__problem-snippet">
                  {p.problem.length > 120 ? `${p.problem.slice(0, 120)}...` : p.problem}
                </p>
              )}

              <div className="gf-group-projects__progress-wrap">
                <div className="gf-group-projects__progress-header">
                  <span className="gf-group-projects__progress-label">Progress</span>
                  <span className="gf-group-projects__progress-val">{p.progress_percentage}%</span>
                </div>
                <div className="gf-group-projects__progress-bar">
                  <div
                    className="gf-group-projects__progress-fill"
                    style={{ width: `${Math.min(100, p.progress_percentage)}%` }}
                  />
                </div>
              </div>

              <div className="gf-group-projects__footer">
                <span className="gf-group-projects__meta">
                  Complexity: {p.complexity || 'INTERMEDIATE'}
                </span>
                {p.deadline && (
                  <span className="gf-group-projects__meta">
                    Target: {new Date(p.deadline).toLocaleDateString()}
                  </span>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
