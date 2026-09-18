import type { ChangeEvent } from 'react';
import type { CatalogFilterState, SortOption } from '../types';
import { COMPLEXITY_OPTIONS, SORT_OPTIONS } from '../utils';
import { Button } from '@/components/ui/Button';

interface MentorProjectFiltersProps {
  filters: CatalogFilterState;
  hasActiveFilters: boolean;
  onFilterChange: <K extends keyof CatalogFilterState>(key: K, value: CatalogFilterState[K]) => void;
  onResetFilters: () => void;
}

export function MentorProjectFilters({
  filters,
  hasActiveFilters,
  onFilterChange,
  onResetFilters,
}: MentorProjectFiltersProps) {
  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    onFilterChange('searchQuery', e.target.value);
  };

  const handleComplexityChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onFilterChange('complexityFilter', e.target.value);
  };

  const handleSortChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onFilterChange('sortBy', e.target.value as SortOption);
  };

  return (
    <section className="gf-mentor-filters" aria-label="Mentor project search and filters">
      {/* Search Input */}
      <div className="gf-mentor-filters__search">
        <label htmlFor="mentor-catalog-search" className="sr-only">
          Search mentor projects by name, problem, or description
        </label>
        <div className="gf-mentor-filters__search-wrap">
          <svg
            className="gf-mentor-filters__search-icon"
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
            id="mentor-catalog-search"
            type="search"
            className="gf-mentor-filters__search-input"
            placeholder="Search mentor projects by title, problem, or solution..."
            value={filters.searchQuery}
            onChange={handleSearchChange}
          />
          {filters.searchQuery && (
            <button
              type="button"
              className="gf-mentor-filters__clear-search"
              onClick={() => onFilterChange('searchQuery', '')}
              aria-label="Clear search text"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Select Controls Group */}
      <div className="gf-mentor-filters__controls">
        {/* Complexity Filter */}
        <div className="gf-mentor-filters__select-wrap">
          <label htmlFor="mentor-catalog-complexity" className="sr-only">
            Filter by complexity
          </label>
          <select
            id="mentor-catalog-complexity"
            className="gf-mentor-filters__select"
            value={filters.complexityFilter}
            onChange={handleComplexityChange}
          >
            {COMPLEXITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <span className="gf-mentor-filters__select-arrow" aria-hidden="true">
            ▼
          </span>
        </div>

        {/* Sorting */}
        <div className="gf-mentor-filters__select-wrap">
          <label htmlFor="mentor-catalog-sort" className="sr-only">
            Sort mentor projects
          </label>
          <select
            id="mentor-catalog-sort"
            className="gf-mentor-filters__select"
            value={filters.sortBy}
            onChange={handleSortChange}
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <span className="gf-mentor-filters__select-arrow" aria-hidden="true">
            ▼
          </span>
        </div>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <Button
            type="button"
            variant="tertiary"
            size="sm"
            onClick={onResetFilters}
            className="gf-mentor-filters__reset-btn"
          >
            Clear filters
          </Button>
        )}
      </div>
    </section>
  );
}
