import { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getProjectActivity } from '@/lib/api';
import type { ActivityItemResponse } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentActivity.css';

export function StudentActivity() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [activities, setActivities] = useState<ActivityItemResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchActivities = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProjectActivity(projectId);
      setActivities(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load project activity audit trail.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchActivities();
  }, [fetchActivities]);

  const filteredActivities = useMemo(() => {
    return activities.filter((act) => {
      // Category filter
      if (filterCategory !== 'ALL') {
        const et = act.event_type.toLowerCase();
        if (filterCategory === 'TASKS' && !et.includes('task')) return false;
        if (filterCategory === 'MILESTONES' && !et.includes('milestone')) return false;
        if (filterCategory === 'BLUEPRINT' && !et.includes('blueprint')) return false;
        if (filterCategory === 'RISKS' && !et.includes('risk')) return false;
        if (filterCategory === 'CHANGES' && !et.includes('change')) return false;
        if (filterCategory === 'MENTOR' && !et.includes('mentor') && !et.includes('help')) return false;
        if (filterCategory === 'GITHUB' && !et.includes('github')) return false;
      }

      // Search query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = act.title.toLowerCase().includes(q);
        const matchesDesc = act.description.toLowerCase().includes(q);
        return matchesTitle || matchesDesc;
      }

      return true;
    });
  }, [activities, filterCategory, searchQuery]);

  const getActorBadgeVariant = (actorRole: string): 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'accent' => {
    switch (actorRole?.toUpperCase()) {
      case 'STUDENT':
        return 'info';
      case 'MENTOR':
        return 'success';
      case 'AI':
      case 'AI_MENTOR':
        return 'accent';
      default:
        return 'neutral';
    }
  };

  if (isProjectLoading || (isLoading && activities.length === 0)) {
    return (
      <div className="gf-activity-page">
        <div className="gf-activity-page__loading" role="status">
          <LoadingSpinner size="lg" label="Loading project audit trail..." />
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-activity-page">
        <div className="gf-activity-page__container" style={{ paddingTop: '2rem' }}>
          <InlineErrorState
            error={projectError || 'Project not found.'}
            title="Error Loading Project"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-activity-page" id="student-activity-screen">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <div className="gf-activity-page__container">
        <header className="gf-activity-page__header">
          <div className="gf-activity-page__header-text">
            <h2 className="gf-activity-page__title">Audit Trail & Activity Stream</h2>
            <p className="gf-activity-page__subtitle">
              Canonical chronological history derived from domain events across your project lifecycle.
            </p>
          </div>
          <div className="gf-activity-page__actions">
            <Button
              variant="secondary"
              onClick={fetchActivities}
              disabled={isLoading}
              id="activity-refresh-btn"
            >
              {isLoading ? 'Refreshing...' : 'Refresh Stream'}
            </Button>
          </div>
        </header>

        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <InlineErrorState error={error} onRetry={fetchActivities} />
          </div>
        )}

        {/* Filter controls */}
        <div className="gf-activity-filters">
          <div className="gf-activity-filters__search">
            <input
              type="text"
              placeholder="Search activity events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="gf-activity-search-input"
              id="activity-search-input"
            />
          </div>

          <div className="gf-activity-filters__categories">
            {[
              { label: 'All', value: 'ALL' },
              { label: 'Tasks', value: 'TASKS' },
              { label: 'Milestones', value: 'MILESTONES' },
              { label: 'Blueprint', value: 'BLUEPRINT' },
              { label: 'Risks', value: 'RISKS' },
              { label: 'Changes', value: 'CHANGES' },
              { label: 'Mentor', value: 'MENTOR' },
              { label: 'GitHub', value: 'GITHUB' },
            ].map((cat) => (
              <button
                key={cat.value}
                type="button"
                className={`gf-activity-cat-btn ${filterCategory === cat.value ? 'gf-activity-cat-btn--active' : ''}`}
                onClick={() => setFilterCategory(cat.value)}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Timeline Stream */}
        <div className="gf-activity-timeline" id="activity-timeline-list">
          {filteredActivities.length > 0 ? (
            filteredActivities.map((item, index) => (
              <div key={item.id || index} className="gf-activity-item">
                <div className="gf-activity-item__marker">
                  <div className="gf-activity-item__dot" />
                  {index < filteredActivities.length - 1 && <div className="gf-activity-item__line" />}
                </div>

                <div className="gf-activity-item__card">
                  <div className="gf-activity-item__top">
                    <div className="gf-activity-item__badges">
                      <Badge variant={getActorBadgeVariant(item.actor_role)}>
                        {item.actor_role || 'SYSTEM'}
                      </Badge>
                      <code className="gf-activity-item__event-type">{item.event_type}</code>
                    </div>
                    <time className="gf-activity-item__time">
                      {item.occurred_at ? new Date(item.occurred_at).toLocaleString() : 'Recent'}
                    </time>
                  </div>

                  <h3 className="gf-activity-item__title">{item.title}</h3>
                  <p className="gf-activity-item__desc">{item.description}</p>

                  {item.metadata && Object.keys(item.metadata).length > 0 && (
                    <details className="gf-activity-item__meta">
                      <summary className="gf-activity-item__meta-summary">View event payload</summary>
                      <pre className="gf-activity-item__meta-content">
                        {JSON.stringify(item.metadata, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            ))
          ) : (
            <EmptyState
              title="No activity records found"
              description={
                searchQuery || filterCategory !== 'ALL'
                  ? 'No events match the selected filters.'
                  : 'Actions taken on this project will be recorded here automatically.'
              }
            />
          )}
        </div>
      </div>
    </div>
  );
}
