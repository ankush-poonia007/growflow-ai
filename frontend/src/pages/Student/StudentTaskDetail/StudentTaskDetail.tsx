import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getTask, updateTask, deleteTask } from '@/lib/api';
import type { TaskResponse, TaskStatus, TaskPriority, TaskPhase } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentTaskDetail.css';

export function StudentTaskDetail() {
  const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>();
  const navigate = useNavigate();
  const {
    project,
    isLoading: isProjectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useProjectWorkspace(projectId);

  const [task, setTask] = useState<TaskResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
    };
  }, []);

  // Form Fields
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [status, setStatus] = useState<TaskStatus>('TODO');
  const [priority, setPriority] = useState<TaskPriority>('MEDIUM');
  const [phase, setPhase] = useState<TaskPhase>('IMPLEMENTATION');
  const [category, setCategory] = useState<string>('');
  const [dueDate, setDueDate] = useState<string>('');
  const [acceptanceCriteria, setAcceptanceCriteria] = useState<string[]>([]);
  const [newCriterion, setNewCriterion] = useState<string>('');
  const [dependencies, setDependencies] = useState<string[]>([]);
  const [newDependency, setNewDependency] = useState<string>('');

  const fetchTask = useCallback(async () => {
    if (!projectId || !taskId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTask(projectId, taskId);
      setTask(data);
      setTitle(data.title);
      setDescription(data.description || '');
      setStatus(data.status);
      setPriority(data.priority);
      setPhase(data.phase);
      setCategory(data.category || '');
      setDueDate(data.due_date ? data.due_date.slice(0, 10) : '');
      setAcceptanceCriteria(data.acceptance_criteria || []);
      setDependencies(data.dependencies || []);
    } catch (err: any) {
      setError(err?.message || 'Unable to load task detail.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, taskId]);

  useEffect(() => {
    void fetchTask();
  }, [fetchTask]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !taskId) return;
    if (!title.trim()) {
      setError('Task title cannot be empty.');
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const updated = await updateTask(projectId, taskId, {
        title: title.trim(),
        description: description.trim(),
        status,
        priority,
        phase,
        category: category.trim(),
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        acceptance_criteria: acceptanceCriteria,
        dependencies,
      });
      setTask(updated);
      setSuccessMsg('Task updated successfully.');
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
      feedbackTimerRef.current = setTimeout(() => {
        setSuccessMsg(null);
        feedbackTimerRef.current = null;
      }, 3000);
    } catch (err: any) {
      setError(err?.message || 'Failed to update task.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!projectId || !taskId) return;
    if (!window.confirm('Are you sure you want to permanently delete this task?')) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteTask(projectId, taskId);
      navigate(`/student/projects/${projectId}/tasks`);
    } catch (err: any) {
      setError(err?.message || 'Failed to delete task.');
      setIsDeleting(false);
    }
  };

  const handleAddCriterion = () => {
    if (!newCriterion.trim()) return;
    setAcceptanceCriteria((prev) => [...prev, newCriterion.trim()]);
    setNewCriterion('');
  };

  const handleRemoveCriterion = (index: number) => {
    setAcceptanceCriteria((prev) => prev.filter((_, i) => i !== index));
  };

  const handleAddDependency = () => {
    if (!newDependency.trim()) return;
    setDependencies((prev) => [...prev, newDependency.trim().toUpperCase()]);
    setNewDependency('');
  };

  const handleRemoveDependency = (index: number) => {
    setDependencies((prev) => prev.filter((_, i) => i !== index));
  };

  const handleRetry = useCallback(() => {
    void refetchProject();
    void fetchTask();
  }, [refetchProject, fetchTask]);

  if (isProjectLoading || isLoading) {
    return (
      <div className="gf-task-detail-page">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '1rem' }}>
          <LoadingSpinner size="lg" label="Loading task details..." />
          <p style={{ color: 'var(--gf-color-text-secondary)', margin: 0, fontSize: '0.875rem' }}>Loading task details...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project || !task) {
    return (
      <div className="gf-task-detail-page">
        <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1rem' }}>
          <InlineErrorState
            error={projectError || error || 'Task or project not found.'}
            onRetry={handleRetry}
            action={
              <Button as="link" to={`/student/projects/${projectId}/tasks`} variant="secondary" size="sm">
                Back to Tasks
              </Button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-task-detail-page" id="student-task-detail-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-task-detail-container">
        {/* Top Header Card */}
        <div className="gf-task-detail-header-card">
          <div className="gf-task-detail-title-group">
            <Link
              to={`/student/projects/${projectId}/tasks`}
              className="gf-task-detail-back-link"
              id="back-to-tasks-btn"
            >
              ← Back to All Tasks
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.25rem' }}>
              <span className="gf-task-detail-code-badge">{task.task_code}</span>
              <h1 className="gf-task-detail-title">{task.title}</h1>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Badge
              variant={
                task.status === 'COMPLETED'
                  ? 'success'
                  : task.status === 'BLOCKED'
                  ? 'danger'
                  : task.status === 'IN_PROGRESS'
                  ? 'accent'
                  : 'neutral'
              }
            >
              {task.status}
            </Badge>
            <Badge
              variant={
                task.priority === 'CRITICAL'
                  ? 'danger'
                  : task.priority === 'HIGH'
                  ? 'warning'
                  : task.priority === 'MEDIUM'
                  ? 'accent'
                  : 'neutral'
              }
            >
              {task.priority} Priority
            </Badge>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <InlineErrorState error={error} onRetry={fetchTask} />
          </div>
        )}
        {successMsg && (
          <div style={{ padding: '1rem', background: '#f0fdf4', color: '#16a34a', borderRadius: '8px', marginBottom: '1.5rem' }}>
            {successMsg}
          </div>
        )}

        {/* Edit Form Grid */}
        <form onSubmit={handleSave}>
          <div className="gf-task-detail-grid">
            {/* Left Column: Core Fields */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="gf-task-detail-card">
                <h3>Task Definition</h3>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="task-edit-title">
                    Title *
                  </label>
                  <input
                    type="text"
                    id="task-edit-title"
                    className="gf-form-input"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="task-edit-description">
                    Description & Specifications
                  </label>
                  <textarea
                    id="task-edit-description"
                    className="gf-form-textarea"
                    style={{ minHeight: '140px' }}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Document implementation details, technical constraints, or edge cases..."
                  />
                </div>
              </div>

              <div className="gf-task-detail-card">
                <h3>Acceptance Criteria</h3>
                {acceptanceCriteria.length === 0 ? (
                  <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                    No specific acceptance criteria added yet.
                  </p>
                ) : (
                  <ul className="gf-checklist">
                    {acceptanceCriteria.map((crit, idx) => (
                      <li key={idx} className="gf-checklist-item">
                        <span>✓ {crit}</span>
                        <button
                          type="button"
                          className="gf-checklist-remove-btn"
                          onClick={() => handleRemoveCriterion(idx)}
                          aria-label="Remove criterion"
                        >
                          ✕
                        </button>
                      </li>
                    ))}
                  </ul>
                )}

                <div className="gf-checklist-add">
                  <input
                    type="text"
                    className="gf-form-input"
                    style={{ flex: 1 }}
                    placeholder="Add an acceptance requirement..."
                    value={newCriterion}
                    onChange={(e) => setNewCriterion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddCriterion();
                      }
                    }}
                  />
                  <Button as="button" variant="secondary" type="button" onClick={handleAddCriterion}>
                    Add
                  </Button>
                </div>
              </div>

              <div className="gf-task-detail-card">
                <h3>Dependencies</h3>
                {dependencies.length === 0 ? (
                  <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                    No prerequisite task dependencies.
                  </p>
                ) : (
                  <ul className="gf-checklist">
                    {dependencies.map((dep, idx) => (
                      <li key={idx} className="gf-checklist-item">
                        <span>🔗 Depends on <strong>{dep}</strong></span>
                        <button
                          type="button"
                          className="gf-checklist-remove-btn"
                          onClick={() => handleRemoveDependency(idx)}
                          aria-label="Remove dependency"
                        >
                          ✕
                        </button>
                      </li>
                    ))}
                  </ul>
                )}

                <div className="gf-checklist-add">
                  <input
                    type="text"
                    className="gf-form-input"
                    style={{ flex: 1 }}
                    placeholder="e.g. T01, T02"
                    value={newDependency}
                    onChange={(e) => setNewDependency(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddDependency();
                      }
                    }}
                  />
                  <Button as="button" variant="secondary" type="button" onClick={handleAddDependency}>
                    Link Task
                  </Button>
                </div>
              </div>
            </div>

            {/* Right Column: Execution Metadata & Actions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="gf-task-detail-card">
                <h3>Execution State</h3>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="task-status-select">
                    Current Status
                  </label>
                  <select
                    id="task-status-select"
                    className="gf-form-select"
                    value={status}
                    onChange={(e) => setStatus(e.target.value as TaskStatus)}
                  >
                    <option value="TODO">To Do</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="BLOCKED">Blocked</option>
                    <option value="COMPLETED">Completed</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="task-priority-select">
                    Priority Level
                  </label>
                  <select
                    id="task-priority-select"
                    className="gf-form-select"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as TaskPriority)}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="task-phase-select">
                    Project Phase
                  </label>
                  <select
                    id="task-phase-select"
                    className="gf-form-select"
                    value={phase}
                    onChange={(e) => setPhase(e.target.value as TaskPhase)}
                  >
                    <option value="PLANNING">Planning</option>
                    <option value="IMPLEMENTATION">Implementation</option>
                    <option value="TESTING">Testing</option>
                    <option value="DEPLOYMENT">Deployment</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="task-category-input">
                    Category
                  </label>
                  <input
                    type="text"
                    id="task-category-input"
                    className="gf-form-input"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="e.g. Backend, Frontend, DevOps"
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="task-due-date-input">
                    Target Due Date
                  </label>
                  <input
                    type="date"
                    id="task-due-date-input"
                    className="gf-form-input"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                  />
                </div>

                <div className="gf-task-detail-meta-list">
                  <div><strong>Created:</strong> {new Date(task.created_at).toLocaleString()}</div>
                  <div><strong>Last Updated:</strong> {new Date(task.updated_at).toLocaleString()}</div>
                  {task.completed_at && (
                    <div style={{ color: '#10b981' }}>
                      <strong>Completed At:</strong> {new Date(task.completed_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="gf-task-detail-card gf-task-detail-actions-card">
                <h3>Actions</h3>
                <Button
                  as="button"
                  variant="primary"
                  type="submit"
                  id="save-task-btn"
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Task Changes'}
                </Button>

                <Button
                  as="button"
                  variant="secondary"
                  type="button"
                  id="delete-task-btn"
                  onClick={handleDelete}
                  disabled={isDeleting}
                  style={{ color: '#ef4444', borderColor: '#fca5a5' }}
                >
                  {isDeleting ? 'Deleting...' : 'Delete Task'}
                </Button>
              </div>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
}
