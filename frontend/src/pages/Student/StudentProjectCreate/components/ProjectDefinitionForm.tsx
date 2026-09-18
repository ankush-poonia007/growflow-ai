import type { ChangeEvent, FormEvent } from 'react';
import type { ProjectFormData, FormValidationErrors } from '../types';
import { COMPLEXITY_OPTIONS } from '../types';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

interface ProjectDefinitionFormProps {
  formData: ProjectFormData;
  errors: FormValidationErrors;
  isSubmitting: boolean;
  onChange: <K extends keyof ProjectFormData>(key: K, value: ProjectFormData[K]) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
}

export function ProjectDefinitionForm({
  formData,
  errors,
  isSubmitting,
  onChange,
  onSubmit,
}: ProjectDefinitionFormProps) {
  const handleNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange('name', e.target.value);
  };

  const handleProblemChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange('problem', e.target.value);
  };

  const handleSolutionChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange('proposedSolution', e.target.value);
  };

  const handleComplexityChange = (val: ProjectFormData['complexity']) => {
    onChange('complexity', val);
  };

  const handleTechnologiesChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange('technologies', e.target.value);
  };

  const handleDeadlineChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange('deadline', e.target.value);
  };

  return (
    <form
      className="gf-project-form"
      onSubmit={onSubmit}
      noValidate
      aria-label="Project Definition Form"
    >
      {/* 1. Project Name */}
      <div className="gf-project-form__field">
        <Input
          id="project-name"
          name="name"
          label="Project Name"
          required
          placeholder="e.g. Autonomous Solar Rover"
          value={formData.name}
          onChange={handleNameChange}
          error={errors.name}
          helperText="Give your project a name that you can recognize throughout the build journey."
          maxLength={255}
          disabled={isSubmitting}
          rightAddon={
            <span className="gf-project-form__char-count" aria-live="polite">
              {formData.name.length}/255
            </span>
          }
        />
      </div>

      {/* 2. Problem Statement */}
      <div className="gf-project-form__field">
        <label htmlFor="project-problem" className="gf-project-form__label">
          Problem Statement <span className="gf-project-form__optional">(Recommended)</span>
        </label>
        <p id="project-problem-helper" className="gf-project-form__helper">
          What problem are you trying to solve, and who experiences it?
        </p>
        <textarea
          id="project-problem"
          name="problem"
          className={`gf-project-form__textarea ${errors.problem ? 'gf-project-form__textarea--error' : ''}`}
          placeholder="Describe the real-world problem, user friction, or technical bottleneck..."
          rows={4}
          value={formData.problem}
          onChange={handleProblemChange}
          aria-describedby="project-problem-helper"
          aria-invalid={Boolean(errors.problem)}
          disabled={isSubmitting}
        />
        {errors.problem && (
          <p className="gf-project-form__field-error" role="alert">
            {errors.problem}
          </p>
        )}
      </div>

      {/* 3. Proposed Solution */}
      <div className="gf-project-form__field">
        <label htmlFor="project-solution" className="gf-project-form__label">
          Proposed Solution <span className="gf-project-form__optional">(Recommended)</span>
        </label>
        <p id="project-solution-helper" className="gf-project-form__helper">
          Describe the solution you want to explore. It does not need to be final.
        </p>
        <textarea
          id="project-solution"
          name="proposedSolution"
          className={`gf-project-form__textarea ${errors.proposedSolution ? 'gf-project-form__textarea--error' : ''}`}
          placeholder="Outline the core concept, proposed architecture, or prototype approach..."
          rows={4}
          value={formData.proposedSolution}
          onChange={handleSolutionChange}
          aria-describedby="project-solution-helper"
          aria-invalid={Boolean(errors.proposedSolution)}
          disabled={isSubmitting}
        />
        {errors.proposedSolution && (
          <p className="gf-project-form__field-error" role="alert">
            {errors.proposedSolution}
          </p>
        )}
      </div>

      {/* 4. Complexity Level */}
      <fieldset className="gf-project-form__fieldset">
        <legend className="gf-project-form__legend">
          Target Complexity <span className="gf-project-form__required">*</span>
        </legend>
        <p id="complexity-helper" className="gf-project-form__helper">
          Indicate the expected architectural and implementation scope for this project.
        </p>
        <div
          className="gf-project-form__complexity-grid"
          role="radiogroup"
          aria-describedby="complexity-helper"
        >
          {COMPLEXITY_OPTIONS.map((opt) => {
            const isSelected = formData.complexity === opt.value;
            return (
              <label
                key={opt.value}
                className={`gf-project-form__complexity-card ${
                  isSelected ? 'gf-project-form__complexity-card--selected' : ''
                }`}
              >
                <input
                  type="radio"
                  name="complexity"
                  value={opt.value}
                  checked={isSelected}
                  onChange={() => handleComplexityChange(opt.value)}
                  className="sr-only"
                  disabled={isSubmitting}
                />
                <div className="gf-project-form__complexity-header">
                  <span className="gf-project-form__complexity-indicator" aria-hidden="true">
                    {isSelected && <span className="gf-project-form__complexity-dot" />}
                  </span>
                  <span className="gf-project-form__complexity-title">{opt.label}</span>
                </div>
                <p className="gf-project-form__complexity-desc">{opt.description}</p>
              </label>
            );
          })}
        </div>
        {errors.complexity && (
          <p className="gf-project-form__field-error" role="alert">
            {errors.complexity}
          </p>
        )}
      </fieldset>

      {/* 5. Technical Stack Direction (Optional) */}
      <div className="gf-project-form__field">
        <Input
          id="project-technologies"
          name="technologies"
          label="Initial Technologies"
          placeholder="e.g. React, Python, PostgreSQL, ROS2"
          value={formData.technologies}
          onChange={handleTechnologiesChange}
          helperText="Comma-separated technologies or frameworks you intend to evaluate."
          disabled={isSubmitting}
        />
      </div>

      {/* 6. Target Deadline (Optional) */}
      <div className="gf-project-form__field">
        <Input
          id="project-deadline"
          name="deadline"
          type="date"
          label="Target Milestone Deadline"
          value={formData.deadline}
          onChange={handleDeadlineChange}
          error={errors.deadline}
          helperText="Optional target completion date for your build journey."
          disabled={isSubmitting}
        />
      </div>

      {/* Form Action Controls */}
      <div className="gf-project-form__actions">
        <Button
          as="button"
          type="submit"
          variant="primary"
          size="lg"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Creating project…' : 'Create project'}
        </Button>
        <Button
          as="link"
          to="/student/projects"
          variant="secondary"
          size="lg"
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
