import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router';
import {
  getMentorDefinition,
  getMentorGroups,
  getGroupStudents,
  assignMentorDefinition,
} from '@/lib/api/client';
import type {
  ProjectDefinition,
  GroupResponse,
  GroupStudentResponse,
  ProjectResponse,
} from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import './DefinitionAssign.css';

export function DefinitionAssign() {
  const { definitionId } = useParams<{ definitionId: string }>();
  const navigate = useNavigate();

  const [definition, setDefinition] = useState<ProjectDefinition | null>(null);
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string>('');
  const [students, setStudents] = useState<GroupStudentResponse[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [deadline, setDeadline] = useState<string>('');

  const [loadingInitial, setLoadingInitial] = useState(true);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [confirmed, setConfirmed] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [successResult, setSuccessResult] = useState<ProjectResponse | null>(null);

  useEffect(() => {
    if (!definitionId) return;

    async function init() {
      try {
        setLoadingInitial(true);
        setError(null);
        const [defRes, groupsRes] = await Promise.all([
          getMentorDefinition(definitionId!),
          getMentorGroups(),
        ]);
        setDefinition(defRes);
        setGroups(groupsRes);
        if (groupsRes.length > 0 && groupsRes[0]) {
          setSelectedGroupId(groupsRes[0].id);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to load assignment context.';
        setError(msg);
      } finally {
        setLoadingInitial(false);
      }
    }

    init();
  }, [definitionId]);

  useEffect(() => {
    if (!selectedGroupId) {
      setStudents([]);
      setSelectedStudentId('');
      return;
    }

    async function loadStudents() {
      try {
        setLoadingStudents(true);
        const memberList = await getGroupStudents(selectedGroupId);
        setStudents(memberList);
        if (memberList.length > 0 && memberList[0]) {
          setSelectedStudentId(memberList[0].student_id);
        } else {
          setSelectedStudentId('');
        }
      } catch (err: unknown) {
        console.error('Failed to load group students:', err);
        setStudents([]);
        setSelectedStudentId('');
      } finally {
        setLoadingStudents(false);
      }
    }

    loadStudents();
  }, [selectedGroupId]);

  async function handleAssign(e: React.FormEvent) {
    e.preventDefault();
    if (!definitionId || !selectedStudentId || isSubmitting || !confirmed) return;

    try {
      setIsSubmitting(true);
      setError(null);

      const assignedProject = await assignMentorDefinition(definitionId, {
        student_id: selectedStudentId,
        group_id: selectedGroupId || null,
        deadline: deadline ? new Date(deadline).toISOString() : null,
      });

      setSuccessResult(assignedProject);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to assign project definition.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (loadingInitial) {
    return (
      <div className="gf-definition-assign gf-definition-assign--loading" aria-busy="true">
        <Skeleton height="60px" />
        <Skeleton height="180px" />
        <Skeleton height="280px" />
      </div>
    );
  }

  if (!definition) {
    return (
      <div className="gf-definition-assign gf-definition-assign--error" role="alert">
        <Card className="gf-definition-assign__error-card">
          <h2>Definition Not Found</h2>
          <p>{error || 'The requested project definition could not be located.'}</p>
          <Button as="link" to="/mentor/projects" variant="secondary">
            Back to Definitions
          </Button>
        </Card>
      </div>
    );
  }

  const curVer = definition.current_version;
  const verNum = curVer?.version_number ?? 1;
  const selectedStudent = students.find((s) => s.student_id === selectedStudentId);
  const selectedGroup = groups.find((g) => g.id === selectedGroupId);

  return (
    <div className="gf-definition-assign" role="main" aria-labelledby="assign-title">
      <PageHeader
        eyebrow="SUPERVISED ASSIGNMENT"
        title={`Assign: ${definition.name}`}
        description="Instantiate an independent student project from this template within your supervised cohorts."
        breadcrumbs={[
          { label: 'Definitions', to: '/mentor/projects' },
          { label: definition.name, to: `/mentor/projects/${definition.id}` },
          { label: 'Assign' },
        ]}
      />

      {error && (
        <div className="gf-definition-assign__error-banner" role="alert">
          <div className="gf-definition-assign__error-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="8" />
            </svg>
          </div>
          <div className="gf-definition-assign__error-text">
            <strong>Assignment Notice:</strong> {error}
          </div>
        </div>
      )}

      {successResult ? (
        <Card className="gf-definition-assign__success-card">
          <div className="gf-definition-assign__success-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h2 className="gf-definition-assign__success-title">Project Successfully Assigned</h2>
          <p className="gf-definition-assign__success-desc">
            An independent operational project instance was created for{' '}
            <strong>{selectedStudent?.full_name || selectedStudent?.email || 'the student'}</strong>{' '}
            pinned to <strong>Version {verNum}</strong>.
          </p>
          <div className="gf-definition-assign__success-meta">
            <span>Project Name: <strong>{successResult.name}</strong></span>
            <span>Current Phase: <strong>{successResult.current_phase}</strong></span>
            <span>Health: <strong>{successResult.health}</strong></span>
          </div>
          <div className="gf-definition-assign__success-actions">
            <Button
              as="link"
              to={`/mentor/groups/${selectedGroupId}/projects`}
              variant="primary"
            >
              View in Group Workspace
            </Button>
            <Button as="link" to="/mentor/projects" variant="secondary">
              Back to Project Definitions
            </Button>
          </div>
        </Card>
      ) : (
        <form onSubmit={handleAssign} className="gf-definition-assign__form">
          {/* Summary Card */}
          <Card className="gf-definition-assign__card">
            <h2 className="gf-definition-assign__section-title">Selected Template Snapshot</h2>
            <div className="gf-definition-assign__snapshot-details">
              <div className="gf-definition-assign__snapshot-header">
                <span className="gf-definition-assign__snapshot-name">{definition.name}</span>
                <div className="gf-definition-assign__snapshot-badges">
                  <Badge variant="accent" size="sm">
                    Version {verNum}
                  </Badge>
                  <Badge variant="neutral" size="sm">
                    {curVer?.complexity || 'INTERMEDIATE'}
                  </Badge>
                </div>
              </div>
              <p className="gf-definition-assign__snapshot-problem">
                {curVer?.problem || 'No problem statement.'}
              </p>
            </div>
          </Card>

          {/* Scope & Target Card */}
          <Card className="gf-definition-assign__card">
            <h2 className="gf-definition-assign__section-title">Supervised Target Scope</h2>

            {groups.length === 0 ? (
              <div className="gf-definition-assign__no-groups">
                <p>You have not created any active student groups/cohorts yet.</p>
                <Button as="link" to="/mentor/groups/new" variant="primary" size="sm">
                  Create a Cohort Group First
                </Button>
              </div>
            ) : (
              <>
                <div className="gf-definition-assign__field">
                  <label htmlFor="assign-group-select" className="gf-definition-assign__label">
                    Target Cohort Group
                  </label>
                  <select
                    id="assign-group-select"
                    className="gf-definition-assign__select"
                    value={selectedGroupId}
                    onChange={(e) => setSelectedGroupId(e.target.value)}
                    aria-label="Target Cohort Group"
                  >
                    {groups.map((g) => (
                      <option key={g.id} value={g.id}>
                        {g.name} ({g.join_code})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="gf-definition-assign__field">
                  <label htmlFor="assign-student-select" className="gf-definition-assign__label">
                    Target Student {loadingStudents && '(Loading students...)'}
                  </label>
                  {students.length === 0 ? (
                    <p className="gf-definition-assign__no-students">
                      No active students found in this cohort group. Share the cohort join code{' '}
                      <strong>{selectedGroup?.join_code}</strong> with students to enroll them.
                    </p>
                  ) : (
                    <select
                      id="assign-student-select"
                      className="gf-definition-assign__select"
                      value={selectedStudentId}
                      onChange={(e) => setSelectedStudentId(e.target.value)}
                      aria-label="Target Student"
                    >
                      {students.map((s) => (
                        <option key={s.student_id} value={s.student_id}>
                          {s.full_name ? `${s.full_name} (${s.email})` : s.email}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                <div className="gf-definition-assign__field">
                  <label htmlFor="assign-deadline" className="gf-definition-assign__label">
                    Target Completion Deadline (Optional)
                  </label>
                  <Input
                    id="assign-deadline"
                    type="date"
                    value={deadline}
                    onChange={(e) => setDeadline(e.target.value)}
                  />
                </div>
              </>
            )}
          </Card>

          {/* Immutability & Consequence Confirmation Card */}
          <Card className="gf-definition-assign__card gf-definition-assign__card--confirmation">
            <h2 className="gf-definition-assign__section-title">Assignment Safety Confirmation</h2>
            <p className="gf-definition-assign__confirmation-desc">
              Assigning will initialize a new independent operational project instance for{' '}
              <strong>{selectedStudent?.full_name || selectedStudent?.email || 'the selected student'}</strong>{' '}
              pinned to <strong>Version {verNum}</strong>.
            </p>
            <div className="gf-definition-assign__checkbox-row">
              <input
                type="checkbox"
                id="assign-confirm-checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
                className="gf-definition-assign__checkbox"
                disabled={!selectedStudentId || isSubmitting}
              />
              <label htmlFor="assign-confirm-checkbox" className="gf-definition-assign__checkbox-label">
                I understand that this action creates a new student project instance and that existing student work
                is never overwritten or mutated.
              </label>
            </div>
          </Card>

          {/* Action Bar */}
          <div className="gf-definition-assign__actions">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate(`/mentor/projects/${definitionId}`)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={!selectedStudentId || !confirmed || isSubmitting}
            >
              {isSubmitting ? 'Assigning Project...' : 'Confirm & Assign Project'}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}
