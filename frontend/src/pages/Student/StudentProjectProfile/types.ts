import type { ProjectComplexity } from '@/lib/api/types';

export type PageMode = 'VIEW' | 'EDIT';

export interface ProjectProfileFormData {
  name: string;
  problem: string;
  proposedSolution: string;
  complexity: ProjectComplexity;
  deadline: string; // YYYY-MM-DD for native date input
}

export interface ProjectProfileFormErrors {
  name?: string;
  problem?: string;
  proposedSolution?: string;
  complexity?: string;
  deadline?: string;
}

export interface ComplexityOption {
  value: ProjectComplexity;
  label: string;
  description: string;
}

export const COMPLEXITY_OPTIONS: ComplexityOption[] = [
  {
    value: 'BEGINNER',
    label: 'Beginner',
    description: 'Focused scope with established patterns and standard libraries.',
  },
  {
    value: 'INTERMEDIATE',
    label: 'Intermediate',
    description: 'Full-stack application with asynchronous data flows and service integrations.',
  },
  {
    value: 'ADVANCED',
    label: 'Advanced',
    description: 'Distributed architecture, real-time telemetry, or complex algorithms.',
  },
];
