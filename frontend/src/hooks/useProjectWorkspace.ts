import { useState, useEffect, useCallback, useRef } from 'react';
import { getProject } from '@/lib/api';
import { ApiClientError } from '@/lib/api/errors';
import type { ProjectResponse } from '@/lib/api/types';

export type ProjectWorkspaceError = ApiClientError | Error | string | null;

export interface UseProjectWorkspaceResult {
  project: ProjectResponse | null;
  isLoading: boolean;
  error: ProjectWorkspaceError;
  refetch: () => Promise<void>;
}

/**
 * useProjectWorkspace hook
 *
 * Loads the active project instance definition and metadata.
 * Preserves typed ApiClientError instances so downstream consumers can inspect
 * HTTP status codes (404, 403, 500) and network connection failures truthfully.
 * Includes request sequence and unmount cancellation guards to prevent stale updates.
 */
export function useProjectWorkspace(projectId: string | undefined): UseProjectWorkspaceResult {
  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<ProjectWorkspaceError>(null);
  const activeRequestIdRef = useRef<number>(0);

  const fetchProject = useCallback(async () => {
    const currentRequestId = ++activeRequestIdRef.current;

    if (!projectId) {
      setProject(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await getProject(projectId);
      if (currentRequestId === activeRequestIdRef.current) {
        setProject(data);
      }
    } catch (err: unknown) {
      if (currentRequestId === activeRequestIdRef.current) {
        if (err instanceof ApiClientError) {
          setError(err);
        } else if (err instanceof Error) {
          setError(err);
        } else if (typeof err === 'string') {
          setError(err);
        } else {
          setError('Unable to load project workspace.');
        }
      }
    } finally {
      if (currentRequestId === activeRequestIdRef.current) {
        setIsLoading(false);
      }
    }
  }, [projectId]);

  useEffect(() => {
    void fetchProject();
    return () => {
      // Invalidate any active in-flight request on unmount or projectId change
      activeRequestIdRef.current++;
    };
  }, [fetchProject]);

  return {
    project,
    isLoading,
    error,
    refetch: fetchProject,
  };
}
