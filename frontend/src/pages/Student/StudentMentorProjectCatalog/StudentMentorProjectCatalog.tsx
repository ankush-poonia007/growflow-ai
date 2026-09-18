import { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams } from 'react-router';
import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { getMentorProjectCatalog } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { MentorCatalogIntro } from './components/MentorCatalogIntro';
import { MentorProjectFilters } from './components/MentorProjectFilters';
import { MentorCatalogSummaryBar } from './components/MentorCatalogSummaryBar';
import { MentorProjectCard } from './components/MentorProjectCard';
import { MentorCatalogLoadingSkeleton } from './components/MentorCatalogLoadingSkeleton';
import { MentorCatalogErrorState } from './components/MentorCatalogErrorState';
import { filterAndSortCatalog, SORT_OPTIONS, COMPLEXITY_OPTIONS } from './utils';
import type { CatalogFilterState, SortOption } from './types';
import './StudentMentorProjectCatalog.css';

export function StudentMentorProjectCatalog() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Server state
  const [catalog, setCatalog] = useState<ProjectDefinitionCatalogItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState<number>(0);

  // Initialize UI filter state from sanitized URL params
  const filters: CatalogFilterState = useMemo(() => {
    const rawSearch = searchParams.get('q') || '';
    const rawComplexity = searchParams.get('complexity') || 'ALL';
    const rawSort = searchParams.get('sort') || 'recently_created';

    const validComplexity = COMPLEXITY_OPTIONS.some((opt) => opt.value === rawComplexity)
      ? rawComplexity
      : 'ALL';

    const validSort = SORT_OPTIONS.some((opt) => opt.value === rawSort)
      ? (rawSort as SortOption)
      : 'recently_created';

    return {
      searchQuery: rawSearch,
      complexityFilter: validComplexity,
      sortBy: validSort,
    };
  }, [searchParams]);

  // Update a specific filter and persist to searchParams via replace
  const handleFilterChange = useCallback(
    <K extends keyof CatalogFilterState>(key: K, value: CatalogFilterState[K]) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (key === 'searchQuery') {
            if (value) {
              next.set('q', value as string);
            } else {
              next.delete('q');
            }
          } else if (key === 'complexityFilter') {
            if (value && value !== 'ALL') {
              next.set('complexity', value as string);
            } else {
              next.delete('complexity');
            }
          } else if (key === 'sortBy') {
            if (value && value !== 'recently_created') {
              next.set('sort', value as string);
            } else {
              next.delete('sort');
            }
          }
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  // Reset all filters to default
  const handleResetFilters = useCallback(() => {
    setSearchParams({}, { replace: true });
  }, [setSearchParams]);

  // Check if any non-default filter is active
  const hasActiveFilters = Boolean(
    filters.searchQuery ||
      filters.complexityFilter !== 'ALL' ||
      filters.sortBy !== 'recently_created',
  );

  // Fetch catalog on mount or on retry
  useEffect(() => {
    let isCancelled = false;

    async function loadCatalog() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await getMentorProjectCatalog();
        if (!isCancelled) {
          setCatalog(data || []);
          setIsLoading(false);
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          const message =
            err instanceof Error ? err.message : 'Failed to retrieve mentor project catalog.';
          setError(message);
          setIsLoading(false);
        }
      }
    }

    loadCatalog();

    return () => {
      isCancelled = true;
    };
  }, [retryKey]);

  const handleRetry = useCallback(() => {
    setRetryKey((prev) => prev + 1);
  }, []);

  // Compute filtered & sorted catalog
  const filteredCatalog = useMemo(() => {
    return filterAndSortCatalog(catalog, filters);
  }, [catalog, filters]);

  // Render loading skeleton
  if (isLoading) {
    return <MentorCatalogLoadingSkeleton />;
  }

  // Render error state
  if (error) {
    return <MentorCatalogErrorState error={error} onRetry={handleRetry} />;
  }

  return (
    <div className="gf-mentor-catalog">
      {/* 1. Page Header & Context Banner */}
      <MentorCatalogIntro />

      {/* 2. Filter Bar */}
      <MentorProjectFilters
        filters={filters}
        hasActiveFilters={hasActiveFilters}
        onFilterChange={handleFilterChange}
        onResetFilters={handleResetFilters}
      />

      {/* 3. Empty Backend Catalog State */}
      {catalog.length === 0 ? (
        <EmptyState
          title="No mentor projects available yet."
          description="Mentor-defined opportunities are not currently available. Please check back later as mentors publish new project blueprints."
          icon={
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
          }
        />
      ) : filteredCatalog.length === 0 ? (
        /* 4. No Matches State */
        <EmptyState
          title="No mentor projects match your filters."
          description="Try broadening your search query or adjusting the complexity filter."
          action={
            <Button type="button" variant="secondary" onClick={handleResetFilters}>
              Clear filters
            </Button>
          }
          icon={
            <svg
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          }
        />
      ) : (
        /* 5. Catalog Collection */
        <>
          <MentorCatalogSummaryBar
            totalCount={catalog.length}
            filteredCount={filteredCatalog.length}
            hasActiveFilters={hasActiveFilters}
            catalog={catalog}
          />

          <div
            className="gf-mentor-catalog__grid"
            role="region"
            aria-label="Mentor project definitions"
          >
            {filteredCatalog.map((definition) => (
              <MentorProjectCard key={definition.id} definition={definition} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
