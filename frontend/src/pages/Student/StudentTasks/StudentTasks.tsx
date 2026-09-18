import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getTasks, createTask, updateTask } from '@/lib/api';
import type { TaskResponse, TaskStatus, TaskPriority, TaskPhase, TaskCreatePayload } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentTasks.css';

export function StudentTasks() {
  const { projectId } = useParams<{ projectId: string }>();
  const {
    project,
    isLoading: isProjectLoading,
    error: projectError,
    refetch: refetchProject,
  } = useProjectWorkspace(projectId);

  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [viewMode, setViewMode] = useState<'kanban' | 'table'>('kanban');

  // Create Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [newTaskTitle, setNewTaskTitle] = useState<string>('');
  const [newTaskDesc, setNewTaskDesc] = useState<string>('');
  const [newTaskPriority, setNewTaskPriority] = useState<TaskPriority>('MEDIUM');
  const [newTaskCategory, setNewTaskCategory] = useState<string>('DEVELOPMENT');
  const [newTaskPhase, setNewTaskPhase] = useState<TaskPhase>('IMPLEMENTATION');
  const [newTaskDueDate, setNewTaskDueDate] = useState<string>('');

  const fetchTasks = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTasks(projectId);
      setTasks(data);
    } catch (err: any) {
      setError(err?.message || 'Unable to load project tasks.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchTasks();
  }, [fetchTasks]);

  // Status transition handler
  const handleQuickStatusChange = async (task: TaskResponse, newStatus: TaskStatus) => {
    if (!projectId) return;
    try {
      setError(null);
      const updated = await updateTask(projectId, task.id, { status: newStatus });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (err: any) {
      setError(`Failed to update task status: ${err?.message || 'Unknown error'}`);
    }
  };

  // Create task handler
  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;
    if (!newTaskTitle.trim()) {
      setModalError('Task title is required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    const payload: TaskCreatePayload = {
      title: newTaskTitle.trim(),
      description: newTaskDesc.trim(),
      priority: newTaskPriority,
      category: newTaskCategory.trim() || 'GENERAL',
      phase: newTaskPhase,
      due_date: newTaskDueDate ? new Date(newTaskDueDate).toISOString() : null,
    };

    try {
      const created = await createTask(projectId, payload);
      setTasks((prev) => [...prev, created]);
      setIsModalOpen(false);
      setNewTaskTitle('');
      setNewTaskDesc('');
      setNewTaskPriority('MEDIUM');
      setNewTaskDueDate('');
    } catch (err: any) {
      setModalError(err?.message || 'Failed to create task.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Filtered tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      if (statusFilter !== 'ALL' && task.status !== statusFilter) return false;
      if (priorityFilter !== 'ALL' && task.priority !== priorityFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = task.title.toLowerCase().includes(q);
        const matchCode = task.task_code.toLowerCase().includes(q);
        const matchCategory = task.category.toLowerCase().includes(q);
        const matchDesc = task.description.toLowerCase().includes(q);
        if (!matchTitle && !matchCode && !matchCategory && !matchDesc) return false;
      }
      return true;
    });
  }, [tasks, statusFilter, priorityFilter, searchQuery]);

  // Counts
  const stats = useMemo(() => {
    return {
      total: tasks.length,
      todo: tasks.filter((t) => t.status === 'TODO').length,
      inProgress: tasks.filter((t) => t.status === 'IN_PROGRESS').length,
      blocked: tasks.filter((t) => t.status === 'BLOCKED').length,
      completed: tasks.filter((t) => t.status === 'COMPLETED').length,
    };
  }, [tasks]);

  const kanbanColumns: { status: TaskStatus; label: string; badgeVariant: 'neutral' | 'accent' | 'danger' | 'success' }[] = [
    { status: 'TODO', label: 'To Do', badgeVariant: 'neutral' },
    { status: 'IN_PROGRESS', label: 'In Progress', badgeVariant: 'accent' },
    { status: 'BLOCKED', label: 'Blocked', badgeVariant: 'danger' },
    { status: 'COMPLETED', label: 'Completed', badgeVariant: 'success' },
  ];

  const getPriorityBadgeVariant = (priority: TaskPriority): 'neutral' | 'accent' | 'warning' | 'danger' => {
    switch (priority) {
      case 'CRITICAL':
        return 'danger';
      case 'HIGH':
        return 'warning';
      case 'MEDIUM':
        return 'accent';
      case 'LOW':
      default:
        return 'neutral';
    }
  };

  if (isProjectLoading) {
    return (
      <div className="gf-tasks-page">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '50vh', gap: '1rem' }}>
          <LoadingSpinner size="lg" label="Loading project tasks..." />
          <p style={{ color: 'var(--gf-color-text-secondary)', margin: 0, fontSize: '0.875rem' }}>Loading project tasks...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-tasks-page">
        <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1rem' }}>
          <InlineErrorState
            error={projectError || 'Project workspace not found.'}
            onRetry={refetchProject}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-tasks-page" id="student-tasks-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-tasks-container">
        {/* Stats Bar */}
        <div className="gf-tasks-stats" role="region" aria-label="Task Statistics Summary">
          <div className="gf-tasks-stat-card">
            <span className="gf-tasks-stat-label">Total Tasks</span>
            <span className="gf-tasks-stat-value" id="stat-total-tasks">{stats.total}</span>
          </div>
          <div className="gf-tasks-stat-card">
            <span className="gf-tasks-stat-label">To Do</span>
            <span className="gf-tasks-stat-value" id="stat-todo-tasks">{stats.todo}</span>
          </div>
          <div className="gf-tasks-stat-card">
            <span className="gf-tasks-stat-label">In Progress</span>
            <span className="gf-tasks-stat-value" id="stat-progress-tasks" style={{ color: '#0284c7' }}>
              {stats.inProgress}
            </span>
          </div>
          <div className="gf-tasks-stat-card">
            <span className="gf-tasks-stat-label">Blocked</span>
            <span className="gf-tasks-stat-value" id="stat-blocked-tasks" style={{ color: '#ef4444' }}>
              {stats.blocked}
            </span>
          </div>
          <div className="gf-tasks-stat-card">
            <span className="gf-tasks-stat-label">Completed</span>
            <span className="gf-tasks-stat-value" id="stat-completed-tasks" style={{ color: '#10b981' }}>
              {stats.completed}
            </span>
          </div>
        </div>

        {/* Controls Bar */}
        <div className="gf-tasks-controls">
          <div className="gf-tasks-filters">
            <div className="gf-tasks-search">
              <input
                type="text"
                id="tasks-search-input"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                aria-label="Search project tasks"
              />
            </div>

            <select
              className="gf-tasks-select"
              id="tasks-status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              aria-label="Filter tasks by status"
            >
              <option value="ALL">All Statuses</option>
              <option value="TODO">To Do</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="BLOCKED">Blocked</option>
              <option value="COMPLETED">Completed</option>
            </select>

            <select
              className="gf-tasks-select"
              id="tasks-priority-filter"
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              aria-label="Filter tasks by priority"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="gf-tasks-actions">
            <div className="gf-tasks-view-toggle">
              <button
                type="button"
                className={`gf-tasks-view-btn ${viewMode === 'kanban' ? 'gf-tasks-view-btn--active' : ''}`}
                id="view-mode-kanban-btn"
                onClick={() => setViewMode('kanban')}
                aria-label="Kanban view"
              >
                Board
              </button>
              <button
                type="button"
                className={`gf-tasks-view-btn ${viewMode === 'table' ? 'gf-tasks-view-btn--active' : ''}`}
                id="view-mode-table-btn"
                onClick={() => setViewMode('table')}
                aria-label="Table view"
              >
                List
              </button>
            </div>

            <Button
              as="button"
              variant="primary"
              id="create-task-btn"
              onClick={() => setIsModalOpen(true)}
            >
              + New Task
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{ marginBottom: '1.5rem' }}>
            <InlineErrorState
              error={error}
              onRetry={fetchTasks}
            />
          </div>
        )}

        {/* Content View */}
        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 0', gap: '0.75rem' }}>
            <LoadingSpinner size="md" label="Refreshing task registry..." />
            <span style={{ color: 'var(--gf-color-text-secondary)', fontSize: '0.875rem' }}>Refreshing task registry...</span>
          </div>
        ) : filteredTasks.length === 0 ? (
          <EmptyState
            icon="📋"
            title="No tasks found"
            description={
              searchQuery || statusFilter !== 'ALL' || priorityFilter !== 'ALL'
                ? 'Try adjusting your filters or search query to find relevant tasks.'
                : 'No tasks have been added yet. Create your first operational task to begin tracking execution.'
            }
            action={
              <Button as="button" variant="primary" onClick={() => setIsModalOpen(true)}>
                Create First Task
              </Button>
            }
          />
        ) : viewMode === 'kanban' ? (
          /* Kanban View */
          <div className="gf-tasks-kanban" role="region" aria-label="Tasks Kanban Board">
            {kanbanColumns.map((col) => {
              const colTasks = filteredTasks.filter((t) => t.status === col.status);
              return (
                <div className="gf-kanban-col" key={col.status} id={`kanban-col-${col.status.toLowerCase()}`}>
                  <div className="gf-kanban-header">
                    <span className="gf-kanban-title">
                      {col.label}
                    </span>
                    <span className="gf-kanban-count">{colTasks.length}</span>
                  </div>

                  <div className="gf-kanban-list">
                    {colTasks.map((task) => (
                      <div className="gf-task-card" key={task.id} id={`task-card-${task.task_code}`}>
                        <div className="gf-task-card__top">
                          <span className="gf-task-card__code">{task.task_code}</span>
                          <Badge variant={getPriorityBadgeVariant(task.priority)}>
                            {task.priority}
                          </Badge>
                        </div>

                        <Link
                          to={`/student/projects/${projectId}/tasks/${task.id}`}
                          className="gf-task-card__title"
                          id={`task-link-${task.id}`}
                        >
                          {task.title}
                        </Link>

                        {task.description && (
                          <p className="gf-task-card__desc">{task.description}</p>
                        )}

                        <div className="gf-task-card__meta">
                          <span>{task.category || 'Engineering'}</span>
                          {task.due_date ? (
                            <span>Due {new Date(task.due_date).toLocaleDateString()}</span>
                          ) : (
                            <span>{task.phase}</span>
                          )}
                        </div>

                        <div className="gf-task-card__quick-status">
                          {col.status !== 'TODO' && (
                            <button
                              type="button"
                              className="gf-task-quick-btn"
                              onClick={() => handleQuickStatusChange(task, 'TODO')}
                              title="Move to To Do"
                            >
                              Todo
                            </button>
                          )}
                          {col.status !== 'IN_PROGRESS' && (
                            <button
                              type="button"
                              className="gf-task-quick-btn"
                              onClick={() => handleQuickStatusChange(task, 'IN_PROGRESS')}
                              title="Move to In Progress"
                            >
                              Start
                            </button>
                          )}
                          {col.status !== 'BLOCKED' && (
                            <button
                              type="button"
                              className="gf-task-quick-btn"
                              onClick={() => handleQuickStatusChange(task, 'BLOCKED')}
                              title="Mark Blocked"
                            >
                              Block
                            </button>
                          )}
                          {col.status !== 'COMPLETED' && (
                            <button
                              type="button"
                              className="gf-task-quick-btn"
                              onClick={() => handleQuickStatusChange(task, 'COMPLETED')}
                              title="Complete Task"
                            >
                              Done ✓
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Table List View */
          <div className="gf-tasks-table-wrapper" role="region" aria-label="Tasks List Table">
            <table className="gf-tasks-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Task Title</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Category</th>
                  <th>Phase</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredTasks.map((task) => (
                  <tr key={task.id} id={`task-row-${task.task_code}`}>
                    <td>
                      <span className="gf-task-card__code">{task.task_code}</span>
                    </td>
                    <td>
                      <Link
                        to={`/student/projects/${projectId}/tasks/${task.id}`}
                        className="gf-tasks-table__link"
                      >
                        {task.title}
                      </Link>
                    </td>
                    <td>
                      <Badge variant={getPriorityBadgeVariant(task.priority)}>
                        {task.priority}
                      </Badge>
                    </td>
                    <td>
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
                    </td>
                    <td>{task.category || 'GENERAL'}</td>
                    <td>{task.phase}</td>
                    <td>
                      <Link
                        to={`/student/projects/${projectId}/tasks/${task.id}`}
                        className="gf-task-quick-btn"
                      >
                        View / Edit →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {/* Create Task Modal */}
      {isModalOpen && (
        <div className="gf-modal-backdrop" role="dialog" aria-modal="true">
          <div className="gf-modal-card">
            <div className="gf-modal-header">
              <h2 className="gf-modal-title">Create Operational Task</h2>
              <button
                type="button"
                className="gf-modal-close-btn"
                onClick={() => setIsModalOpen(false)}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateTask}>
              <div className="gf-modal-body">
                {modalError && (
                  <div style={{ padding: '0.75rem', background: '#fef2f2', color: '#b91c1c', borderRadius: '6px', fontSize: '0.875rem' }}>
                    {modalError}
                  </div>
                )}

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-task-title">
                    Task Title *
                  </label>
                  <input
                    type="text"
                    id="new-task-title"
                    className="gf-form-input"
                    placeholder="e.g. Set up JWT authentication middleware"
                    value={newTaskTitle}
                    onChange={(e) => setNewTaskTitle(e.target.value)}
                    required
                    autoFocus
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-task-desc">
                    Description
                  </label>
                  <textarea
                    id="new-task-desc"
                    className="gf-form-textarea"
                    placeholder="Provide acceptance details and scope..."
                    value={newTaskDesc}
                    onChange={(e) => setNewTaskDesc(e.target.value)}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-task-priority">
                      Priority
                    </label>
                    <select
                      id="new-task-priority"
                      className="gf-form-select"
                      value={newTaskPriority}
                      onChange={(e) => setNewTaskPriority(e.target.value as TaskPriority)}
                    >
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                      <option value="CRITICAL">Critical</option>
                    </select>
                  </div>

                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-task-phase">
                      Lifecycle Phase
                    </label>
                    <select
                      id="new-task-phase"
                      className="gf-form-select"
                      value={newTaskPhase}
                      onChange={(e) => setNewTaskPhase(e.target.value as TaskPhase)}
                    >
                      <option value="PLANNING">Planning</option>
                      <option value="IMPLEMENTATION">Implementation</option>
                      <option value="TESTING">Testing</option>
                      <option value="DEPLOYMENT">Deployment</option>
                    </select>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-task-category">
                      Category
                    </label>
                    <input
                      type="text"
                      id="new-task-category"
                      className="gf-form-input"
                      placeholder="e.g. Backend, Frontend, QA"
                      value={newTaskCategory}
                      onChange={(e) => setNewTaskCategory(e.target.value)}
                    />
                  </div>

                  <div className="gf-form-group">
                    <label className="gf-form-label" htmlFor="new-task-due">
                      Target Due Date
                    </label>
                    <input
                      type="date"
                      id="new-task-due"
                      className="gf-form-input"
                      value={newTaskDueDate}
                      onChange={(e) => setNewTaskDueDate(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="gf-modal-footer">
                <Button
                  as="button"
                  variant="secondary"
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  as="button"
                  variant="primary"
                  type="submit"
                  id="submit-task-btn"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Creating...' : 'Create Task'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
