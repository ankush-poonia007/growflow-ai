import type { ProjectResponse } from '@/lib/api/types';

interface ProjectSummaryBarProps {
  totalCount: number;
  filteredCount: number;
  projects: ProjectResponse[];
  hasActiveFilters: boolean;
}

export function ProjectSummaryBar({
  totalCount,
  filteredCount,
  projects,
  hasActiveFilters,
}: ProjectSummaryBarProps) {
  const activeCount = projects.filter((p) => p.status?.toUpperCase() === 'ACTIVE').length;
  const attentionCount = projects.filter(
    (p) => p.health?.toUpperCase() === 'WARNING' || p.health?.toUpperCase() === 'CRITICAL',
  ).length;
  const completedCount = projects.filter(
    (p) => p.status?.toUpperCase() === 'COMPLETED' || p.current_phase?.toUpperCase() === 'COMPLETED',
  ).length;

  return (
    <div className="gf-projects-summary" aria-label="Projects Collection Summary">
      <div className="gf-projects-summary__counts">
        <span className="gf-projects-summary__count-item">
          <strong>{totalCount}</strong> {totalCount === 1 ? 'project total' : 'projects total'}
        </span>
        <span className="gf-projects-summary__sep" aria-hidden="true">•</span>
        <span className="gf-projects-summary__count-item">
          <strong>{activeCount}</strong> active
        </span>
        {attentionCount > 0 && (
          <>
            <span className="gf-projects-summary__sep" aria-hidden="true">•</span>
            <span className="gf-projects-summary__count-item gf-projects-summary__count-item--attention">
              <strong>{attentionCount}</strong> attention needed
            </span>
          </>
        )}
        <span className="gf-projects-summary__sep" aria-hidden="true">•</span>
        <span className="gf-projects-summary__count-item">
          <strong>{completedCount}</strong> completed
        </span>
      </div>

      {hasActiveFilters && (
        <div className="gf-projects-summary__filter-status">
          Showing <strong>{filteredCount}</strong> of <strong>{totalCount}</strong>
        </div>
      )}
    </div>
  );
}
