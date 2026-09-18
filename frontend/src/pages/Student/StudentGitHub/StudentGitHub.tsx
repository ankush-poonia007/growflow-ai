import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import {
  getGitHubIntegration,
  connectGitHub,
  syncGitHub,
  disconnectGitHub,
} from '@/lib/api';
import type { GitHubIntegrationResponse } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import './StudentGitHub.css';

export function StudentGitHub() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [integration, setIntegration] = useState<GitHubIntegrationResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [syncSuccessMessage, setSyncSuccessMessage] = useState<string | null>(null);

  // Connect form state
  const [repoUrl, setRepoUrl] = useState<string>('');
  const [repoBranch, setRepoBranch] = useState<string>('main');
  const [isConnecting, setIsConnecting] = useState<boolean>(false);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [isDisconnecting, setIsDisconnecting] = useState<boolean>(false);

  const fetchIntegration = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getGitHubIntegration(projectId);
      setIntegration(data);
      if (data.repository_url) {
        setRepoUrl(data.repository_url);
      }
      if (data.default_branch) {
        setRepoBranch(data.default_branch);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load GitHub integration details.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchIntegration();
  }, [fetchIntegration]);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !repoUrl.trim()) return;

    setIsConnecting(true);
    setError(null);
    setSyncSuccessMessage(null);

    try {
      const updated = await connectGitHub(projectId, {
        repository_url: repoUrl.trim(),
        default_branch: repoBranch.trim() || 'main',
      });
      setIntegration(updated);
      setSyncSuccessMessage('Repository connected successfully.');
    } catch (err: any) {
      setError(err?.message || 'Failed to connect repository.');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSync = async () => {
    if (!projectId) return;

    setIsSyncing(true);
    setError(null);
    setSyncSuccessMessage(null);

    try {
      const synced = await syncGitHub(projectId);
      setIntegration(synced);
      setSyncSuccessMessage('Repository synced successfully.');
    } catch (err: any) {
      setError(err?.message || 'Failed to sync with GitHub.');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!projectId) return;
    if (!window.confirm('Are you sure you want to disconnect this GitHub repository?')) {
      return;
    }

    setIsDisconnecting(true);
    setError(null);
    setSyncSuccessMessage(null);

    try {
      const disconnected = await disconnectGitHub(projectId);
      setIntegration(disconnected);
      setSyncSuccessMessage('Repository disconnected.');
    } catch (err: any) {
      setError(err?.message || 'Failed to disconnect repository.');
    } finally {
      setIsDisconnecting(false);
    }
  };

  if (isProjectLoading || (isLoading && !integration)) {
    return (
      <div className="gf-github-page">
        <div className="gf-github-page__loading" role="status">
          <div className="gf-github-page__spinner" />
          <p>Loading GitHub integration...</p>
        </div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-github-page">
        <div className="gf-github-page__error" role="alert">
          <h2>Error Loading Project</h2>
          <p>{(typeof projectError === 'string' ? projectError : projectError?.message) || 'Project not found.'}</p>
        </div>
      </div>
    );
  }

  const isConnected = integration?.connection_status === 'CONNECTED';

  return (
    <div className="gf-github-page" id="student-github-screen">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <div className="gf-github-page__container">
        <header className="gf-github-page__header">
          <div className="gf-github-page__header-text">
            <h2 className="gf-github-page__title">GitHub Repository Integration</h2>
            <p className="gf-github-page__subtitle">
              Monitor project commits and branch activity as an external observation stream.
            </p>
          </div>
          {isConnected && (
            <div className="gf-github-page__actions">
              <Button
                variant="secondary"
                onClick={handleSync}
                disabled={isSyncing}
                id="github-sync-btn"
              >
                {isSyncing ? 'Syncing...' : 'Sync Now'}
              </Button>
              <button
                type="button"
                className="gf-btn gf-btn--danger"
                onClick={handleDisconnect}
                disabled={isDisconnecting}
                id="github-disconnect-btn"
              >
                {isDisconnecting ? 'Disconnecting...' : 'Disconnect'}
              </button>
            </div>
          )}
        </header>

        {syncSuccessMessage && (
          <div className="gf-github-page__alert gf-github-page__alert--success" role="alert">
            <span>✓</span> {syncSuccessMessage}
          </div>
        )}

        {error && (
          <div className="gf-github-page__alert gf-github-page__alert--danger" role="alert">
            <span>⚠️</span> {error}
          </div>
        )}

        <div className="gf-github-page__grid">
          {/* Main Status / Form Card */}
          <div className="gf-github-card">
            <h3 className="gf-github-card__title">Connection Status</h3>

            {isConnected && integration ? (
              <div className="gf-github-connected-details">
                <div className="gf-github-detail-row">
                  <span className="gf-github-detail-label">Status</span>
                  <Badge variant="success">Connected</Badge>
                </div>
                <div className="gf-github-detail-row">
                  <span className="gf-github-detail-label">Repository</span>
                  <a
                    href={integration.repository_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="gf-github-link"
                    id="github-external-link"
                  >
                    {integration.repository_name || integration.repository_url} ↗
                  </a>
                </div>
                <div className="gf-github-detail-row">
                  <span className="gf-github-detail-label">Default Branch</span>
                  <code className="gf-github-code">{integration.default_branch || 'main'}</code>
                </div>
                <div className="gf-github-detail-row">
                  <span className="gf-github-detail-label">Total Commits</span>
                  <strong>{integration.commit_count}</strong>
                </div>
                <div className="gf-github-detail-row">
                  <span className="gf-github-detail-label">Last Synced</span>
                  <span>{integration.last_sync_at ? new Date(integration.last_sync_at).toLocaleString() : 'Never'}</span>
                </div>
              </div>
            ) : (
              <form onSubmit={handleConnect} className="gf-github-form" id="github-connect-form">
                <p className="gf-github-form__help">
                  Connect your GitHub repository to stream commits and branch telemetry into your GrowFlow workspace.
                </p>

                <div className="gf-github-form__field">
                  <label htmlFor="repo-url-input">GitHub Repository URL</label>
                  <input
                    id="repo-url-input"
                    type="url"
                    required
                    placeholder="https://github.com/organization/repo-name"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    className="gf-github-input"
                  />
                </div>

                <div className="gf-github-form__field">
                  <label htmlFor="repo-branch-input">Default Branch</label>
                  <input
                    id="repo-branch-input"
                    type="text"
                    placeholder="main"
                    value={repoBranch}
                    onChange={(e) => setRepoBranch(e.target.value)}
                    className="gf-github-input"
                  />
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  disabled={isConnecting}
                  id="github-connect-btn"
                >
                  {isConnecting ? 'Connecting...' : 'Connect Repository'}
                </Button>
              </form>
            )}
          </div>

          {/* Architecture Note Card */}
          <div className="gf-github-card gf-github-card--info">
            <h3 className="gf-github-card__title">Observation Integration</h3>
            <p className="gf-github-card__text">
              GitHub serves strictly as an external observation source. GrowFlow monitors commit volume, branch health, and delivery cadence without mutating or replacing canonical project tasks and execution milestones.
            </p>
            <ul className="gf-github-card__list">
              <li>Commit timestamps feed the project activity timeline</li>
              <li>Operational tasks remain governed by the GrowFlow blueprint</li>
              <li>Zero synthetic data duplication or lock-in</li>
            </ul>
          </div>
        </div>

        {/* Recent Commits Section */}
        <div className="gf-github-commits-section">
          <h3 className="gf-github-commits-section__title">Recent Commits Preview</h3>
          {isConnected && integration?.cached_commits_preview && integration.cached_commits_preview.length > 0 ? (
            <div className="gf-github-commits-list" id="github-commits-list">
              {integration.cached_commits_preview.map((commit, idx) => (
                <div key={commit.sha || idx} className="gf-github-commit-item">
                  <div className="gf-github-commit-header">
                    <code className="gf-github-commit-sha">{commit.sha.substring(0, 7)}</code>
                    <span className="gf-github-commit-author">{commit.author}</span>
                    <span className="gf-github-commit-date">
                      {commit.date ? new Date(commit.date).toLocaleDateString() : 'Recent'}
                    </span>
                  </div>
                  <p className="gf-github-commit-message">{commit.message}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title={isConnected ? "No commits synced yet" : "Repository not connected"}
              description={
                isConnected
                  ? "Click 'Sync Now' to pull the latest commits from your repository."
                  : "Connect a repository above to preview recent development activity."
              }
            />
          )}
        </div>
      </div>
    </div>
  );
}
