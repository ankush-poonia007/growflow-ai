import type { ProjectPhase, ProjectStatus, ProjectHealth } from '@/lib/api/types';

export type SortOption =
  | 'recently_created'
  | 'name_asc'
  | 'name_desc'
  | 'progress_desc'
  | 'progress_asc'
  | 'deadline_asc'
  | 'deadline_desc';

export interface ProjectFilterState {
  searchQuery: string;
  statusFilter: 'ALL' | ProjectStatus | string;
  phaseFilter: 'ALL' | ProjectPhase | string;
  healthFilter: 'ALL' | ProjectHealth | string;
  sortBy: SortOption;
}

export const DEFAULT_FILTERS: ProjectFilterState = {
  searchQuery: '',
  statusFilter: 'ALL',
  phaseFilter: 'ALL',
  healthFilter: 'ALL',
  sortBy: 'recently_created',
};
