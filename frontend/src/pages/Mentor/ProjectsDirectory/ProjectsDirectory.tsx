import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getMentorDefinitions } from '@/lib/api/client';
import type { ProjectDefinition } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './ProjectsDirectory.css';

export function ProjectsDirectory() {
  const [definitions, setDefinitions] = useState<ProjectDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [complexityFilter, setComplexityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  async function loadDefinitions() {
    try {
      setLoading(true);
      setError(null);
      const data = await getMentorDefinitions();
      setDefinitions(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load project definitions.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDefinitions();
  }, []);

  const filteredDefinitions = definitions.filter((def) => {
    const q = search.trim().toLowerCase();
    const matchesQuery =
      !q ||
      def.name.toLowerCase().includes(q) ||
      (def.current_version?.problem && def.current_version.problem.toLowerCase().includes(q)) ||
      (def.current_version?.description && def.current_version.description.toLowerCase().includes(q));

    const matchesComplexity =
      complexityFilter === 'ALL' ||
      def.current_version?.complexity?.toUpperCase() === complexityFilter;

    const matchesStatus =
      statusFilter === 'ALL' || def.status.toUpperCase() === statusFilter;

    return matchesQuery && matchesComplexity && matchesStatus;
  });

  const getComplexityVariant = (complexity?: string): 'neutral' | 'accent' | 'warning' => {
    switch (complexity?.toUpperCase()) {
      case 'BEGINNER':
        return 'neutral';
      case 'INTERMEDIATE':
        return 'accent';
      case 'ADVANCED':
        return 'warning';
      default:
        return 'neutral';
    }
  };

  const getStatusVariant = (status: string): 'success' | 'warning' | 'neutral' => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return 'success';
      case 'DRAFT':
        return 'warning';
      case 'ARCHIVED':
        return 'neutral';
      default:
        return 'neutral';
    }
  };

  return (
    <div className="gf-definitions-directory" role="main" aria-labelledby="page-title" aria-busy={loading ? 'true' : undefined}>
      <PageHeader
        eyebrow="SUPERVISE"
        title="Project Definitions"
        description="Author, version, and assign reusable project templates to supervised students."
        breadcrumbs={[{ label: 'Definitions' }]}
        action={
          <Button as="link" to="/mentor/projects/new" variant="primary" size="sm">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ marginRight: '6px' }}>
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Definition
          </Button>
        }
      />

      {error && (
        <div className="gf-definitions-directory__error" role="alert">
          <div className="gf-definitions-directory__error-text">
            <strong>Error:</strong> {error}
          </div>
          <Button variant="secondary" size="sm" onClick={loadDefinitions}>
            Retry
          </Button>
        </div>
      )}

      {/* Toolbar */}
      <div className="gf-definitions-directory__toolbar">
        <div className="gf-definitions-directory__search">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search definitions by name, problem, or scope..."
            aria-label="Filter project definitions"
          />
        </div>

        <div className="gf-definitions-directory__filters">
          <div className="gf-definitions-directory__filter-group">
            <label htmlFor="complexity-filter-select" className="gf-definitions-directory__filter-label">
              Complexity:
            </label>
            <select
              id="complexity-filter-select"
              className="gf-definitions-directory__select"
              value={complexityFilter}
              onChange={(e) => setComplexityFilter(e.target.value)}
              aria-label="Filter by complexity"
            >
              <option value="ALL">All Complexities</option>
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
            </select>
          </div>

          <div className="gf-definitions-directory__filter-group">
            <label htmlFor="status-filter-select" className="gf-definitions-directory__filter-label">
              Status:
            </label>
            <select
              id="status-filter-select"
              className="gf-definitions-directory__select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              aria-label="Filter by status"
            >
              <option value="ALL">All Statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="DRAFT">Draft</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="gf-definitions-directory__grid" aria-busy="true">
          <Skeleton height="180px" />
          <Skeleton height="180px" />
          <Skeleton height="180px" />
        </div>
      ) : filteredDefinitions.length === 0 ? (
        <EmptyState
          title={search || complexityFilter !== 'ALL' || statusFilter !== 'ALL' ? 'No matching definitions' : 'No project definitions yet'}
          description={
            search || complexityFilter !== 'ALL' || statusFilter !== 'ALL'
              ? 'Try refining your search terms or filter criteria.'
              : 'Create your first project definition template to begin assigning projects to students.'
          }
          action={
            !search && complexityFilter === 'ALL' && statusFilter === 'ALL' ? (
              <Button as="link" to="/mentor/projects/new" variant="primary">
                Create First Definition
              </Button>
            ) : undefined
          }
        />
      ) : (
        <div className="gf-definitions-directory__grid" role="list">
          {filteredDefinitions.map((def) => {
            const verNum = def.current_version?.version_number ?? 1;
            const complexity = def.current_version?.complexity ?? 'INTERMEDIATE';
            const problem = def.current_version?.problem || 'No problem description specified.';
            const updatedDate = def.updated_at
              ? new Date(def.updated_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })
              : 'Recently';

            return (
              <Card key={def.id} className="gf-definitions-directory__card" role="listitem">
                <div className="gf-definitions-directory__card-header">
                  <div className="gf-definitions-directory__card-badges">
                    <Badge variant="accent" size="sm">
                      v{verNum}
                    </Badge>
                    <Badge variant={getComplexityVariant(complexity)} size="sm">
                      {complexity}
                    </Badge>
                    <Badge variant={getStatusVariant(def.status)} size="sm">
                      {def.status}
                    </Badge>
                  </div>
                  <span className="gf-definitions-directory__card-date">
                    Updated {updatedDate}
                  </span>
                </div>

                <div className="gf-definitions-directory__card-body">
                  <h2 className="gf-definitions-directory__card-title">
                    <Link to={`/mentor/projects/${def.id}`} className="gf-definitions-directory__card-link">
                      {def.name}
                    </Link>
                  </h2>
                  <p className="gf-definitions-directory__card-problem">
                    {problem}
                  </p>
                </div>

                <div className="gf-definitions-directory__card-footer">
                  <Button
                    as="link"
                    to={`/mentor/projects/${def.id}`}
                    variant="secondary"
                    size="sm"
                  >
                    View Detail
                  </Button>
                  <div className="gf-definitions-directory__card-actions-right">
                    <Button
                      as="link"
                      to={`/mentor/projects/${def.id}/edit`}
                      variant="tertiary"
                      size="sm"
                    >
                      Edit
                    </Button>
                    <Button
                      as="link"
                      to={`/mentor/projects/${def.id}/assign`}
                      variant="primary"
                      size="sm"
                    >
                      Assign
                    </Button>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
