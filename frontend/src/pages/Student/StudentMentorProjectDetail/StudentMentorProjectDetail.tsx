import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectDefinition, selectMentorProject } from '@/lib/api';
import type { ProjectDefinitionCatalogItem, ProjectResponse } from '@/lib/api/types';
import { ApiClientError } from '@/lib/api/errors';

import { MentorProjectDetailHeader } from './components/MentorProjectDetailHeader';
import { MentorProjectOverview } from './components/MentorProjectOverview';
import { MentorProjectTechnology } from './components/MentorProjectTechnology';
import { MentorProjectConstraintsAssumptions } from './components/MentorProjectConstraintsAssumptions';
import { MentorProjectMetadata } from './components/MentorProjectMetadata';
import { MentorProjectSelectionPanel } from './components/MentorProjectSelectionPanel';
import { MentorProjectSelectionSuccess } from './components/MentorProjectSelectionSuccess';
import { MentorProjectLoadingSkeleton } from './components/MentorProjectLoadingSkeleton';
import { MentorProjectErrorState } from './components/MentorProjectErrorState';

import './StudentMentorProjectDetail.css';

type PageState = 'LOADING' | 'ERROR_NOT_FOUND' | 'ERROR_GENERIC' | 'DETAIL' | 'SELECTION_SUCCESS';
type SelectionState = 'IDLE' | 'SELECTING' | 'SELECTION_ERROR';

export function StudentMentorProjectDetail() {
  const { definitionId } = useParams<{ definitionId: string }>();

  const [pageState, setPageState] = useState<PageState>('LOADING');
  const [selectionState, setSelectionState] = useState<SelectionState>('IDLE');
  const [definition, setDefinition] = useState<ProjectDefinitionCatalogItem | null>(null);
  const [createdProject, setCreatedProject] = useState<ProjectResponse | null>(null);
  const [loadError, setLoadError] = useState<Error | null>(null);
  const [selectionError, setSelectionError] = useState<Error | null>(null);
  const [retryKey, setRetryKey] = useState(0);

  // Scroll to top on route mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [definitionId]);

  // Load definition data
  useEffect(() => {
    let isCancelled = false;

    async function loadDefinition() {
      if (!definitionId) {
        setLoadError(new ApiClientError(404, 'PROJECT_DEFINITION_NOT_FOUND', 'Project definition not found.'));
        setPageState('ERROR_NOT_FOUND');
        return;
      }

      setPageState('LOADING');
      setLoadError(null);
      setSelectionError(null);

      try {
        const data = await getMentorProjectDefinition(definitionId);
        if (!isCancelled) {
          setDefinition(data);
          setPageState('DETAIL');
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          const error = err instanceof Error ? err : new Error('Failed to load mentor project');
          setLoadError(error);

          if (
            error instanceof ApiClientError &&
            (error.status === 404 || error.code === 'PROJECT_DEFINITION_NOT_FOUND')
          ) {
            setPageState('ERROR_NOT_FOUND');
          } else {
            setPageState('ERROR_GENERIC');
          }
        }
      }
    }

    loadDefinition();

    return () => {
      isCancelled = true;
    };
  }, [definitionId, retryKey]);

  const handleRetry = useCallback(() => {
    setRetryKey((prev) => prev + 1);
  }, []);

  const handleSelectProject = useCallback(async () => {
    if (!definitionId || selectionState === 'SELECTING') return;

    setSelectionState('SELECTING');
    setSelectionError(null);

    try {
      const result = await selectMentorProject(definitionId);
      setCreatedProject(result);
      setPageState('SELECTION_SUCCESS');
      setSelectionState('IDLE');
    } catch (err: unknown) {
      const error = err instanceof Error ? err : new Error('Unable to select project');
      setSelectionError(error);
      setSelectionState('SELECTION_ERROR');
    }
  }, [definitionId, selectionState]);

  const handleClearSelectionError = useCallback(() => {
    setSelectionError(null);
    setSelectionState('IDLE');
  }, []);

  // 1. Loading State
  if (pageState === 'LOADING') {
    return <MentorProjectLoadingSkeleton />;
  }

  // 2. Error States (404 / 403 / 5xx / Network)
  if (pageState === 'ERROR_NOT_FOUND' || pageState === 'ERROR_GENERIC') {
    return <MentorProjectErrorState error={loadError} onRetry={handleRetry} />;
  }

  // 3. Selection Success State
  if (pageState === 'SELECTION_SUCCESS' && createdProject) {
    return <MentorProjectSelectionSuccess project={createdProject} />;
  }

  // 4. Detail State
  if (!definition) {
    return <MentorProjectErrorState error={loadError} onRetry={handleRetry} />;
  }

  return (
    <div className="gf-detail-page">
      {/* Header with Breadcrumb & Back button */}
      <MentorProjectDetailHeader definition={definition} />

      {/* Main Content & Sticky Sidebar Grid */}
      <div className="gf-detail-layout">
        {/* Main Column */}
        <main className="gf-detail-layout__main">
          {/* Section 1: Overview (Problem, Solution, Description) */}
          <MentorProjectOverview definition={definition} />

          {/* Section 2: Technology Snapshot */}
          <MentorProjectTechnology technologies={definition.technology_snapshot} />

          {/* Section 3: Constraints & Assumptions */}
          <MentorProjectConstraintsAssumptions
            constraints={definition.constraints}
            assumptions={definition.assumptions}
          />
        </main>

        {/* Sidebar Column */}
        <div className="gf-detail-layout__sidebar">
          {/* Action Panel: Primary Selection CTA */}
          <MentorProjectSelectionPanel
            onSelect={handleSelectProject}
            isSelecting={selectionState === 'SELECTING'}
            selectionError={selectionError}
            onClearError={handleClearSelectionError}
          />

          {/* Metadata Snapshot */}
          <MentorProjectMetadata definition={definition} />
        </div>
      </div>
    </div>
  );
}
