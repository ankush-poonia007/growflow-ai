import { useState, useEffect, useCallback, useMemo, type FormEvent } from 'react';
import { useParams } from 'react-router';
import type {
  ProjectResponse,
  ProjectOverviewResponse,
  ProjectDefinitionCatalogItem,
  AssessmentSessionStatus,
} from '@/lib/api/types';
import {
  getProject,
  getProjectOverview,
  getMentorProjectDefinition,
  updateProject,
  getAssessmentStatus,
} from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent, Badge, Button } from '@/components/ui';
import type {
  PageMode,
  ProjectProfileFormData,
  ProjectProfileFormErrors,
} from './types';
import {
  toFormData,
  toUpdatePayload,
  isFormDirty,
  validateProjectProfileForm,
} from './utils';
import { ProjectProfileHeader } from './components/ProjectProfileHeader';
import { ProjectIdentitySection } from './components/ProjectIdentitySection';
import { ProjectObjectiveSection } from './components/ProjectObjectiveSection';
import { ProjectTechnologySection } from './components/ProjectTechnologySection';
import { ProjectProvenanceSection } from './components/ProjectProvenanceSection';
import { ProjectSystemStateSection } from './components/ProjectSystemStateSection';
import { ProjectProfileEditForm } from './components/ProjectProfileEditForm';
import { ProjectProfileLoading } from './components/ProjectProfileLoading';
import { ProjectProfileError } from './components/ProjectProfileError';
import './StudentProjectProfile.css';

export function StudentProjectProfile() {
  const { projectId } = useParams<{ projectId: string }>();

  // Canonical server state
  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [overview, setOverview] = useState<ProjectOverviewResponse | null>(null);
  const [mentorDefinition, setMentorDefinition] =
    useState<ProjectDefinitionCatalogItem | null>(null);
  const [assessmentStatus, setAssessmentStatus] =
    useState<AssessmentSessionStatus | null>(null);

  // Loading & error lifecycle
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState<number>(0);

  // Profile view / edit mode
  const [mode, setMode] = useState<PageMode>('VIEW');
  const [formData, setFormData] = useState<ProjectProfileFormData>({
    name: '',
    problem: '',
    proposedSolution: '',
    complexity: 'INTERMEDIATE',
    deadline: '',
  });
  const [formErrors, setFormErrors] = useState<ProjectProfileFormErrors>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Fetch canonical project and provenance details
  useEffect(() => {
    let isMounted = true;

    if (!projectId) {
      setIsLoading(false);
      setLoadError('Invalid project identifier.');
      return;
    }

    setIsLoading(true);
    setLoadError(null);

    async function loadProjectData() {
      try {
        // 1. Authoritative primary project record
        const projectData = await getProject(projectId!);
        if (!isMounted) return;
        setProject(projectData);
        setFormData(toFormData(projectData));

        // 2. Supporting overview details (objective, technologies, days remaining)
        try {
          const overviewData = await getProjectOverview(projectId!);
          if (isMounted) {
            setOverview(overviewData);
          }
        } catch {
          if (isMounted) {
            setOverview(null);
          }
        }

        // 3. Mentor project definition provenance if linked
        if (projectData.project_definition_id) {
          try {
            const defData = await getMentorProjectDefinition(
              projectData.project_definition_id,
            );
            if (isMounted) {
              setMentorDefinition(defData);
            }
          } catch {
            if (isMounted) {
              setMentorDefinition(null);
            }
          }
        } else {
          if (isMounted) {
            setMentorDefinition(null);
          }
        }

        // 4. Assessment workflow status (S06 Integration for S07-S11)
        try {
          const assessmentData = await getAssessmentStatus(projectId!);
          if (isMounted) {
            setAssessmentStatus(assessmentData);
          }
        } catch {
          if (isMounted) {
            setAssessmentStatus(null);
          }
        }
      } catch (err: unknown) {
        if (!isMounted) return;
        const msg =
          err instanceof Error
            ? err.message
            : 'Unable to connect to the GrowFlow workspace service.';
        setLoadError(msg);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadProjectData();

    return () => {
      isMounted = false;
    };
  }, [projectId, retryKey]);

  const handleRetry = useCallback(() => {
    setRetryKey((prev) => prev + 1);
  }, []);

  // Enter edit mode
  const handleEnterEditMode = useCallback(() => {
    if (!project) return;
    setFormData(toFormData(project));
    setFormErrors({});
    setApiError(null);
    setMode('EDIT');
  }, [project]);

  // Cancel edit mode and restore canonical state
  const handleCancelEditMode = useCallback(() => {
    if (!project) return;
    setFormData(toFormData(project));
    setFormErrors({});
    setApiError(null);
    setMode('VIEW');
  }, [project]);

  // Form field update
  const handleFormChange = useCallback(
    <K extends keyof ProjectProfileFormData>(key: K, value: ProjectProfileFormData[K]) => {
      setFormData((prev) => ({ ...prev, [key]: value }));
      setFormErrors((prev) => ({ ...prev, [key]: undefined }));
      setApiError(null);
    },
    [],
  );

  // Check if form has unsaved modifications
  const isDirty = useMemo(() => {
    if (!project) return false;
    return isFormDirty(formData, project);
  }, [formData, project]);

  // Submit edit form
  const handleFormSubmit = useCallback(
    async (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!projectId || !project || isSubmitting || !isDirty) return;

      // 1. Frontend validation
      const validationErrors = validateProjectProfileForm(formData);
      if (Object.keys(validationErrors).length > 0) {
        setFormErrors(validationErrors);
        return;
      }

      setFormErrors({});
      setApiError(null);
      setIsSubmitting(true);

      try {
        // 2. Dispatch update to canonical backend endpoint
        const payload = toUpdatePayload(formData);
        const updated = await updateProject(projectId, payload);

        // 3. Reconcile with persisted backend response
        setProject(updated);
        setFormData(toFormData(updated));

        // Update overview with matching name/problem/solution if present
        setOverview((prev) =>
          prev
            ? {
                ...prev,
                name: updated.name,
                problem: updated.problem,
                proposed_solution: updated.proposed_solution,
                complexity: updated.complexity || prev.complexity,
                deadline: updated.deadline,
              }
            : null,
        );

        setMode('VIEW');
      } catch (err: unknown) {
        const msg =
          err instanceof Error
            ? err.message
            : 'Unable to save changes. Please review your input and try again.';
        setApiError(msg);
      } finally {
        setIsSubmitting(false);
      }
    },
    [projectId, project, isSubmitting, isDirty, formData],
  );

  // 1. Loading State
  if (isLoading) {
    return (
      <main className="gf-profile-page" aria-label="Loading Project Profile">
        <ProjectProfileLoading />
      </main>
    );
  }

  // 2. Error State (404, 403, 422, Network / 5xx)
  if (loadError || !project) {
    return (
      <main className="gf-profile-page" aria-label="Project Profile Error">
        <ProjectProfileError error={loadError} onRetry={handleRetry} />
      </main>
    );
  }

  // 3. Render Profile
  return (
    <main className="gf-profile-page" aria-label={`Project Profile: ${project.name}`}>
      {/* Authoritative Header */}
      <ProjectProfileHeader
        project={project}
        mode={mode}
        onEnterEditMode={handleEnterEditMode}
        onCancelEditMode={handleCancelEditMode}
        assessmentStatus={assessmentStatus}
      />

      {/* Main Content: Edit Mode OR View Mode */}
      {mode === 'EDIT' ? (
        <ProjectProfileEditForm
          formData={formData}
          errors={formErrors}
          apiError={apiError}
          isSubmitting={isSubmitting}
          isDirty={isDirty}
          onChange={handleFormChange}
          onSubmit={handleFormSubmit}
          onCancel={handleCancelEditMode}
        />
      ) : (
        <div className="gf-profile-content-layout">
          {/* Identity & Scope */}
          <ProjectIdentitySection project={project} overview={overview} />

          {/* Stage 2 Technical Assessment Gateway (S06 Integration for S07-S11) */}
          <Card
            as="section"
            className="gf-profile-section gf-profile-section--assessment"
            variant="bordered"
            aria-label="Stage 2 Technical Assessment Gateway"
          >
            <CardHeader className="gf-profile-section__header">
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  width: '100%',
                  marginBottom: '0.25rem',
                }}
              >
                <Badge variant="accent">Stage 2 Gate</Badge>
                <Badge
                  variant={
                    assessmentStatus?.status === 'COMPLETED'
                      ? 'success'
                      : assessmentStatus?.status === 'IN_PROGRESS'
                      ? 'accent'
                      : 'neutral'
                  }
                >
                  {assessmentStatus?.status === 'COMPLETED'
                    ? 'Completed'
                    : assessmentStatus?.status === 'IN_PROGRESS'
                    ? `In Progress (${assessmentStatus.current_question_index} of ${assessmentStatus.total_questions})`
                    : 'Not Started'}
                </Badge>
              </div>
              <CardTitle as="h2" className="gf-profile-section__title">
                Technical Readiness Assessment
              </CardTitle>
              <p className="gf-profile-section__subtitle">
                {assessmentStatus?.status === 'COMPLETED'
                  ? 'Your technical readiness evaluation is complete. View your synthesized readiness profile, dimensional scores, and recommendations.'
                  : assessmentStatus?.status === 'IN_PROGRESS'
                  ? `You have an active assessment in progress. Currently on question ${assessmentStatus.current_question_index} of ${assessmentStatus.total_questions}.`
                  : 'Evaluate technical feasibility, architectural patterns, and design trade-offs before proceeding to Stage 3 Blueprinting.'}
              </p>
            </CardHeader>
            <CardContent className="gf-profile-section__body">
              <Button
                as="link"
                to={`/student/projects/${project.id}/assessment`}
                variant="primary"
                size="md"
                id="profile-assessment-gateway-btn"
              >
                {assessmentStatus?.status === 'COMPLETED'
                  ? 'View Assessment Results →'
                  : assessmentStatus?.status === 'IN_PROGRESS'
                  ? 'Continue Assessment →'
                  : 'Start Assessment →'}
              </Button>
            </CardContent>
          </Card>

          {/* Objectives, Scope, Constraints & Assumptions */}
          <ProjectObjectiveSection profile={overview?.profile} />

          {/* Technologies */}
          <ProjectTechnologySection technologies={overview?.technologies} />

          {/* Origin & Provenance */}
          <ProjectProvenanceSection
            project={project}
            mentorDefinition={mentorDefinition}
          />

          {/* Operational & Lifecycle State (System-Controlled) */}
          <ProjectSystemStateSection project={project} />
        </div>
      )}
    </main>
  );
}
