import type { ProjectResponse } from '@/lib/api/types';
import type { ProjectFilterState, SortOption } from './types';

export const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'recently_created', label: 'Recently Created' },
  { value: 'name_asc', label: 'Name (A to Z)' },
  { value: 'name_desc', label: 'Name (Z to A)' },
  { value: 'progress_desc', label: 'Progress (High to Low)' },
  { value: 'progress_asc', label: 'Progress (Low to High)' },
  { value: 'deadline_asc', label: 'Deadline (Nearest first)' },
  { value: 'deadline_desc', label: 'Deadline (Furthest first)' },
];

export const STATUS_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: 'ALL', label: 'All Statuses' },
  { value: 'ACTIVE', label: 'Active' },
  { value: 'DRAFT', label: 'Draft' },
  { value: 'PAUSED', label: 'Paused' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'ARCHIVED', label: 'Archived' },
];

export const PHASE_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: 'ALL', label: 'All Lifecycle Phases' },
  { value: 'IDEA', label: 'Stage 1: Idea' },
  { value: 'ASSESSMENT', label: 'Stage 2: Assessment' },
  { value: 'BLUEPRINT', label: 'Stage 3: Blueprint' },
  { value: 'PLANNING', label: 'Stage 4: Planning' },
  { value: 'IMPLEMENTATION', label: 'Stage 5: Implementation' },
  { value: 'TESTING', label: 'Stage 6: Testing' },
  { value: 'DEPLOYMENT', label: 'Stage 7: Deployment' },
  { value: 'COMPLETED', label: 'Stage 8: Completed' },
];

export const HEALTH_FILTER_OPTIONS: { value: string; label: string }[] = [
  { value: 'ALL', label: 'All Health Statuses' },
  { value: 'HEALTHY', label: 'Healthy' },
  { value: 'WARNING', label: 'Warning' },
  { value: 'CRITICAL', label: 'Critical' },
];

/**
 * Filter and sort a collection of projects client-side.
 * Does not mutate the source array.
 */
export function filterAndSortProjects(
  projects: ProjectResponse[],
  filters: ProjectFilterState,
): ProjectResponse[] {
  return projects
    .filter((project) => {
      // 1. Text Search Filter (name, problem, proposed_solution)
      if (filters.searchQuery.trim()) {
        const q = filters.searchQuery.trim().toLowerCase();
        const matchesName = project.name.toLowerCase().includes(q);
        const matchesProblem = project.problem ? project.problem.toLowerCase().includes(q) : false;
        const matchesSolution = project.proposed_solution
          ? project.proposed_solution.toLowerCase().includes(q)
          : false;

        if (!matchesName && !matchesProblem && !matchesSolution) {
          return false;
        }
      }

      // 2. Status Filter
      if (filters.statusFilter !== 'ALL') {
        if (project.status?.toUpperCase() !== filters.statusFilter.toUpperCase()) {
          return false;
        }
      }

      // 3. Phase Filter
      if (filters.phaseFilter !== 'ALL') {
        if (project.current_phase?.toUpperCase() !== filters.phaseFilter.toUpperCase()) {
          return false;
        }
      }

      // 4. Health Filter
      if (filters.healthFilter !== 'ALL') {
        if (project.health?.toUpperCase() !== filters.healthFilter.toUpperCase()) {
          return false;
        }
      }

      return true;
    })
    .sort((a, b) => {
      switch (filters.sortBy) {
        case 'name_asc':
          return a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });

        case 'name_desc':
          return b.name.localeCompare(a.name, undefined, { sensitivity: 'base' });

        case 'progress_desc':
          return (b.progress_percentage ?? 0) - (a.progress_percentage ?? 0);

        case 'progress_asc':
          return (a.progress_percentage ?? 0) - (b.progress_percentage ?? 0);

        case 'deadline_asc': {
          // Nearest deadline first; nulls placed at the end
          if (!a.deadline && !b.deadline) return 0;
          if (!a.deadline) return 1;
          if (!b.deadline) return -1;
          return new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
        }

        case 'deadline_desc': {
          // Furthest deadline first; nulls placed at the end
          if (!a.deadline && !b.deadline) return 0;
          if (!a.deadline) return 1;
          if (!b.deadline) return -1;
          return new Date(b.deadline).getTime() - new Date(a.deadline).getTime();
        }

        case 'recently_created':
        default: {
          // Newest creation timestamp first; nulls placed at the end
          if (!a.created_at && !b.created_at) return 0;
          if (!a.created_at) return 1;
          if (!b.created_at) return -1;
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
      }
    });
}
