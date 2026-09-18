import { useMemo } from 'react';
import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';

interface MentorCatalogSummaryBarProps {
  totalCount: number;
  filteredCount: number;
  hasActiveFilters: boolean;
  catalog: ProjectDefinitionCatalogItem[];
}

export function MentorCatalogSummaryBar({
  totalCount,
  filteredCount,
  hasActiveFilters,
  catalog,
}: MentorCatalogSummaryBarProps) {
  // Derive complexity breakdown strictly from returned catalog items
  const complexityCounts = useMemo(() => {
    const counts: Record<'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED', number> = {
      BEGINNER: 0,
      INTERMEDIATE: 0,
      ADVANCED: 0,
    };
    for (const item of catalog) {
      const c = (item.complexity || '').toUpperCase() as 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
      if (c in counts) {
        counts[c] += 1;
      }
    }
    return counts;
  }, [catalog]);

  return (
    <div className="gf-mentor-summary-bar" aria-live="polite">
      <div className="gf-mentor-summary-bar__count">
        <span className="gf-mentor-summary-bar__number">
          {hasActiveFilters ? `${filteredCount} of ${totalCount}` : totalCount}
        </span>{' '}
        mentor project{totalCount === 1 ? '' : 's'}{' '}
        {hasActiveFilters ? 'matching filters' : 'available'}
      </div>

      <div className="gf-mentor-summary-bar__distribution" aria-label="Complexity breakdown">
        {complexityCounts.BEGINNER > 0 && (
          <span className="gf-mentor-summary-bar__badge gf-mentor-summary-bar__badge--beginner">
            {complexityCounts.BEGINNER} Beginner
          </span>
        )}
        {complexityCounts.INTERMEDIATE > 0 && (
          <span className="gf-mentor-summary-bar__badge gf-mentor-summary-bar__badge--intermediate">
            {complexityCounts.INTERMEDIATE} Intermediate
          </span>
        )}
        {complexityCounts.ADVANCED > 0 && (
          <span className="gf-mentor-summary-bar__badge gf-mentor-summary-bar__badge--advanced">
            {complexityCounts.ADVANCED} Advanced
          </span>
        )}
      </div>
    </div>
  );
}
