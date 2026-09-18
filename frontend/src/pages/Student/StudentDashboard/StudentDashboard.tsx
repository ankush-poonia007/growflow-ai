import { useState, useEffect, useCallback, useRef } from 'react';
import type { ProjectResponse, ProjectOverviewResponse } from '@/lib/api/types';
import { getProjects, getProjectOverview } from '@/lib/api';
import { DashboardWelcome } from './components/DashboardWelcome';
import { CurrentWork } from './components/CurrentWork';
import { LifecycleTrack } from './components/LifecycleTrack';
import { DeterministicNextAction } from './components/DeterministicNextAction';
import { RecentChanges } from './components/RecentChanges';
import { SecondaryProjects } from './components/SecondaryProjects';
import { DashboardEmptyState } from './components/DashboardEmptyState';
import { DashboardLoadingSkeleton } from './components/DashboardLoadingSkeleton';
import { DashboardErrorState } from './components/DashboardErrorState';
import './StudentDashboard.css';

export function StudentDashboard() {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [overview, setOverview] = useState<ProjectOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState<number>(0);
  const activeSelectedIdRef = useRef<string | null>(null);

  // Fetch initial projects collection
  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    async function fetchWorkspaceData() {
      try {
        const projectList = await getProjects();
        if (!isMounted) return;

        setProjects(projectList);

        if (projectList && projectList.length > 0) {
          // Select first active project, or first project in list
          const defaultProject =
            projectList.find((p) => p.status?.toUpperCase() === 'ACTIVE') ?? projectList[0];
          if (defaultProject) {
            setSelectedProjectId(defaultProject.id);
            activeSelectedIdRef.current = defaultProject.id;

            try {
              const overviewData = await getProjectOverview(defaultProject.id);
              if (isMounted && activeSelectedIdRef.current === defaultProject.id) {
                setOverview(overviewData);
              }
            } catch {
              // Overview failure should not block dashboard rendering if core project exists
              if (isMounted && activeSelectedIdRef.current === defaultProject.id) {
                setOverview(null);
              }
            }
          }
        } else {
          setSelectedProjectId(null);
          activeSelectedIdRef.current = null;
          setOverview(null);
        }
      } catch (err: unknown) {
        if (!isMounted) return;
        const msg =
          err instanceof Error ? err.message : 'Unable to connect to the GrowFlow workspace service.';
        setError(msg);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void fetchWorkspaceData();

    return () => {
      isMounted = false;
      activeSelectedIdRef.current = null;
    };
  }, [retryKey]);

  // Handle switching focused project in dashboard context
  const handleSelectProject = useCallback(
    async (projectId: string) => {
      setSelectedProjectId(projectId);
      activeSelectedIdRef.current = projectId;
      try {
        const overviewData = await getProjectOverview(projectId);
        if (activeSelectedIdRef.current === projectId) {
          setOverview(overviewData);
        }
      } catch {
        if (activeSelectedIdRef.current === projectId) {
          setOverview(null);
        }
      }
    },
    [],
  );

  const handleRetry = useCallback(() => {
    setRetryKey((prev) => prev + 1);
  }, []);

  // 1. Loading State
  if (isLoading) {
    return (
      <main className="gf-dashboard" aria-label="Student Workspace Dashboard">
        <DashboardLoadingSkeleton />
      </main>
    );
  }

  // 2. Error State
  if (error) {
    return (
      <main className="gf-dashboard" aria-label="Student Workspace Dashboard">
        <DashboardErrorState message={error} onRetry={handleRetry} />
      </main>
    );
  }

  // 3. Zero Projects Empty State
  if (projects.length === 0) {
    return (
      <main className="gf-dashboard" aria-label="Student Workspace Dashboard">
        <DashboardWelcome projectCount={0} />
        <DashboardEmptyState />
      </main>
    );
  }

  // 4. Active Project Context
  const activeProject =
    projects.find((p) => p.id === selectedProjectId) ?? projects[0];

  if (!activeProject) {
    return (
      <main className="gf-dashboard" aria-label="Student Workspace Dashboard">
        <DashboardWelcome projectCount={0} />
        <DashboardEmptyState />
      </main>
    );
  }

  return (
    <main className="gf-dashboard" aria-label="Student Workspace Dashboard">
      {/* 1. Welcome Header */}
      <DashboardWelcome projectCount={projects.length} />

      {/* 2. Primary Project Context (Current Work) */}
      <CurrentWork project={activeProject} overview={overview} />

      {/* 3. Two-Column Split: Lifecycle Position & Deterministic Next Action */}
      <div className="gf-dashboard__split-grid">
        <LifecycleTrack currentPhase={activeProject.current_phase} />
        <DeterministicNextAction currentPhase={activeProject.current_phase} />
      </div>

      {/* 4. Recent Project Transitions (Audit Record from overview) */}
      <RecentChanges activity={overview?.recent_activity} />

      {/* 5. Secondary Projects (if multiple active projects exist) */}
      {projects.length > 1 && (
        <SecondaryProjects
          projects={projects}
          selectedProjectId={activeProject.id}
          onSelectProject={handleSelectProject}
        />
      )}
    </main>
  );
}
