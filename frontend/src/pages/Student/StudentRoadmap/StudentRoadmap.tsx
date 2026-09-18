import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getRoadmap } from '@/lib/api';
import type { RoadmapResponse } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentRoadmap.css';

export function StudentRoadmap() {
  const { projectId } = useParams<{ projectId: string }>();
  const {
    project,
    isLoading: isProjectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useProjectWorkspace(projectId);

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRoadmap = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getRoadmap(projectId);
      setRoadmap(data);
    } catch (err: any) {
      setError(err?.message || 'Unable to load roadmap projection.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchRoadmap();
  }, [fetchRoadmap]);

  const handleRetry = useCallback(() => {
    void refetchProject();
    void fetchRoadmap();
  }, [refetchProject, fetchRoadmap]);

  if (isProjectLoading || isLoading) {
    return (
      <div className="gf-roadmap-page">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '1rem' }}>
          <LoadingSpinner size="lg" label="Synthesizing execution roadmap projection..." />
          <p style={{ color: 'var(--gf-color-text-secondary)', margin: 0, fontSize: '0.875rem' }}>Synthesizing execution roadmap projection...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project || !roadmap) {
    return (
      <div className="gf-roadmap-page">
        <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1rem' }}>
          <InlineErrorState
            error={projectError || error || 'Roadmap projection could not be loaded.'}
            onRetry={handleRetry}
          />
        </div>
      </div>
    );
  }

  const { summary, milestones, grouped_tasks } = roadmap;

  return (
    <div className="gf-roadmap-page" id="student-roadmap-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-roadmap-container">
        {/* Synthesis Summary Bar */}
        <div className="gf-roadmap-summary-bar">
          <div className="gf-roadmap-summary-card">
            <h4>OVERALL PROGRESS</h4>
            <div className="gf-roadmap-summary-val" style={{ color: '#0284c7' }} id="roadmap-stat-progress">
              {summary.overall_progress}%
            </div>
          </div>

          <div className="gf-roadmap-summary-card">
            <h4>GATE MILESTONES</h4>
            <div className="gf-roadmap-summary-val">
              {summary.completed_milestones} / {summary.total_milestones}
            </div>
          </div>

          <div className="gf-roadmap-summary-card">
            <h4>TASK COMPLETION</h4>
            <div className="gf-roadmap-summary-val" style={{ color: '#10b981' }}>
              {summary.completed_tasks} / {summary.total_tasks}
            </div>
          </div>

          <div className="gf-roadmap-summary-card">
            <h4>OVERDUE ITEMS</h4>
            <div
              className="gf-roadmap-summary-val"
              style={{ color: summary.overdue_tasks_count > 0 ? '#ef4444' : '#64748b' }}
              id="roadmap-stat-overdue"
            >
              {summary.overdue_tasks_count}
            </div>
          </div>

          <div className="gf-roadmap-summary-card">
            <h4>BLOCKED TASKS</h4>
            <div
              className="gf-roadmap-summary-val"
              style={{ color: summary.blocked_tasks_count > 0 ? '#f59e0b' : '#64748b' }}
              id="roadmap-stat-blocked"
            >
              {summary.blocked_tasks_count}
            </div>
          </div>
        </div>

        {/* Milestone Progression Section */}
        <section className="gf-roadmap-timeline-section" aria-label="Milestones Progression">
          <h3>Sequential Stage Gates & Verification Deliverables</h3>
          <div className="gf-roadmap-timeline">
            {milestones.map((m) => (
              <div key={m.id} className="gf-roadmap-milestone-row" id={`roadmap-gate-${m.gate_code || m.id}`}>
                <div className="gf-roadmap-gate-badge">{m.gate_code || 'M'}</div>

                <div className="gf-roadmap-milestone-content">
                  <div className="gf-roadmap-milestone-title-row">
                    <span className="gf-roadmap-milestone-title">{m.title}</span>
                    <Badge
                      variant={
                        m.status === 'COMPLETED'
                          ? 'success'
                          : m.status === 'IN_PROGRESS'
                          ? 'accent'
                          : m.status === 'AT_RISK'
                          ? 'danger'
                          : 'neutral'
                      }
                    >
                      {m.status} ({m.progress_percent}%)
                    </Badge>
                  </div>

                  {m.description && (
                    <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748b' }}>
                      {m.description}
                    </p>
                  )}

                  {/* Progress Bar */}
                  <div style={{ width: '100%', height: '6px', background: '#e2e8f0', borderRadius: '999px', overflow: 'hidden', marginTop: '4px' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${m.progress_percent}%`,
                        background: 'linear-gradient(90deg, #0284c7, #10b981)',
                        borderRadius: '999px',
                      }}
                    />
                  </div>

                  {/* Attached Tasks Snippets */}
                  {m.tasks && m.tasks.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                      {m.tasks.map((t) => (
                        <Link
                          key={t.id}
                          to={`/student/projects/${projectId}/tasks/${t.id}`}
                          style={{
                            fontSize: '0.75rem',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: t.status === 'COMPLETED' ? '#dcfce7' : '#f1f5f9',
                            color: t.status === 'COMPLETED' ? '#166534' : '#475569',
                            textDecoration: 'none',
                            fontWeight: 500,
                          }}
                        >
                          {t.status === 'COMPLETED' ? '✓' : '○'} {t.task_code}: {t.title}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Attention Queues Grid */}
        <section className="gf-roadmap-attention-grid" aria-label="Task Execution Breakdown">
          {/* Overdue Queue */}
          <div className="gf-roadmap-panel" style={{ borderLeft: '4px solid #ef4444' }}>
            <h3 style={{ color: '#b91c1c' }}>
              <span>🚨 Overdue Attention</span>
              <span>{grouped_tasks.overdue.length}</span>
            </h3>
            {grouped_tasks.overdue.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                No tasks are currently past their target due date.
              </p>
            ) : (
              grouped_tasks.overdue.map((t) => (
                <div key={t.id} className="gf-roadmap-panel-item gf-roadmap-panel-item--overdue">
                  <Link
                    to={`/student/projects/${projectId}/tasks/${t.id}`}
                    style={{ fontWeight: 600, color: '#9f1239', textDecoration: 'none' }}
                  >
                    {t.task_code}: {t.title}
                  </Link>
                  <span style={{ fontSize: '0.75rem' }}>
                    Due {t.due_date ? new Date(t.due_date).toLocaleDateString() : 'Overdue'}
                  </span>
                </div>
              ))
            )}
          </div>

          {/* Blocked Queue */}
          <div className="gf-roadmap-panel" style={{ borderLeft: '4px solid #f59e0b' }}>
            <h3 style={{ color: '#b45309' }}>
              <span>⚠️ Blocked Items</span>
              <span>{grouped_tasks.blocked.length}</span>
            </h3>
            {grouped_tasks.blocked.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                No blocked tasks impeding development.
              </p>
            ) : (
              grouped_tasks.blocked.map((t) => (
                <div key={t.id} className="gf-roadmap-panel-item gf-roadmap-panel-item--blocked">
                  <Link
                    to={`/student/projects/${projectId}/tasks/${t.id}`}
                    style={{ fontWeight: 600, color: '#92400e', textDecoration: 'none' }}
                  >
                    {t.task_code}: {t.title}
                  </Link>
                  <Badge variant="danger">Blocked</Badge>
                </div>
              ))
            )}
          </div>

          {/* In Progress Queue */}
          <div className="gf-roadmap-panel" style={{ borderLeft: '4px solid #0284c7' }}>
            <h3 style={{ color: '#0369a1' }}>
              <span>⚡ Active In Progress</span>
              <span>{grouped_tasks.in_progress.length}</span>
            </h3>
            {grouped_tasks.in_progress.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                No active tasks currently marked in progress.
              </p>
            ) : (
              grouped_tasks.in_progress.map((t) => (
                <div key={t.id} className="gf-roadmap-panel-item">
                  <Link
                    to={`/student/projects/${projectId}/tasks/${t.id}`}
                    style={{ fontWeight: 600, color: '#0284c7', textDecoration: 'none' }}
                  >
                    {t.task_code}: {t.title}
                  </Link>
                  <Badge variant="accent">In Progress</Badge>
                </div>
              ))
            )}
          </div>

          {/* Upcoming Queue */}
          <div className="gf-roadmap-panel">
            <h3>
              <span>📋 Next in Queue</span>
              <span>{grouped_tasks.upcoming.length}</span>
            </h3>
            {grouped_tasks.upcoming.length === 0 ? (
              <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                All upcoming tasks have been started or completed.
              </p>
            ) : (
              grouped_tasks.upcoming.slice(0, 5).map((t) => (
                <div key={t.id} className="gf-roadmap-panel-item">
                  <Link
                    to={`/student/projects/${projectId}/tasks/${t.id}`}
                    style={{ fontWeight: 500, color: '#334155', textDecoration: 'none' }}
                  >
                    {t.task_code}: {t.title}
                  </Link>
                  <Badge variant="neutral">{t.priority}</Badge>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
