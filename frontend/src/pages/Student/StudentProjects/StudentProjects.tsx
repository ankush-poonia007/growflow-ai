import { useState, useEffect, useMemo, useCallback } from 'react';
import { useSearchParams } from 'react-router';
import type { ProjectResponse } from '@/lib/api/types';
import { getProjects } from '@/lib/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { ProjectFilters } from './components/ProjectFilters';
import { ProjectSummaryBar } from './components/ProjectSummaryBar';
import { ProjectCard } from './components/ProjectCard';
import { ProjectsLoadingSkeleton } from './components/ProjectsLoadingSkeleton';
import { ProjectsErrorState } from './components/ProjectsErrorState';
import { filterAndSortProjects, SORT_OPTIONS } from './utils';
import type { ProjectFilterState, SortOption } from './types';
import './StudentProjects.css';

export function StudentProjects() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Server state
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState<number>(0);

  // Initialize UI filter state from sanitized URL params
  const filters: ProjectFilterState = useMemo(() => {
    const rawSearch = searchParams.get('q') || '';
    const rawStatus = searchParams.get('status') || 'ALL';
    const rawPhase = searchParams.get('phase') || 'ALL';
    const rawHealth = searchParams.get('health') || 'ALL';
    const rawSort = searchParams.get('sort') || 'recently_created';

    const validSort = SORT_OPTIONS.some((opt) => opt.value === rawSort)
      ? (rawSort as SortOption)
      : 'recently_created';

    return {
      searchQuery: rawSearch,
      statusFilter: rawStatus,
      phaseFilter: rawPhase,
      healthFilter: rawHealth,
      sortBy: validSort,
    };
  }, [searchParams]);

  // Update a specific filter and persist to searchParams
  const handleFilterChange = useCallback(
    <K extends keyof ProjectFilterState>(key: K, value: ProjectFilterState[K]) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (key === 'searchQuery') {
            if (value) {
              next.set('q', value as string);
            } else {
              next.delete('q');
            }
          } else if (key === 'statusFilter') {
            if (value && value !== 'ALL') {
              next.set('status', value as string);
            } else {
              next.delete('status');
            }
          } else if (key === 'phaseFilter') {
            if (value && value !== 'ALL') {
              next.set('phase', value as string);
            } else {
              next.delete('phase');
            }
          } else if (key === 'healthFilter') {
            if (value && value !== 'ALL') {
              next.set('health', value as string);
            } else {
              next.delete('health');
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

  // Has active non-default filters
  const hasActiveFilters = Boolean(
    filters.searchQuery ||
      filters.statusFilter !== 'ALL' ||
      filters.phaseFilter !== 'ALL' ||
      filters.healthFilter !== 'ALL' ||
      filters.sortBy !== 'recently_created',
  );

  // Data fetching from backend
  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    async function fetchProjects() {
      try {
        const data = await getProjects();
        if (isMounted) {
          setProjects(data || []);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg =
            err instanceof Error
              ? err.message
              : 'Unable to connect to the GrowFlow workspace service.';
          setError(msg);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void fetchProjects();

    return () => {
      isMounted = false;
    };
  }, [retryKey]);

  const handleRetry = useCallback(() => {
    setRetryKey((prev) => prev + 1);
  }, []);

  // Compute filtered & sorted presentation list
  const filteredProjects = useMemo(() => {
    return filterAndSortProjects(projects, filters);
  }, [projects, filters]);

  // 1. Loading State
  if (isLoading) {
    return (
      <main className="gf-projects-page" aria-label="Student Projects Collection">
        <ProjectsLoadingSkeleton />
      </main>
    );
  }

  // 2. Error State
  if (error) {
    return (
      <main className="gf-projects-page" aria-label="Student Projects Collection">
        <ProjectsErrorState message={error} onRetry={handleRetry} />
      </main>
    );
  }

  // 3. Zero Projects Server State (Empty Collection)
  if (projects.length === 0) {
    return (
      <main className="gf-projects-page" aria-label="Student Projects Collection">
        <PageHeader
          title="Projects"
          eyebrow="STUDENT / BUILD"
          description="Keep track of the work you're building and where each project stands."
          actions={
            <Button as="link" to="/student/projects/new" variant="primary">
              Create Project
            </Button>
          }
        />
        <div className="gf-projects-empty-container">
          <EmptyState
            title="No projects yet."
            description="Start with an idea and turn it into something you can build."
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
                aria-hidden="true"
              >
                <path d="M2 7a2 2 0 0 1 2-2h4l2 2h10a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2Z" />
                <path d="M12 11v6" />
                <path d="M9 14h6" />
              </svg>
            }
            action={
              <Button as="link" to="/student/projects/new" variant="primary">
                Create your first project
              </Button>
            }
          />
        </div>
      </main>
    );
  }

  // 4. Populated Projects Collection
  return (
    <main className="gf-projects-page" aria-label="Student Projects Collection">
      {/* Page Header */}
      <PageHeader
        title="Projects"
        eyebrow="STUDENT / BUILD"
        description="Keep track of the work you're building and where each project stands."
        actions={
          <Button as="link" to="/student/projects/new" variant="primary">
            Create Project
          </Button>
        }
      />

      {/* Collection Summary Bar */}
      <ProjectSummaryBar
        totalCount={projects.length}
        filteredCount={filteredProjects.length}
        projects={projects}
        hasActiveFilters={hasActiveFilters}
      />

      {/* Search / Filters / Sort Bar */}
      <ProjectFilters
        filters={filters}
        hasActiveFilters={hasActiveFilters}
        onFilterChange={handleFilterChange}
        onResetFilters={handleResetFilters}
      />

      {/* Project Collection List or No Matches */}
      {filteredProjects.length === 0 ? (
        <div className="gf-projects-empty-container">
          <EmptyState
            title="No projects match your filters."
            description="Try changing your search terms or clearing your active filters."
            action={
              <Button as="button" variant="secondary" onClick={handleResetFilters}>
                Clear Filters
              </Button>
            }
          />
        </div>
      ) : (
        <section
          className="gf-projects-list"
          aria-label={`List of ${filteredProjects.length} projects`}
          role="feed"
        >
          {filteredProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </section>
      )}
    </main>
  );
}
