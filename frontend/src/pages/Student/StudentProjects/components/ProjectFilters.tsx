import type { ChangeEvent } from 'react';
import type { ProjectFilterState, SortOption } from '../types';
import {
  STATUS_FILTER_OPTIONS,
  PHASE_FILTER_OPTIONS,
  HEALTH_FILTER_OPTIONS,
  SORT_OPTIONS,
} from '../utils';
import { Button } from '@/components/ui/Button';

interface ProjectFiltersProps {
  filters: ProjectFilterState;
  hasActiveFilters: boolean;
  onFilterChange: <K extends keyof ProjectFilterState>(key: K, value: ProjectFilterState[K]) => void;
  onResetFilters: () => void;
}

export function ProjectFilters({
  filters,
  hasActiveFilters,
  onFilterChange,
  onResetFilters,
}: ProjectFiltersProps) {
  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    onFilterChange('searchQuery', e.target.value);
  };

  const handleStatusChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onFilterChange('statusFilter', e.target.value);
  };

  const handlePhaseChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onFilterChange('phaseFilter', e.target.value);
  };

  const handleHealthChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onFilterChange('healthFilter', e.target.value);
  };

  const handleSortChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onFilterChange('sortBy', e.target.value as SortOption);
  };

  return (
    <section className="gf-projects-filter-bar" aria-label="Project search and filters">
      {/* Search Input */}
      <div className="gf-projects-filter-bar__search">
        <label htmlFor="project-search" className="sr-only">
          Search projects by name or problem statement
        </label>
        <div className="gf-projects-filter-bar__search-wrap">
          <svg
            className="gf-projects-filter-bar__search-icon"
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
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            id="project-search"
            type="search"
            className="gf-projects-filter-bar__search-input"
            placeholder="Search projects by name, problem, or solution..."
            value={filters.searchQuery}
            onChange={handleSearchChange}
          />
          {filters.searchQuery && (
            <button
              type="button"
              className="gf-projects-filter-bar__clear-search"
              onClick={() => onFilterChange('searchQuery', '')}
              aria-label="Clear search text"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Select Controls Group */}
      <div className="gf-projects-filter-bar__controls">
        {/* Status Filter */}
        <div className="gf-projects-filter-bar__select-wrap">
          <label htmlFor="project-status-filter" className="sr-only">
            Filter by project status
          </label>
          <select
            id="project-status-filter"
            className="gf-projects-filter-bar__select"
            value={filters.statusFilter}
            onChange={handleStatusChange}
          >
            {STATUS_FILTER_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Phase Filter */}
        <div className="gf-projects-filter-bar__select-wrap">
          <label htmlFor="project-phase-filter" className="sr-only">
            Filter by lifecycle phase
          </label>
          <select
            id="project-phase-filter"
            className="gf-projects-filter-bar__select"
            value={filters.phaseFilter}
            onChange={handlePhaseChange}
          >
            {PHASE_FILTER_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Health Filter */}
        <div className="gf-projects-filter-bar__select-wrap">
          <label htmlFor="project-health-filter" className="sr-only">
            Filter by health status
          </label>
          <select
            id="project-health-filter"
            className="gf-projects-filter-bar__select"
            value={filters.healthFilter}
            onChange={handleHealthChange}
          >
            {HEALTH_FILTER_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Sort Select */}
        <div className="gf-projects-filter-bar__select-wrap">
          <label htmlFor="project-sort-select" className="sr-only">
            Sort projects
          </label>
          <select
            id="project-sort-select"
            className="gf-projects-filter-bar__select"
            value={filters.sortBy}
            onChange={handleSortChange}
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Reset Filters Button */}
        {hasActiveFilters && (
          <Button
            as="button"
            variant="tertiary"
            size="sm"
            onClick={onResetFilters}
            className="gf-projects-filter-bar__reset-btn"
          >
            Reset Filters
          </Button>
        )}
      </div>
    </section>
  );
}
