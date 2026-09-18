import type { ChangeEvent, FormEvent } from 'react';
import type { ProjectProfileFormData, ProjectProfileFormErrors } from '../types';
import { COMPLEXITY_OPTIONS } from '../types';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';

interface ProjectProfileEditFormProps {
  formData: ProjectProfileFormData;
  errors: ProjectProfileFormErrors;
  apiError?: string | null;
  isSubmitting: boolean;
  isDirty: boolean;
  onChange: <K extends keyof ProjectProfileFormData>(
    key: K,
    value: ProjectProfileFormData[K],
  ) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
}

export function ProjectProfileEditForm({
  formData,
  errors,
  apiError,
  isSubmitting,
  isDirty,
  onChange,
  onSubmit,
  onCancel,
}: ProjectProfileEditFormProps) {
  const handleNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange('name', e.target.value);
  };

  const handleProblemChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange('problem', e.target.value);
  };

  const handleSolutionChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange('proposedSolution', e.target.value);
  };

  const handleComplexityChange = (val: ProjectProfileFormData['complexity']) => {
    onChange('complexity', val);
  };

  const handleDeadlineChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange('deadline', e.target.value);
  };

  return (
    <Card
      as="section"
      className="gf-profile-edit-card"
      variant="bordered"
      aria-label="Edit Project Information"
    >
      <CardHeader className="gf-profile-edit-card__header">
        <div className="gf-profile-edit-card__header-top">
          <CardTitle as="h2" className="gf-profile-edit-card__title">
            Edit Project Information
          </CardTitle>
          <span className="gf-profile-edit-card__mode-tag">EDIT MODE</span>
        </div>
        <p className="gf-profile-edit-card__subtitle">
          Update the canonical definition, problem formulation, and target milestones for this
          project instance.
        </p>
      </CardHeader>

      <form onSubmit={onSubmit} noValidate aria-label="Project Profile Edit Form">
        <CardContent className="gf-profile-edit-card__content">
          {/* Server Error Alert Banner */}
          {apiError && (
            <div className="gf-profile-form-alert" role="alert">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
                className="gf-profile-form-alert__icon"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <div className="gf-profile-form-alert__text">{apiError}</div>
            </div>
          )}

          {/* 1. Project Name */}
          <div className="gf-profile-form-field">
            <Input
              id="project-name"
              name="name"
              label="Project Name"
              required
              placeholder="e.g. Autonomous Solar Rover"
              value={formData.name}
              onChange={handleNameChange}
              error={errors.name}
              helperText="Authoritative name of your project instance."
              maxLength={255}
              disabled={isSubmitting}
              rightAddon={
                <span className="gf-profile-form-char-count" aria-live="polite">
                  {formData.name.length}/255
                </span>
              }
            />
          </div>

          {/* 2. Problem Statement */}
          <div className="gf-profile-form-field">
            <label htmlFor="project-problem" className="gf-profile-form-label">
              Problem Statement
            </label>
            <p id="project-problem-helper" className="gf-profile-form-helper">
              What problem are you trying to solve, and who experiences it?
            </p>
            <textarea
              id="project-problem"
              name="problem"
              className={`gf-profile-form-textarea ${
                errors.problem ? 'gf-profile-form-textarea--error' : ''
              }`}
              placeholder="Describe the real-world problem, user friction, or technical bottleneck..."
              rows={4}
              value={formData.problem}
              onChange={handleProblemChange}
              aria-describedby="project-problem-helper"
              aria-invalid={Boolean(errors.problem)}
              disabled={isSubmitting}
            />
            {errors.problem && (
              <p className="gf-profile-form-error" role="alert">
                {errors.problem}
              </p>
            )}
          </div>

          {/* 3. Proposed Solution */}
          <div className="gf-profile-form-field">
            <label htmlFor="project-solution" className="gf-profile-form-label">
              Proposed Solution
            </label>
            <p id="project-solution-helper" className="gf-profile-form-helper">
              Outline the core technical concept, proposed architecture, or prototype approach.
            </p>
            <textarea
              id="project-solution"
              name="proposedSolution"
              className={`gf-profile-form-textarea ${
                errors.proposedSolution ? 'gf-profile-form-textarea--error' : ''
              }`}
              placeholder="Outline the approach, architectural stack, or implementation concept..."
              rows={4}
              value={formData.proposedSolution}
              onChange={handleSolutionChange}
              aria-describedby="project-solution-helper"
              aria-invalid={Boolean(errors.proposedSolution)}
              disabled={isSubmitting}
            />
            {errors.proposedSolution && (
              <p className="gf-profile-form-error" role="alert">
                {errors.proposedSolution}
              </p>
            )}
          </div>

          {/* 4. Target Complexity */}
          <fieldset className="gf-profile-form-fieldset">
            <legend className="gf-profile-form-legend">
              Target Complexity <span className="gf-profile-form-required">*</span>
            </legend>
            <p id="complexity-helper" className="gf-profile-form-helper">
              Architectural and implementation complexity tier.
            </p>
            <div
              className="gf-profile-complexity-grid"
              role="radiogroup"
              aria-describedby="complexity-helper"
            >
              {COMPLEXITY_OPTIONS.map((opt) => {
                const isSelected = formData.complexity === opt.value;
                return (
                  <label
                    key={opt.value}
                    className={`gf-profile-complexity-card ${
                      isSelected ? 'gf-profile-complexity-card--selected' : ''
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
                    <div className="gf-profile-complexity-card-header">
                      <span
                        className="gf-profile-complexity-indicator"
                        aria-hidden="true"
                      >
                        {isSelected && <span className="gf-profile-complexity-dot" />}
                      </span>
                      <span className="gf-profile-complexity-title">{opt.label}</span>
                    </div>
                    <p className="gf-profile-complexity-desc">{opt.description}</p>
                  </label>
                );
              })}
            </div>
            {errors.complexity && (
              <p className="gf-profile-form-error" role="alert">
                {errors.complexity}
              </p>
            )}
          </fieldset>

          {/* 5. Target Deadline */}
          <div className="gf-profile-form-field">
            <Input
              id="project-deadline"
              name="deadline"
              type="date"
              label="Target Deadline"
              value={formData.deadline}
              onChange={handleDeadlineChange}
              error={errors.deadline}
              helperText="Target completion milestone for your build lifecycle."
              disabled={isSubmitting}
            />
          </div>

          {/* Immutability Scope Notice */}
          <div className="gf-profile-immutable-reminder" role="note">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
            <p>
              Lifecycle phase, operational status, project health, and ownership are system-managed
              and cannot be modified from this form.
            </p>
          </div>
        </CardContent>

        <CardFooter className="gf-profile-edit-card__footer">
          <Button
            as="button"
            type="submit"
            variant="primary"
            size="md"
            disabled={!isDirty || isSubmitting}
            aria-busy={isSubmitting}
            className="gf-profile-save-btn"
          >
            {isSubmitting ? (
              <>
                <span className="gf-profile-spinner" aria-hidden="true" />
                Saving Changes…
              </>
            ) : (
              'Save Changes'
            )}
          </Button>

          <Button
            as="button"
            type="button"
            variant="secondary"
            size="md"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
