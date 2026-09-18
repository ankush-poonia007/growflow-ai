import { useState } from 'react';
import { useNavigate } from 'react-router';
import { createMentorDefinition } from '@/lib/api/client';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import './DefinitionCreate.css';

export function DefinitionCreate() {
  const navigate = useNavigate();

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
    if (!validate() || isSubmitting) return;

    try {
      setIsSubmitting(true);
      setServerError(null);

      const technology_snapshot = techInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
        .map((techName) => ({ name: techName }));

      const res = await createMentorDefinition({
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

      navigate(`/mentor/projects/${res.id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create project definition.';
      setServerError(msg);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="gf-definition-create" role="main" aria-labelledby="create-title">
      <PageHeader
        eyebrow="NEW TEMPLATE"
        title="Create Project Definition"
        description="Draft a new reusable project template. This will generate the initial Version 1 snapshot."
        breadcrumbs={[
          { label: 'Definitions', to: '/mentor/projects' },
          { label: 'New Definition' },
        ]}
      />

      {serverError && (
        <div className="gf-definition-create__server-error" role="alert">
          <strong>Error:</strong> {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="gf-definition-create__form" noValidate>
        <Card className="gf-definition-create__card">
          <h2 className="gf-definition-create__section-title">Core Identity & Specification</h2>

          <div className="gf-definition-create__field">
            <label htmlFor="def-name" className="gf-definition-create__label">
              Definition Name <span className="gf-definition-create__required">*</span>
            </label>
            <Input
              id="def-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Autonomous Solar-Powered Environmental Rover"
              aria-invalid={Boolean(errors.name)}
              aria-describedby={errors.name ? 'def-name-error' : undefined}
            />
            {errors.name && (
              <span id="def-name-error" className="gf-definition-create__field-error">
                {errors.name}
              </span>
            )}
          </div>

          <div className="gf-definition-create__field">
            <label htmlFor="def-problem" className="gf-definition-create__label">
              Problem Statement <span className="gf-definition-create__required">*</span>
            </label>
            <textarea
              id="def-problem"
              className={`gf-definition-form__textarea ${errors.problem ? 'gf-definition-form__textarea--error' : ''}`}
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              placeholder="Describe the concrete domain problem or challenge students are solving..."
              rows={4}
              aria-invalid={Boolean(errors.problem)}
              aria-describedby={errors.problem ? 'def-problem-error' : undefined}
            />
            {errors.problem && (
              <span id="def-problem-error" className="gf-definition-create__field-error">
                {errors.problem}
              </span>
            )}
          </div>

          <div className="gf-definition-create__field">
            <label htmlFor="def-solution" className="gf-definition-create__label">
              Proposed Solution <span className="gf-definition-create__required">*</span>
            </label>
            <textarea
              id="def-solution"
              className={`gf-definition-form__textarea ${errors.proposedSolution ? 'gf-definition-form__textarea--error' : ''}`}
              value={proposedSolution}
              onChange={(e) => setProposedSolution(e.target.value)}
              placeholder="Outline the architectural approach, technical design, or core system..."
              rows={4}
              aria-invalid={Boolean(errors.proposedSolution)}
              aria-describedby={errors.proposedSolution ? 'def-solution-error' : undefined}
            />
            {errors.proposedSolution && (
              <span id="def-solution-error" className="gf-definition-create__field-error">
                {errors.proposedSolution}
              </span>
            )}
          </div>

          <div className="gf-definition-create__field">
            <label htmlFor="def-description" className="gf-definition-create__label">
              Educational Objectives & Detailed Description
            </label>
            <textarea
              id="def-description"
              className="gf-definition-form__textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Key learning outcomes, deliverables, and student responsibilities..."
              rows={3}
            />
          </div>
        </Card>

        <Card className="gf-definition-create__card">
          <h2 className="gf-definition-create__section-title">Scope, Parameters & Technologies</h2>

          <div className="gf-definition-create__row">
            <div className="gf-definition-create__field gf-definition-create__field--half">
              <label htmlFor="def-complexity" className="gf-definition-create__label">
                Complexity Classification
              </label>
              <select
                id="def-complexity"
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

            <div className="gf-definition-create__field gf-definition-create__field--half">
              <label htmlFor="def-duration" className="gf-definition-create__label">
                Estimated Duration
              </label>
              <Input
                id="def-duration"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                placeholder="e.g., 8 weeks, 1 semester"
              />
            </div>
          </div>

          <div className="gf-definition-create__row">
            <div className="gf-definition-create__field gf-definition-create__field--half">
              <label htmlFor="def-constraints" className="gf-definition-create__label">
                Constraints
              </label>
              <textarea
                id="def-constraints"
                className="gf-definition-form__textarea"
                value={constraints}
                onChange={(e) => setConstraints(e.target.value)}
                placeholder="e.g., Budget limits, safety requirements, target hardware..."
                rows={3}
              />
            </div>

            <div className="gf-definition-create__field gf-definition-create__field--half">
              <label htmlFor="def-assumptions" className="gf-definition-create__label">
                Assumptions
              </label>
              <textarea
                id="def-assumptions"
                className="gf-definition-form__textarea"
                value={assumptions}
                onChange={(e) => setAssumptions(e.target.value)}
                placeholder="e.g., Lab access, internet connectivity, prerequisite skills..."
                rows={3}
              />
            </div>
          </div>

          <div className="gf-definition-create__field">
            <label htmlFor="def-tech" className="gf-definition-create__label">
              Initial Technologies (Comma-separated)
            </label>
            <Input
              id="def-tech"
              value={techInput}
              onChange={(e) => setTechInput(e.target.value)}
              placeholder="e.g., Python, ROS2, FastAPI, PostgreSQL, OpenCV"
            />
            <span className="gf-definition-create__field-hint">
              These will be pinned to Version 1 as recommended architectural technologies.
            </span>
          </div>
        </Card>

        {/* Actions Bar */}
        <div className="gf-definition-create__actions">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/mentor/projects')}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? 'Creating Version 1...' : 'Create Definition'}
          </Button>
        </div>
      </form>
    </div>
  );
}
