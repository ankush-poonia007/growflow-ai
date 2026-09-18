import { useState, useCallback, useRef, type FormEvent } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { ProjectStageIndicator } from './components/ProjectStageIndicator';
import { ProjectDefinitionForm } from './components/ProjectDefinitionForm';
import { ProjectSnapshot } from './components/ProjectSnapshot';
import { ProjectCreateSuccess } from './components/ProjectCreateSuccess';
import { ProjectCreateError } from './components/ProjectCreateError';
import { INITIAL_FORM_DATA, type ProjectFormData, type FormValidationErrors } from './types';
import { validateProjectForm, toCreatePayload, formatProjectCreateError } from './utils';
import { createProject } from '@/lib/api';
import type { ProjectResponse } from '@/lib/api/types';
import './StudentProjectCreate.css';

/**
 * S03 — Create Your Own Project
 *
 * Route: /student/projects/new
 * Protected: requiredRole="STUDENT" under AuthenticatedLayout.
 *
 * Allows students to define an independent project idea (name, problem, proposed solution,
 * complexity, technologies, target deadline) and commit it canonically to the backend via POST /api/v1/projects.
 *
 * Provides a live local project snapshot preview and transitions safely to confirmation
 * with next-stage Assessment guidance.
 */
export function StudentProjectCreate() {
  const [formData, setFormData] = useState<ProjectFormData>(INITIAL_FORM_DATA);
  const [errors, setErrors] = useState<FormValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [createdProject, setCreatedProject] = useState<ProjectResponse | null>(null);

  // Reference to error container for accessible focus management
  const errorContainerRef = useRef<HTMLDivElement>(null);

  // Field change handler that preserves all other form fields and clears related field error
  const handleChange = useCallback(
    <K extends keyof ProjectFormData>(key: K, value: ProjectFormData[K]) => {
      setFormData((prev) => ({ ...prev, [key]: value }));
      setErrors((prev) => {
        if (!prev[key]) return prev;
        const next = { ...prev };
        delete next[key];
        return next;
      });
      if (apiError) {
        setApiError(null);
      }
    },
    [apiError],
  );

  // Form submit handler with frontend validation and duplicate submission guard
  const handleSubmit = useCallback(
    async (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();

      // Duplicate submission protection: do nothing if already in flight
      if (isSubmitting) return;

      // 1. Validate frontend form state
      const validationErrors = validateProjectForm(formData);
      if (Object.keys(validationErrors).length > 0) {
        setErrors(validationErrors);
        return;
      }

      // 2. Clear previous errors and engage submitting state
      setErrors({});
      setApiError(null);
      setIsSubmitting(true);

      try {
        // 3. Dispatch canonical creation request via centralized API client
        const payload = toCreatePayload(formData);
        const response = await createProject(payload);

        // 4. On success, store the canonical created project instance
        setCreatedProject(response);
      } catch (err) {
        // 5. On error, preserve form state, format safe error message, allow retry
        const safeMessage = formatProjectCreateError(err);
        setApiError(safeMessage);
        if (typeof errorContainerRef.current?.scrollIntoView === 'function') {
          errorContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      } finally {
        setIsSubmitting(false);
      }
    },
    [formData, isSubmitting],
  );

  return (
    <main className="gf-project-create-page" aria-label="Create Your Own Project">
      {/* Page Header */}
      <PageHeader
        title="Create your own project"
        eyebrow="STUDENT / BUILD"
        description="Start with the problem you want to solve. GrowFlow will use this project definition as the foundation for the next stages of your build journey."
      />

      {/* Progression Orientation Cue */}
      <ProjectStageIndicator
        currentStep={createdProject ? 'assess' : isSubmitting ? 'create' : 'define'}
      />

      {/* Conditional: Success confirmation view OR Two-column definition form & live snapshot */}
      {createdProject ? (
        <div className="gf-project-create-success-wrapper">
          <ProjectCreateSuccess project={createdProject} />
        </div>
      ) : (
        <div className="gf-project-create-layout">
          {/* Left Column: Form and Alert */}
          <div className="gf-project-form-container">
            <div ref={errorContainerRef}>
              {apiError && <ProjectCreateError message={apiError} />}
            </div>
            <ProjectDefinitionForm
              formData={formData}
              errors={errors}
              isSubmitting={isSubmitting}
              onChange={handleChange}
              onSubmit={handleSubmit}
            />
          </div>

          {/* Right Column: Live Contextual Project Snapshot */}
          <aside className="gf-project-snapshot-column" aria-label="Live Project Snapshot">
            <ProjectSnapshot formData={formData} />
          </aside>
        </div>
      )}
    </main>
  );
}
