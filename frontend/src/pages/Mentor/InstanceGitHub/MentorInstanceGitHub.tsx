import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectInstance, getMentorInstanceGitHub } from '@/lib/api/client';
import type { MentorProjectInstanceDetail, GitHubIntegrationResponse } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceGitHub.css';

export const MentorInstanceGitHub: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [github, setGithub] = useState<GitHubIntegrationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const [projRes, ghRes] = await Promise.all([
          getMentorProjectInstance(projectId),
          getMentorInstanceGitHub(projectId),
        ]);
        if (mounted) {
          setProject(projRes);
          setGithub(ghRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          setError(
            err instanceof Error ? err.message : 'Failed to retrieve GitHub integration or access denied.'
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadData();
    return () => {
      mounted = false;
    };
  }, [projectId]);

  const getConnectionBadge = (status: string) => {
    switch (status) {
      case 'CONNECTED':
        return <Badge variant="success">Connected</Badge>;
      case 'SYNCING':
        return <Badge variant="info">Syncing</Badge>;
      case 'ERROR':
        return <Badge variant="danger">Sync Error</Badge>;
      case 'NOT_CONNECTED':
      default:
        return <Badge variant="neutral">Not Connected</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-github-page" id="mentor-github-loading">
        <Skeleton width="100%" height="160px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <Skeleton width="100%" height="220px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <Skeleton width="100%" height="300px" style={{ borderRadius: '12px' }} />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-mentor-github-page" id="mentor-github-error">
        <div className="gf-mentor-github-error-card" role="alert">
          <h3>GitHub Supervision Restricted</h3>
          <p>{error || 'GitHub details not found or access denied.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  const isConnected = github && github.connection_status !== 'NOT_CONNECTED';

  return (
    <div className="gf-mentor-github-page" id="mentor-github-container">
      <MentorInstanceHeader project={project} activeTab="github" />

      {/* Observational Status Card */}
      <div className="gf-mentor-github__card" id="mentor-github-status-card">
        <div className="gf-mentor-github__header">
          <div>
            <span className="gf-mentor-github__eyebrow">OBSERVATIONAL REPOSITORY INSPECTION</span>
            <h2 className="gf-mentor-github__heading">GitHub Version Control</h2>
          </div>
          <div className="gf-mentor-github__status-tags">
            {github && getConnectionBadge(github.connection_status)}
            <span className="gf-mentor-github__read-only-pill">OBSERVATION ONLY</span>
          </div>
        </div>

        {!isConnected ? (
          <div className="gf-mentor-github__disconnected-state" id="mentor-github-disconnected">
            <div className="gf-mentor-github__icon-placeholder">⎇</div>
            <h3>No Repository Connected</h3>
            <p>
              The student has not connected an external GitHub repository to this project instance yet.
              When connected, commit telemetry and activity logs will appear here for supervision.
            </p>
          </div>
        ) : (
          <div className="gf-mentor-github__details-grid" id="mentor-github-details">
            <div className="gf-mentor-github__detail-item">
              <span className="gf-mentor-github__label">Repository:</span>
              <strong className="gf-mentor-github__val">{github.repository_name}</strong>
            </div>

            <div className="gf-mentor-github__detail-item">
              <span className="gf-mentor-github__label">URL:</span>
              <a
                href={github.repository_url}
                target="_blank"
                rel="noopener noreferrer"
                className="gf-mentor-github__link"
              >
                {github.repository_url}
              </a>
            </div>

            <div className="gf-mentor-github__detail-item">
              <span className="gf-mentor-github__label">Default Branch:</span>
              <code className="gf-mentor-github__branch">{github.default_branch}</code>
            </div>

            <div className="gf-mentor-github__detail-item">
              <span className="gf-mentor-github__label">Observed Commits:</span>
              <span className="gf-mentor-github__val">{github.commit_count} commits</span>
            </div>

            <div className="gf-mentor-github__detail-item">
              <span className="gf-mentor-github__label">Last Telemetry Sync:</span>
              <span className="gf-mentor-github__val">
                {github.last_sync_at ? new Date(github.last_sync_at).toLocaleString() : 'Pending'}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Observed Commits Feed */}
      {isConnected && (
        <div className="gf-mentor-github__commits-card" id="mentor-github-commits">
          <div className="gf-mentor-github__commits-header">
            <h3>Recent Commit Activity</h3>
            <span className="gf-mentor-github__commits-count">
              Showing {github.cached_commits_preview?.length || 0} commits
            </span>
          </div>

          {(!github.cached_commits_preview || github.cached_commits_preview.length === 0) ? (
            <div className="gf-mentor-github__commits-empty" id="mentor-commits-empty">
              <p>No commits observed in the repository yet.</p>
            </div>
          ) : (
            <div className="gf-mentor-github__commits-list">
              {github.cached_commits_preview.map((c) => (
                <div key={c.sha} className="gf-mentor-commit-row" id={`commit-${c.sha}`}>
                  <div className="gf-mentor-commit-row__sha">
                    <code>{c.sha.substring(0, 7)}</code>
                  </div>
                  <div className="gf-mentor-commit-row__main">
                    <p className="gf-mentor-commit-row__msg">{c.message}</p>
                    <div className="gf-mentor-commit-row__meta">
                      <span>Author: <strong>{c.author}</strong></span>
                      <span>•</span>
                      <span>{new Date(c.date).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
