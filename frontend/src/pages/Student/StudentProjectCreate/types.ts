import type { ProjectComplexity } from '@/lib/api/types';

export interface ProjectFormData {
  name: string;
  problem: string;
  proposedSolution: string;
  complexity: ProjectComplexity;
  technologies: string;
  deadline: string;
}

export interface FormValidationErrors {
  name?: string;
  problem?: string;
  proposedSolution?: string;
  complexity?: string;
  technologies?: string;
  deadline?: string;
}

export const INITIAL_FORM_DATA: ProjectFormData = {
  name: '',
  problem: '',
  proposedSolution: '',
  complexity: 'INTERMEDIATE',
  technologies: '',
  deadline: '',
};

export interface ComplexityOption {
  value: ProjectComplexity;
  label: string;
  description: string;
}

export const COMPLEXITY_OPTIONS: ComplexityOption[] = [
  {
    value: 'BEGINNER',
    label: 'Beginner',
    description: 'Foundational architecture, minimal dependencies, focus on core concept validation.',
  },
  {
    value: 'INTERMEDIATE',
    label: 'Intermediate',
    description: 'Multi-component architecture, structured services, standard build milestones.',
  },
  {
    value: 'ADVANCED',
    label: 'Advanced',
    description: 'Complex architecture, distributed services, custom algorithmic pipelines.',
  },
];
