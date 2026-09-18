import type {
  ProjectComplexity,
  ProjectResponse,
  ProjectUpdatePayload,
} from '@/lib/api/types';
import type {
  ProjectProfileFormData,
  ProjectProfileFormErrors,
} from './types';

/**
 * Format an ISO date string into a user-friendly format (e.g. "Oct 15, 2026").
 */
export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) return 'Not set';
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return 'Not set';
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return 'Not set';
  }
}

/**
 * Format an ISO date string with time (e.g. "Oct 15, 2026, 2:30 PM").
 */
export function formatDateTime(isoString: string | null | undefined): string {
  if (!isoString) return 'Not set';
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return 'Not set';
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  } catch {
    return 'Not set';
  }
}

/**
 * Convert an ISO string to a YYYY-MM-DD string for HTML date inputs.
 */
export function formatDateIsoToInput(isoString: string | null | undefined): string {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return '';
    return date.toISOString().split('T')[0] ?? '';
  } catch {
    return '';
  }
}

export const CANONICAL_PHASES: readonly string[] = [
  'IDEA',
  'ASSESSMENT',
  'BLUEPRINT',
  'PLANNING',
  'IMPLEMENTATION',
  'TESTING',
  'DEPLOYMENT',
  'COMPLETED',
] as const;

export function getStageNumber(phase: string | undefined): number {
  if (!phase) return 1;
  const idx = CANONICAL_PHASES.indexOf(phase.toUpperCase());
  return idx >= 0 ? idx + 1 : 1;
}

export interface HealthDisplayMeta {
  label: string;
  variant: 'success' | 'warning' | 'danger' | 'neutral';
  description: string;
}

export function getHealthDisplay(health: string | undefined): HealthDisplayMeta {
  const normalized = health?.toUpperCase();
  switch (normalized) {
    case 'HEALTHY':
      return {
        label: 'Healthy',
        variant: 'success',
        description: 'Project is progressing smoothly with no critical blockers.',
      };
    case 'WARNING':
      return {
        label: 'Warning',
        variant: 'warning',
        description: 'Project has minor blockers or schedule risks requiring attention.',
      };
    case 'CRITICAL':
      return {
        label: 'Critical',
        variant: 'danger',
        description: 'Significant technical impediments or risk of deadline breach.',
      };
    default:
      return {
        label: health || 'Unknown',
        variant: 'neutral',
        description: 'Health indicator not recorded.',
      };
  }
}

/**
 * Populate editable form data from a canonical ProjectResponse.
 */
export function toFormData(project: ProjectResponse): ProjectProfileFormData {
  let complexity: ProjectComplexity = 'INTERMEDIATE';
  if (
    project.complexity === 'BEGINNER' ||
    project.complexity === 'INTERMEDIATE' ||
    project.complexity === 'ADVANCED'
  ) {
    complexity = project.complexity;
  }

  return {
    name: project.name || '',
    problem: project.problem || '',
    proposedSolution: project.proposed_solution || '',
    complexity,
    deadline: formatDateIsoToInput(project.deadline),
  };
}

/**
 * Determine if user has made any changes compared to the canonical project state.
 */
export function isFormDirty(formData: ProjectProfileFormData, project: ProjectResponse): boolean {
  const initial = toFormData(project);
  return (
    formData.name.trim() !== initial.name.trim() ||
    formData.problem.trim() !== initial.problem.trim() ||
    formData.proposedSolution.trim() !== initial.proposedSolution.trim() ||
    formData.complexity !== initial.complexity ||
    formData.deadline !== initial.deadline
  );
}

/**
 * Validate editable fields according to backend constraints:
 * - name: 1–255 characters, required
 * - complexity: BEGINNER | INTERMEDIATE | ADVANCED
 * - deadline: optional, must be valid date if set
 */
export function validateProjectProfileForm(data: ProjectProfileFormData): ProjectProfileFormErrors {
  const errors: ProjectProfileFormErrors = {};

  const trimmedName = data.name.trim();
  if (!trimmedName) {
    errors.name = 'Project name is required.';
  } else if (trimmedName.length > 255) {
    errors.name = 'Project name cannot exceed 255 characters.';
  }

  if (data.deadline) {
    const d = new Date(data.deadline);
    if (isNaN(d.getTime())) {
      errors.deadline = 'Please enter a valid date.';
    }
  }

  return errors;
}

/**
 * Transform validated form data into backend-compatible ProjectUpdatePayload.
 */
export function toUpdatePayload(formData: ProjectProfileFormData): ProjectUpdatePayload {
  let deadlineIso: string | null = null;
  if (formData.deadline) {
    const d = new Date(formData.deadline);
    if (!isNaN(d.getTime())) {
      deadlineIso = d.toISOString();
    }
  }

  return {
    name: formData.name.trim(),
    problem: formData.problem.trim(),
    proposed_solution: formData.proposedSolution.trim(),
    complexity: formData.complexity,
    deadline: deadlineIso,
  };
}
