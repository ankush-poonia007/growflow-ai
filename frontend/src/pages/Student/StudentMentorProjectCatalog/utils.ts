import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import type { CatalogFilterState, SortOption } from './types';

export const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'recently_created', label: 'Recently added' },
  { value: 'name_asc', label: 'Name A–Z' },
  { value: 'name_desc', label: 'Name Z–A' },
  { value: 'complexity_asc', label: 'Complexity (Beginner first)' },
  { value: 'complexity_desc', label: 'Complexity (Advanced first)' },
];

export const COMPLEXITY_OPTIONS = [
  { value: 'ALL', label: 'All Complexities' },
  { value: 'BEGINNER', label: 'Beginner' },
  { value: 'INTERMEDIATE', label: 'Intermediate' },
  { value: 'ADVANCED', label: 'Advanced' },
];

const COMPLEXITY_RANKS: Record<string, number> = {
  BEGINNER: 1,
  INTERMEDIATE: 2,
  ADVANCED: 3,
};

/**
 * Filter and sort mentor project definition catalog items.
 * Operates purely in-memory on immutable data.
 */
export function filterAndSortCatalog(
  items: ProjectDefinitionCatalogItem[],
  filters: CatalogFilterState,
): ProjectDefinitionCatalogItem[] {
  const query = filters.searchQuery.trim().toLowerCase();
  const complexity = filters.complexityFilter.toUpperCase();

  return items
    .filter((item) => {
      // Complexity filter
      if (complexity !== 'ALL') {
        const itemComplexity = (item.complexity || '').toUpperCase();
        if (itemComplexity !== complexity) {
          return false;
        }
      }

      // Search query across name, problem, proposed_solution, description
      if (query) {
        const matchName = (item.name || '').toLowerCase().includes(query);
        const matchProblem = (item.problem || '').toLowerCase().includes(query);
        const matchSolution = (item.proposed_solution || '').toLowerCase().includes(query);
        const matchDescription = (item.description || '').toLowerCase().includes(query);

        if (!matchName && !matchProblem && !matchSolution && !matchDescription) {
          return false;
        }
      }

      return true;
    })
    .sort((a, b) => {
      switch (filters.sortBy) {
        case 'recently_created': {
          const timeA = a.created_at ? new Date(a.created_at).getTime() : 0;
          const timeB = b.created_at ? new Date(b.created_at).getTime() : 0;
          return timeB - timeA;
        }
        case 'name_asc':
          return (a.name || '').localeCompare(b.name || '');
        case 'name_desc':
          return (b.name || '').localeCompare(a.name || '');
        case 'complexity_asc': {
          const rankA = COMPLEXITY_RANKS[(a.complexity || '').toUpperCase()] || 99;
          const rankB = COMPLEXITY_RANKS[(b.complexity || '').toUpperCase()] || 99;
          if (rankA !== rankB) return rankA - rankB;
          return (a.name || '').localeCompare(b.name || '');
        }
        case 'complexity_desc': {
          const rankA = COMPLEXITY_RANKS[(a.complexity || '').toUpperCase()] || 0;
          const rankB = COMPLEXITY_RANKS[(b.complexity || '').toUpperCase()] || 0;
          if (rankA !== rankB) return rankB - rankA;
          return (a.name || '').localeCompare(b.name || '');
        }
        default:
          return 0;
      }
    });
}
