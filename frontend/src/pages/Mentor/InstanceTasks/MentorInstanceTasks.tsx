import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectInstance, getMentorInstanceTasks } from '@/lib/api/client';
import type { MentorProjectInstanceDetail, TaskResponse, TaskStatus, TaskPriority } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceTasks.css';

export const MentorInstanceTasks: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const [projRes, tasksRes] = await Promise.all([
          getMentorProjectInstance(projectId),
          getMentorInstanceTasks(projectId),
        ]);
        if (mounted) {
          setProject(projRes);
          setTasks(tasksRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          setError(
            err instanceof Error ? err.message : 'Failed to retrieve project tasks or access denied.'
          );
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
  }, [projectId]);

  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => {
      if (statusFilter !== 'ALL' && t.status !== statusFilter) return false;
      if (priorityFilter !== 'ALL' && t.priority !== priorityFilter) return false;
      if (search.trim()) {
        const query = search.toLowerCase();
        const matchesCode = t.task_code.toLowerCase().includes(query);
        const matchesTitle = t.title.toLowerCase().includes(query);
        const matchesDesc = (t.description || '').toLowerCase().includes(query);
        if (!matchesCode && !matchesTitle && !matchesDesc) return false;
      }
      return true;
    });
  }, [tasks, statusFilter, priorityFilter, search]);

  const getStatusBadge = (status: TaskStatus) => {
    switch (status) {
      case 'COMPLETED':
        return <Badge variant="success">Completed</Badge>;
      case 'IN_PROGRESS':
        return <Badge variant="info">In Progress</Badge>;
      case 'BLOCKED':
        return <Badge variant="danger">Blocked</Badge>;
      case 'TODO':
      default:
        return <Badge variant="neutral">To Do</Badge>;
    }
  };

  const getPriorityBadge = (priority: TaskPriority) => {
    switch (priority) {
      case 'CRITICAL':
        return <Badge variant="danger">Critical</Badge>;
      case 'HIGH':
        return <Badge variant="warning">High</Badge>;
      case 'MEDIUM':
        return <Badge variant="neutral">Medium</Badge>;
      case 'LOW':
      default:
        return <Badge variant="neutral">Low</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-tasks-page" id="mentor-tasks-loading">
        <Skeleton width="100%" height="160px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <Skeleton width="100%" height="56px" style={{ borderRadius: '8px', marginBottom: '1rem' }} />
        <Skeleton width="100%" height="300px" style={{ borderRadius: '12px' }} />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-mentor-tasks-page" id="mentor-tasks-error">
        <div className="gf-mentor-tasks-error-card" role="alert">
          <h3>Task Supervision Restricted</h3>
          <p>{error || 'Project tasks not found or access denied.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-tasks-page" id="mentor-tasks-container">
      <MentorInstanceHeader project={project} activeTab="tasks" />

      {/* Control Bar: Filter and Search Only (Read-Only) */}
      <div className="gf-mentor-tasks__toolbar" id="mentor-tasks-toolbar">
        <div className="gf-mentor-tasks__search-wrap">
          <Input
            id="mentor-tasks-search"
            type="search"
            placeholder="Search tasks by code, title, or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="gf-mentor-tasks__filters">
          <label className="gf-mentor-tasks__filter-label">
            <span>Status:</span>
            <select
              id="filter-task-status"
              className="gf-mentor-tasks__select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="TODO">To Do</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="BLOCKED">Blocked</option>
              <option value="COMPLETED">Completed</option>
            </select>
          </label>

          <label className="gf-mentor-tasks__filter-label">
            <span>Priority:</span>
            <select
              id="filter-task-priority"
              className="gf-mentor-tasks__select"
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </label>
        </div>
      </div>

      {/* Task Inspection List / Table */}
      <div className="gf-mentor-tasks__content">
        <div className="gf-mentor-tasks__header-info">
          <span>
            Showing <strong>{filteredTasks.length}</strong> of <strong>{tasks.length}</strong> tasks
          </span>
          <span className="gf-mentor-tasks__read-only-indicator">READ-ONLY SUPERVISION</span>
        </div>

        {filteredTasks.length === 0 ? (
          <div className="gf-mentor-tasks__empty-state" id="mentor-tasks-empty">
            <p>No tasks match the selected criteria or no tasks exist for this project instance.</p>
          </div>
        ) : (
          <div className="gf-mentor-tasks__table-container">
            <table className="gf-mentor-tasks__table" id="mentor-tasks-table">
              <thead>
                <tr>
                  <th style={{ width: '80px' }}>Code</th>
                  <th>Task Title & Summary</th>
                  <th style={{ width: '120px' }}>Status</th>
                  <th style={{ width: '100px' }}>Priority</th>
                  <th style={{ width: '130px' }}>Phase</th>
                  <th style={{ width: '120px' }}>Category</th>
                  <th style={{ width: '120px' }}>Due Date</th>
                </tr>
              </thead>
              <tbody>
                {filteredTasks.map((t) => (
                  <tr key={t.id} id={`task-row-${t.id}`}>
                    <td className="gf-mentor-tasks__cell-code">
                      <code>{t.task_code}</code>
                    </td>
                    <td>
                      <div className="gf-mentor-tasks__title">{t.title}</div>
                      {t.description && (
                        <div className="gf-mentor-tasks__desc">{t.description}</div>
                      )}
                    </td>
                    <td>{getStatusBadge(t.status)}</td>
                    <td>{getPriorityBadge(t.priority)}</td>
                    <td className="gf-mentor-tasks__cell-meta">{t.phase}</td>
                    <td className="gf-mentor-tasks__cell-meta">{t.category}</td>
                    <td className="gf-mentor-tasks__cell-meta">
                      {t.due_date ? new Date(t.due_date).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
