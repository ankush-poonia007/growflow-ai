import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router';
import { getMentorDefinition, updateMentorDefinition } from '@/lib/api/client';
import type { ProjectDefinition } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import './DefinitionEdit.css';

export function DefinitionEdit() {
  const { definitionId } = useParams<{ definitionId: string }>();
  const navigate = useNavigate();

  const [definition, setDefinition] = useState<ProjectDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [name, setName] = useState('');
  const [problem, setProblem] = useState('');
  const [proposedSolution, setProposedSolution] = useState('');
  const [complexity, setComplexity] = useState('INTERMEDIATE');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState('');
  const [constraints, setConstraints] = useState('');
  const [assumptions, setAssumptions] = useState('');
  const [techInput, setTechInput] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState<string | null>(null);

  useEffect(() => {
    if (!definitionId) return;

    async function load() {
      try {
        setLoading(true);
        setLoadError(null);
        const data = await getMentorDefinition(definitionId!);
        setDefinition(data);
        setName(data.name || '');

        const v = data.current_version;
        if (v) {
          setProblem(v.problem || '');
          setProposedSolution(v.proposed_solution || '');
          setComplexity(v.complexity || 'INTERMEDIATE');
          setDescription(v.description || '');
          setDuration(v.duration || '');
          setConstraints(v.constraints || '');
          setAssumptions(v.assumptions || '');

          if (v.technology_snapshot && Array.isArray(v.technology_snapshot)) {
            const names = v.technology_snapshot
              .map((t) => t.name || t.label || t.title)
              .filter(Boolean)
              .join(', ');
            setTechInput(names);
          }
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to load definition for editing.';
        setLoadError(msg);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [definitionId]);

  function validate() {
    const nextErrors: Record<string, string> = {};
    if (!name.trim()) {
      nextErrors.name = 'Project definition name is required.';
    } else if (name.trim().length > 255) {
      nextErrors.name = 'Name must be 255 characters or fewer.';
    }

    if (!problem.trim()) {
      nextErrors.problem = 'Problem statement is required.';
    }

    if (!proposedSolution.trim()) {
      nextErrors.proposedSolution = 'Proposed solution is required.';
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!definitionId || !validate() || isSubmitting) return;

    try {
      setIsSubmitting(true);
      setServerError(null);

      const technology_snapshot = techInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
        .map((techName) => ({ name: techName }));

      await updateMentorDefinition(definitionId, {
        name: name.trim(),
        problem: problem.trim(),
        proposed_solution: proposedSolution.trim(),
        complexity,
        description: description.trim(),
        duration: duration.trim(),
        constraints: constraints.trim(),
        assumptions: assumptions.trim(),
        technology_snapshot,
      });

      navigate(`/mentor/projects/${definitionId}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update definition.';
      setServerError(msg);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="gf-definition-edit gf-definition-edit--loading" aria-busy="true">
        <Skeleton height="60px" />
        <Skeleton height="320px" />
        <Skeleton height="240px" />
      </div>
    );
  }

  if (loadError || !definition) {
    return (
      <div className="gf-definition-edit gf-definition-edit--error" role="alert">
        <Card className="gf-definition-edit__error-card">
          <h2>Unable to Load Definition for Editing</h2>
          <p>{loadError || 'The definition was not found or access is unauthorized.'}</p>
          <Button as="link" to="/mentor/projects" variant="secondary">
            Back to Definitions
          </Button>
        </Card>
      </div>
    );
  }

  const curVerNum = definition.current_version?.version_number ?? 1;
  const nextVerNum = curVerNum + 1;

  return (
    <div className="gf-definition-edit" role="main" aria-labelledby="edit-title">
      <PageHeader
        eyebrow="VERSIONED EDIT"
        title={`Edit Definition: ${definition.name}`}
        description={`Current version is v${curVerNum}. Submitting changes will publish v${nextVerNum}.`}
        breadcrumbs={[
          { label: 'Definitions', to: '/mentor/projects' },
          { label: definition.name, to: `/mentor/projects/${definition.id}` },
          { label: 'Edit' },
        ]}
      />

      {/* Versioning Immutability Notice Banner */}
      <div className="gf-definition-edit__version-notice" role="note">
        <div className="gf-definition-edit__version-notice-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
        </div>
        <div className="gf-definition-edit__version-notice-content">
          <h2 className="gf-definition-edit__version-notice-title">
            Versioning Immutability Guarantee
          </h2>
          <p className="gf-definition-edit__version-notice-desc">
            Saving these changes will create an immutable new version (<strong>v{nextVerNum}</strong>) and set it as current.
            Existing Student Project Instances created under <strong>v{curVerNum}</strong> or prior versions remain completely frozen
            and will not be altered.
          </p>
        </div>
      </div>

      {serverError && (
        <div className="gf-definition-edit__server-error" role="alert">
          <strong>Error:</strong> {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="gf-definition-edit__form" noValidate>
        <Card className="gf-definition-edit__card">
          <h2 className="gf-definition-edit__section-title">Core Identity & Specification</h2>

          <div className="gf-definition-edit__field">
            <label htmlFor="edit-def-name" className="gf-definition-edit__label">
              Definition Name <span className="gf-definition-edit__required">*</span>
            </label>
            <Input
              id="edit-def-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Autonomous Precision Agriculture Drone"
              aria-invalid={Boolean(errors.name)}
              aria-describedby={errors.name ? 'edit-def-name-error' : undefined}
            />
            {errors.name && (
              <span id="edit-def-name-error" className="gf-definition-edit__field-error">
                {errors.name}
              </span>
            )}
          </div>

          <div className="gf-definition-edit__field">
            <label htmlFor="edit-def-problem" className="gf-definition-edit__label">
              Problem Statement <span className="gf-definition-edit__required">*</span>
            </label>
            <textarea
              id="edit-def-problem"
              className={`gf-definition-form__textarea ${errors.problem ? 'gf-definition-form__textarea--error' : ''}`}
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              placeholder="Describe the domain problem students are solving..."
              rows={4}
              aria-invalid={Boolean(errors.problem)}
              aria-describedby={errors.problem ? 'edit-def-problem-error' : undefined}
            />
            {errors.problem && (
              <span id="edit-def-problem-error" className="gf-definition-edit__field-error">
                {errors.problem}
              </span>
            )}
          </div>

          <div className="gf-definition-edit__field">
            <label htmlFor="edit-def-solution" className="gf-definition-edit__label">
              Proposed Solution <span className="gf-definition-edit__required">*</span>
            </label>
            <textarea
              id="edit-def-solution"
              className={`gf-definition-form__textarea ${errors.proposedSolution ? 'gf-definition-form__textarea--error' : ''}`}
              value={proposedSolution}
              onChange={(e) => setProposedSolution(e.target.value)}
              placeholder="Outline the architectural approach, technical design, or core system..."
              rows={4}
              aria-invalid={Boolean(errors.proposedSolution)}
              aria-describedby={errors.proposedSolution ? 'edit-def-solution-error' : undefined}
            />
            {errors.proposedSolution && (
              <span id="edit-def-solution-error" className="gf-definition-edit__field-error">
                {errors.proposedSolution}
              </span>
            )}
          </div>

          <div className="gf-definition-edit__field">
            <label htmlFor="edit-def-description" className="gf-definition-edit__label">
              Educational Objectives & Detailed Description
            </label>
            <textarea
              id="edit-def-description"
              className="gf-definition-form__textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Key learning outcomes, deliverables, and student responsibilities..."
              rows={3}
            />
          </div>
        </Card>

        <Card className="gf-definition-edit__card">
          <h2 className="gf-definition-edit__section-title">Scope, Parameters & Technologies</h2>

          <div className="gf-definition-edit__row">
            <div className="gf-definition-edit__field gf-definition-edit__field--half">
              <label htmlFor="edit-def-complexity" className="gf-definition-edit__label">
                Complexity Classification
              </label>
              <select
                id="edit-def-complexity"
                className="gf-definition-form__select"
                value={complexity}
                onChange={(e) => setComplexity(e.target.value)}
                aria-label="Complexity Classification"
              >
                <option value="BEGINNER">Beginner — Foundational skills</option>
                <option value="INTERMEDIATE">Intermediate — Standard engineering</option>
                <option value="ADVANCED">Advanced — Complex architecture & systems</option>
              </select>
            </div>

            <div className="gf-definition-edit__field gf-definition-edit__field--half">
              <label htmlFor="edit-def-duration" className="gf-definition-edit__label">
                Estimated Duration
              </label>
              <Input
                id="edit-def-duration"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                placeholder="e.g., 8 weeks, 1 semester"
              />
            </div>
          </div>

          <div className="gf-definition-edit__row">
            <div className="gf-definition-edit__field gf-definition-edit__field--half">
              <label htmlFor="edit-def-constraints" className="gf-definition-edit__label">
                Constraints
              </label>
              <textarea
                id="edit-def-constraints"
                className="gf-definition-form__textarea"
                value={constraints}
                onChange={(e) => setConstraints(e.target.value)}
                placeholder="e.g., Budget limits, safety requirements, target hardware..."
                rows={3}
              />
            </div>

            <div className="gf-definition-edit__field gf-definition-edit__field--half">
              <label htmlFor="edit-def-assumptions" className="gf-definition-edit__label">
                Assumptions
              </label>
              <textarea
                id="edit-def-assumptions"
                className="gf-definition-form__textarea"
                value={assumptions}
                onChange={(e) => setAssumptions(e.target.value)}
                placeholder="e.g., Lab access, internet connectivity, prerequisite skills..."
                rows={3}
              />
            </div>
          </div>

          <div className="gf-definition-edit__field">
            <label htmlFor="edit-def-tech" className="gf-definition-edit__label">
              Recommended Technologies (Comma-separated)
            </label>
            <Input
              id="edit-def-tech"
              value={techInput}
              onChange={(e) => setTechInput(e.target.value)}
              placeholder="e.g., Python, ROS2, FastAPI, PostgreSQL"
            />
            <span className="gf-definition-edit__field-hint">
              These will be pinned to Version {nextVerNum} as recommended technologies.
            </span>
          </div>
        </Card>

        {/* Actions Bar */}
        <div className="gf-definition-edit__actions">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate(`/mentor/projects/${definitionId}`)}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? `Publishing v${nextVerNum}...` : `Save & Publish Version ${nextVerNum}`}
          </Button>
        </div>
      </form>
    </div>
  );
}
