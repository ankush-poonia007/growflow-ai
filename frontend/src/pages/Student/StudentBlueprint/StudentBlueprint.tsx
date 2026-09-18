import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router';
import {
  getProject,
  getBlueprintStatus,
  subscribeBlueprintEvents,
  startBlueprintGeneration,
  retryBlueprintGeneration,
  getBlueprintContent,
  approveBlueprint,
} from '@/lib/api';
import type {
  ProjectResponse,
  BlueprintStatusResponse,
  BlueprintContentResponse,
  BlueprintSectionKey,
} from '@/lib/api/types';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import {
  BlueprintHeader,
  BlueprintPrerequisiteBlock,
  BlueprintNotStarted,
  BlueprintGeneratingProgress,
  BlueprintFailureView,
  BlueprintReviewApproval,
  BlueprintApprovedView,
} from './components';
import './StudentBlueprint.css';

export function StudentBlueprint() {
  const { projectId } = useParams<{ projectId: string }>();

  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [blueprintStatus, setBlueprintStatus] = useState<BlueprintStatusResponse | null>(null);
  const [blueprintContent, setBlueprintContent] = useState<BlueprintContentResponse | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isStarting, setIsStarting] = useState<boolean>(false);
  const [isRetrying, setIsRetrying] = useState<boolean>(false);
  const [isApproving, setIsApproving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isStaleGeneration, setIsStaleGeneration] = useState<boolean>(false);

  const sseCleanupRef = useRef<(() => void) | null>(null);
  const pollingTimerRef = useRef<number | null>(null);
  const generatingStartTimeRef = useRef<number | null>(null);

  const stopActiveStreams = useCallback(() => {
    if (sseCleanupRef.current) {
      try {
        sseCleanupRef.current();
      } catch {
        // Ignore cleanup errors
      }
      sseCleanupRef.current = null;
    }
    if (pollingTimerRef.current) {
      window.clearTimeout(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }
  }, []);

  // Clear polling & SSE on unmount
  useEffect(() => {
    return () => {
      stopActiveStreams();
    };
  }, [stopActiveStreams]);

  // Fetch full content when completed or approved
  const fetchContent = useCallback(async (pid: string) => {
    try {
      const content = await getBlueprintContent(pid);
      setBlueprintContent(content);
    } catch (err: any) {
      console.error('Failed to load blueprint content:', err);
    }
  }, []);

  // Poll status fallback while GENERATING
  const pollStatus = useCallback(
    async (pid: string) => {
      try {
        const updated = await getBlueprintStatus(pid);
        setBlueprintStatus(updated);

        if (updated.status === 'GENERATING' || updated.status === 'VALIDATING') {
          pollingTimerRef.current = window.setTimeout(() => {
            void pollStatus(pid);
          }, 1500);
        } else if (
          updated.status === 'READY_FOR_APPROVAL' ||
          updated.status === 'COMPLETED' ||
          updated.status === 'GENERATED' ||
          updated.status === 'APPROVED' ||
          updated.status === 'QA_REJECTED'
        ) {
          stopActiveStreams();
          void fetchContent(pid);
        } else {
          stopActiveStreams();
        }
      } catch (err: any) {
        console.error('Status poll error:', err);
      }
    },
    [fetchContent, stopActiveStreams]
  );

  // Establish SSE stream with transparent polling fallback
  const startLiveTracking = useCallback(
    async (pid: string) => {
      stopActiveStreams();
      if (!generatingStartTimeRef.current) {
        generatingStartTimeRef.current = Date.now();
      }

      if (typeof subscribeBlueprintEvents === 'function') {
        try {
          const cleanup = await subscribeBlueprintEvents(
            pid,
            (updated) => {
              setBlueprintStatus(updated);
              if (
                updated.status === 'READY_FOR_APPROVAL' ||
                updated.status === 'COMPLETED' ||
                updated.status === 'GENERATED' ||
                updated.status === 'APPROVED' ||
                updated.status === 'QA_REJECTED'
              ) {
                stopActiveStreams();
                void fetchContent(pid);
              } else if (updated.status === 'FAILED') {
                stopActiveStreams();
              }
            },
            (_err) => {
              // On SSE error or disconnection, transparently fall back to polling
              console.warn('SSE connection interrupted, falling back to polling.');
              stopActiveStreams();
              void pollStatus(pid);
            }
          );
          sseCleanupRef.current = cleanup;
          return;
        } catch (err) {
          console.warn('Failed to initialize SSE, falling back to polling.', err);
        }
      }

      // Fallback if SSE unavailable
      void pollStatus(pid);
    },
    [fetchContent, pollStatus, stopActiveStreams]
  );

  // Track 3-minute stale generation safeguard (UI safeguard, NOT a backend cancellation)
  useEffect(() => {
    const isGenerating =
      blueprintStatus?.status === 'GENERATING' ||
      blueprintStatus?.status === 'VALIDATING';

    if (!isGenerating) {
      generatingStartTimeRef.current = null;
      setIsStaleGeneration(false);
      return;
    }

    if (!generatingStartTimeRef.current) {
      generatingStartTimeRef.current = Date.now();
    }

    const interval = window.setInterval(() => {
      if (generatingStartTimeRef.current) {
        const elapsed = Date.now() - generatingStartTimeRef.current;
        if (elapsed >= 180000) {
          setIsStaleGeneration(true);
        }
      }
    }, 2000);

    return () => {
      window.clearInterval(interval);
    };
  }, [blueprintStatus?.status]);

  // Load initial workspace data
  const loadInitialData = useCallback(
    async (pid: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const [projData, statusData] = await Promise.all([
          getProject(pid),
          getBlueprintStatus(pid).catch((_err: any) => {
            // If 404/not started, return a default NOT_STARTED response envelope
            return {
              blueprint_id: '',
              project_id: pid,
              status: 'NOT_STARTED' as const,
              current_stage: 3,
              qa_status: 'PENDING' as const,
              generation_progress: {
                completed_sections: [],
                total_sections: 10,
              },
            } as BlueprintStatusResponse;
          }),
        ]);

        setProject(projData);
        setBlueprintStatus(statusData);

        if (statusData.status === 'GENERATING' || statusData.status === 'VALIDATING') {
          void startLiveTracking(pid);
        } else if (
          statusData.status === 'READY_FOR_APPROVAL' ||
          statusData.status === 'COMPLETED' ||
          statusData.status === 'GENERATED' ||
          statusData.status === 'APPROVED' ||
          statusData.status === 'QA_REJECTED'
        ) {
          void fetchContent(pid);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load project details.');
      } finally {
        setIsLoading(false);
      }
    },
    [fetchContent, startLiveTracking]
  );

  useEffect(() => {
    if (!projectId) return;
    void loadInitialData(projectId);
  }, [projectId, loadInitialData]);

  // Start generation handler
  const handleStartGeneration = async () => {
    if (!projectId) return;
    try {
      setIsStarting(true);
      setError(null);
      const res = await startBlueprintGeneration(projectId);
      setBlueprintStatus(res);

      if (res.status === 'GENERATING') {
        void startLiveTracking(projectId);
      } else if (res.status === 'COMPLETED' || res.status === 'READY_FOR_APPROVAL') {
        void fetchContent(projectId);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to initiate blueprint synthesis.');
    } finally {
      setIsStarting(false);
    }
  };

  // Retry generation handler (targeted or full)
  const handleRetry = async (targetSections?: BlueprintSectionKey[]) => {
    if (!projectId) return;
    try {
      setIsRetrying(true);
      setError(null);
      const target_output_key = targetSections && targetSections.length > 0 ? targetSections[0] : undefined;
      const res = await retryBlueprintGeneration(
        projectId,
        target_output_key ? { target_output_key } : undefined
      );
      setBlueprintStatus(res);

      if (res.status === 'GENERATING') {
        void startLiveTracking(projectId);
      } else if (res.status === 'COMPLETED' || res.status === 'READY_FOR_APPROVAL') {
        void fetchContent(projectId);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to retry blueprint synthesis.');
    } finally {
      setIsRetrying(false);
    }
  };

  // Authoritative Approval handler
  const handleApprove = async () => {
    if (!projectId) return;
    try {
      setIsApproving(true);
      setError(null);
      await approveBlueprint(projectId);
      // Update local state to APPROVED
      if (blueprintStatus) {
        setBlueprintStatus({
          ...blueprintStatus,
          status: 'APPROVED',
        });
      }
      // Re-fetch project to get updated phase
      const updatedProj = await getProject(projectId);
      setProject(updatedProj);
    } catch (err: any) {
      setError(err.message || 'Failed to approve blueprint.');
    } finally {
      setIsApproving(false);
    }
  };

  // Batch 2 loading state
  if (isLoading) {
    return (
      <div className="gf-blueprint-container" data-testid="blueprint-loading-state">
        <div className="gf-blueprint-card" style={{ textAlign: 'center', padding: '64px 24px' }}>
          <LoadingSpinner size="lg" className="gf-blueprint-spinner-dot" />
          <h3 className="gf-blueprint-card__title">Loading Blueprint Workspace...</h3>
          <p className="gf-blueprint-card__desc" style={{ margin: '0 auto' }}>
            Checking stage prerequisites and synthesis state.
          </p>
        </div>
      </div>
    );
  }

  // Batch 2 error state on critical load failure
  if (error && !project) {
    return (
      <div className="gf-blueprint-container" data-testid="blueprint-error-state">
        <InlineErrorState
          error={error}
          title="Unable to Load Blueprint Workspace"
          onRetry={() => {
            if (projectId) {
              void loadInitialData(projectId);
            }
          }}
          retryLabel="Retry Loading"
        />
      </div>
    );
  }

  if (!project || !projectId) return null;

  // Prerequisite verification:
  // If project is still in IDEA phase and blueprint has not been created or started,
  // the assessment is incomplete.
  const isPrereqBlocked =
    project.current_phase === 'IDEA' &&
    (!blueprintStatus || blueprintStatus.status === 'NOT_STARTED');

  const currentStatus = blueprintStatus?.status || 'NOT_STARTED';

  const isReadyForReview =
    currentStatus === 'READY_FOR_APPROVAL' ||
    currentStatus === 'COMPLETED' ||
    currentStatus === 'GENERATED';

  const isFailed =
    currentStatus === 'FAILED' ||
    currentStatus === 'QA_REJECTED';

  const isGenerating =
    currentStatus === 'GENERATING' ||
    currentStatus === 'VALIDATING';

  return (
    <div className="gf-blueprint-container" id="student-blueprint-page">
      <BlueprintHeader
        projectId={projectId}
        projectTitle={project.name}
        status={currentStatus}
        qaStatus={blueprintStatus?.qa_status}
      />

      {/* Batch 2 Inline Section Error when operation fails */}
      {error && (
        <InlineErrorState
          error={error}
          title="Blueprint Notice"
          className="mb-4"
          onRetry={
            isFailed
              ? () => handleRetry()
              : undefined
          }
          retryLabel="Retry Generation"
        />
      )}

      {/* Batch 4 3-Minute Stale Generation Safeguard */}
      {isStaleGeneration && isGenerating && (
        <div
          role="alert"
          className="gf-blueprint-preservation-banner mb-4"
          style={{
            borderColor: 'var(--gf-color-warning, #f59e0b)',
            backgroundColor: 'rgba(245, 158, 11, 0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
            padding: '16px 20px',
            borderRadius: '8px',
          }}
          data-testid="stale-generation-safeguard"
        >
          <div style={{ color: 'var(--gf-color-warning-dark, #b45309)', fontSize: '0.875rem' }}>
            <strong>Notice:</strong> Blueprint synthesis is taking longer than usual (over 3 minutes). The background process is still running. You may continue waiting or attempt a retry.
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleRetry()}
            disabled={isRetrying}
          >
            {isRetrying ? 'Retrying...' : 'Retry Generation'}
          </Button>
        </div>
      )}

      {isPrereqBlocked ? (
        <BlueprintPrerequisiteBlock projectId={projectId} />
      ) : currentStatus === 'APPROVED' ? (
        <BlueprintApprovedView
          projectId={projectId}
          qaFeedback={blueprintStatus?.qa_feedback || blueprintContent?.qa_feedback}
          sections={blueprintContent?.content as Record<string, any>}
          approvedAt={blueprintStatus?.updated_at || undefined}
        />
      ) : isReadyForReview ? (
        <BlueprintReviewApproval
          qaFeedback={blueprintStatus?.qa_feedback || blueprintContent?.qa_feedback}
          sections={blueprintContent?.content as Record<string, any>}
          onApprove={handleApprove}
          onRetry={handleRetry}
          isApproving={isApproving}
          isRetrying={isRetrying}
        />
      ) : isFailed ? (
        <BlueprintFailureView
          activeJob={blueprintStatus?.active_job}
          completedSections={blueprintStatus?.generation_progress?.completed_sections}
          failedSections={blueprintStatus?.generation_progress?.failed_sections}
          onRetry={handleRetry}
          isRetrying={isRetrying}
        />
      ) : isGenerating ? (
        <BlueprintGeneratingProgress progress={blueprintStatus?.generation_progress} />
      ) : (
        <BlueprintNotStarted
          onStartGeneration={handleStartGeneration}
          isStarting={isStarting}
        />
      )}
    </div>
  );
}
