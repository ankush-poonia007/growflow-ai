import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router';
import {
  getMentorGroup,
  getGroupStudents,
  getGroupProjects,
} from '@/lib/api/client';
import type {
  GroupResponse,
  GroupStudentResponse,
  ProjectResponse,
} from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupWorkspace.css';

export function GroupWorkspace() {
  const { groupId } = useParams<{ groupId: string }>();
  const [group, setGroup] = useState<GroupResponse | null>(null);
  const [students, setStudents] = useState<GroupStudentResponse[]>([]);
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const copiedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (copiedTimerRef.current) {
        clearTimeout(copiedTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!groupId) return;
    let mounted = true;

    async function loadWorkspaceData() {
      try {
        setLoading(true);
        setError(null);
        const [gRes, sRes, pRes] = await Promise.all([
          getMentorGroup(groupId!),
          getGroupStudents(groupId!),
          getGroupProjects(groupId!),
        ]);

        if (mounted) {
          setGroup(gRes);
          setStudents(sRes);
          setProjects(pRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to load group workspace.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadWorkspaceData();
    return () => {
      mounted = false;
    };
  }, [groupId]);

  const handleCopyCode = async () => {
    if (!group?.join_code) return;
    try {
      await navigator.clipboard.writeText(group.join_code);
      setCopied(true);
      if (copiedTimerRef.current) {
        clearTimeout(copiedTimerRef.current);
      }
      copiedTimerRef.current = setTimeout(() => {
        setCopied(false);
        copiedTimerRef.current = null;
      }, 2000);
    } catch {
      // ignore clipboard error
    }
  };

  const atRiskProjects = projects.filter(
    (p) => p.health === 'WARNING' || p.health === 'CRITICAL' || p.health === 'AT_RISK'
  );

  if (loading) {
    return (
      <div className="gf-group-workspace">
        <Skeleton height="60px" />
        <div className="gf-group-workspace__stats">
          <Skeleton height="90px" />
          <Skeleton height="90px" />
          <Skeleton height="90px" />
        </div>
        <Skeleton height="200px" />
      </div>
    );
  }

  if (error || !group) {
    return (
      <div className="gf-group-workspace">
        <PageHeader
          eyebrow="SUPERVISE"
          title="Group Not Found"
          breadcrumbs={[{ label: 'Groups', to: '/mentor/groups' }, { label: 'Not Found' }]}
        />
        <div className="gf-group-workspace__error" role="alert">
          <p>{error || 'This student group does not exist or you do not have permission to view it.'}</p>
          <Button as="link" to="/mentor/groups" variant="secondary">
            Back to Groups Directory
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-group-workspace">
      <PageHeader
        eyebrow="COHORT WORKSPACE"
        title={group.name}
        breadcrumbs={[
          { label: 'Groups', to: '/mentor/groups' },
          { label: group.name },
        ]}
        badge={
          <div className="gf-group-workspace__header-badges">
            <Badge variant={group.status === 'ACTIVE' ? 'success' : 'neutral'}>
              {group.status}
            </Badge>
            <div className="gf-group-workspace__join-code" title="Enrollment Join Code">
              <span className="gf-group-workspace__join-label">CODE:</span>
              <code className="gf-group-workspace__join-value">{group.join_code}</code>
              <button
                type="button"
                className="gf-group-workspace__copy-btn"
                onClick={handleCopyCode}
                aria-label={copied ? 'Copied code' : 'Copy join code'}
                title="Copy code to clipboard"
              >
                {copied ? (
                  <span className="gf-group-workspace__copied-text">Copied!</span>
                ) : (
                  <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        }
      />

      {/* Workspace Subnavigation Tabs */}
      <nav className="gf-group-workspace__tabs" aria-label="Cohort sections">
        <Link
          to={`/mentor/groups/${groupId}`}
          className="gf-group-workspace__tab gf-group-workspace__tab--active"
          aria-current="page"
        >
          Overview
        </Link>
        <Link
          to={`/mentor/groups/${groupId}/students`}
          className="gf-group-workspace__tab"
        >
          Students ({students.length})
        </Link>
        <Link
          to={`/mentor/groups/${groupId}/projects`}
          className="gf-group-workspace__tab"
        >
          Projects ({projects.length})
        </Link>
        <Link
          to={`/mentor/groups/${groupId}/at-risk`}
          className={`gf-group-workspace__tab ${
            atRiskProjects.length > 0 ? 'gf-group-workspace__tab--at-risk' : ''
          }`}
        >
          At-Risk ({atRiskProjects.length})
        </Link>
        <Link
          to={`/mentor/groups/${groupId}/activity`}
          className="gf-group-workspace__tab"
        >
          Activity
        </Link>
        <Link
          to={`/mentor/groups/${groupId}/ai`}
          className="gf-group-workspace__tab"
        >
          AI Mentor
        </Link>
      </nav>

      {/* Metrics Row */}
      <section className="gf-group-workspace__stats" aria-label="Cohort Summary">
        <StatTile
          label="Enrolled Students"
          value={students.length}
          subtext="Students in cohort"
        />
        <StatTile
          label="Linked Projects"
          value={projects.length}
          subtext="Active student projects"
        />
        <StatTile
          label="At-Risk Projects"
          value={atRiskProjects.length}
          subtext={atRiskProjects.length > 0 ? 'Action required' : 'All projects healthy'}
          tone={atRiskProjects.length > 0 ? 'warning' : 'success'}
        />
      </section>

      {/* Cohort Content Preview Grid */}
      <div className="gf-group-workspace__panels">
        {/* Students Preview */}
        <Card className="gf-group-workspace__panel">
          <div className="gf-group-workspace__panel-header">
            <div>
              <h2 className="gf-group-workspace__panel-title">Students Roster</h2>
              <p className="gf-group-workspace__panel-subtitle">Recently enrolled members</p>
            </div>
            <Button
              as="link"
              to={`/mentor/groups/${groupId}/students`}
              variant="tertiary"
              size="sm"
            >
              View All ({students.length}) &rarr;
            </Button>
          </div>

          {students.length === 0 ? (
            <div className="gf-group-workspace__empty-panel">
              <p>No students enrolled in this group yet.</p>
              <span className="gf-group-workspace__empty-hint">
                Provide code <strong>{group.join_code}</strong> to your students.
              </span>
            </div>
          ) : (
            <ul className="gf-group-workspace__roster-list" role="list">
              {students.slice(0, 5).map((s) => (
                <li key={s.student_id} className="gf-group-workspace__roster-item">
                  <div className="gf-group-workspace__roster-avatar" aria-hidden="true">
                    {(s.full_name?.[0] || s.email[0] || '?').toUpperCase()}
                  </div>
                  <div className="gf-group-workspace__roster-info">
                    <span className="gf-group-workspace__roster-name">
                      {s.full_name || s.email}
                    </span>
                    <span className="gf-group-workspace__roster-email">{s.email}</span>
                  </div>
                  <Badge variant={s.status === 'ACTIVE' ? 'success' : 'neutral'}>
                    {s.status}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Projects Preview */}
        <Card className="gf-group-workspace__panel">
          <div className="gf-group-workspace__panel-header">
            <div>
              <h2 className="gf-group-workspace__panel-title">Cohort Projects</h2>
              <p className="gf-group-workspace__panel-subtitle">Current phase & health distribution</p>
            </div>
            <Button
              as="link"
              to={`/mentor/groups/${groupId}/projects`}
              variant="tertiary"
              size="sm"
            >
              View All ({projects.length}) &rarr;
            </Button>
          </div>

          {projects.length === 0 ? (
            <div className="gf-group-workspace__empty-panel">
              <p>No student projects linked to this group yet.</p>
              <span className="gf-group-workspace__empty-hint">
                When enrolled students create projects, they will appear here.
              </span>
            </div>
          ) : (
            <ul className="gf-group-workspace__project-list" role="list">
              {projects.slice(0, 5).map((p) => (
                <li key={p.id} className="gf-group-workspace__project-item">
                  <div className="gf-group-workspace__project-info">
                    <span className="gf-group-workspace__project-name">{p.name}</span>
                    <div className="gf-group-workspace__project-meta">
                      <span className="gf-group-workspace__project-phase">{p.current_phase}</span>
                      <span className="gf-group-workspace__project-progress">
                        {p.progress_percentage}% complete
                      </span>
                    </div>
                  </div>
                  <Badge
                    variant={
                      p.health === 'HEALTHY'
                        ? 'success'
                        : p.health === 'ATTENTION'
                        ? 'accent'
                        : 'danger'
                    }
                  >
                    {p.health}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
