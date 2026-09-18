import type { ProjectCreatePayload } from '@/lib/api/types';
import type { ProjectFormData, FormValidationErrors } from './types';

/**
 * Validates the Project Creation form input before submission.
 * Enforces backend boundaries without inventing restrictive rules.
 */
export function validateProjectForm(data: ProjectFormData): FormValidationErrors {
  const errors: FormValidationErrors = {};
  const trimmedName = data.name.trim();

  if (!trimmedName) {
    errors.name = 'Project name is required.';
  } else if (trimmedName.length > 255) {
    errors.name = 'Project name cannot exceed 255 characters.';
  }

  if (!['BEGINNER', 'INTERMEDIATE', 'ADVANCED'].includes(data.complexity)) {
    errors.complexity = 'Please select a valid complexity level.';
  }

  if (data.deadline) {
    const d = new Date(data.deadline);
    if (isNaN(d.getTime())) {
      errors.deadline = 'Please enter a valid deadline date.';
    }
  }

  return errors;
}

/**
 * Converts local form state into the canonical backend ProjectCreatePayload.
 * Trims values and serializes optional fields.
 */
export function toCreatePayload(data: ProjectFormData): ProjectCreatePayload {
  const techList = data.technologies
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean);

  let deadlineIso: string | null = null;
  if (data.deadline) {
    try {
      const parsed = new Date(data.deadline);
      if (!isNaN(parsed.getTime())) {
        deadlineIso = parsed.toISOString();
      }
    } catch {
      deadlineIso = null;
    }
  }

  return {
    name: data.name.trim(),
    problem: data.problem.trim() || undefined,
    proposed_solution: data.proposedSolution.trim() || undefined,
    complexity: data.complexity,
    technologies: techList.length > 0 ? techList : undefined,
    deadline: deadlineIso,
  };
}

/**
 * Normalizes error messages from ApiClientError or unexpected failures into user-safe, actionable copy.
 */
export function formatProjectCreateError(err: unknown): string {
  if (err && typeof err === 'object' && 'name' in err && (err as { name: string }).name === 'ApiClientError') {
    const apiErr = err as import('@/lib/api/errors').ApiClientError;
    if (apiErr.isUnauthorized) {
      return 'Your session has expired. Please sign in again.';
    }
    if (apiErr.isForbidden) {
      return 'You do not have permission to create a project in this workspace.';
    }
    if (apiErr.status === 409) {
      return 'A project with this name already exists. Please choose a different name.';
    }
    if (apiErr.isValidationError) {
      return 'Your project couldn\'t be created. Please review the highlighted fields.';
    }
    if (apiErr.isRateLimited) {
      return 'Too many requests. Please wait a moment before trying again.';
    }
    if (apiErr.isServerError) {
      return 'Something went wrong on the server while creating your project. Please try again.';
    }
    if (apiErr.isNetworkError) {
      return 'Unable to reach the server. Please check your network connection and try again.';
    }
    if (apiErr.message && !apiErr.message.startsWith('HTTP ') && !apiErr.message.includes('Failed to fetch')) {
      return apiErr.message;
    }
  }
  return 'Something went wrong while creating the project. Please try again.';
}
