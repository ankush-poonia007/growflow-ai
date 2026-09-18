import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router';
import { getProjectOverview, getBlueprintDocument, downloadBlueprintDocument } from '@/lib/api';
import type { ProjectOverviewResponse, BlueprintDocumentDetail } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { SafeMarkdownViewer } from '@/components/ui/SafeMarkdownViewer/SafeMarkdownViewer';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentBlueprintDocumentViewer.css';

type DocumentViewMode = 'preview' | 'raw';

export function StudentBlueprintDocumentViewer() {
  const { projectId, documentKey = 'readme' } = useParams<{ projectId: string; documentKey?: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<ProjectOverviewResponse | null>(null);
  const [documentDetail, setDocumentDetail] = useState<BlueprintDocumentDetail | null>(null);
  const [viewMode, setViewMode] = useState<DocumentViewMode>('preview');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const fetchDocument = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    setErrorCode(null);
    setDownloadError(null);

    try {
      const [projData, docData] = await Promise.all([
        getProjectOverview(projectId),
        getBlueprintDocument(projectId, documentKey),
      ]);
      setProject(projData);
      setDocumentDetail(docData);
    } catch (err: any) {
      setError(err?.message || 'Unable to load blueprint document.');
      setErrorCode(err?.code || (err?.status === 403 ? 'AUTH_FORBIDDEN' : err?.status === 404 ? 'NOT_FOUND' : 'UNKNOWN'));
    } finally {
      setIsLoading(false);
    }
  }, [projectId, documentKey]);

  useEffect(() => {
    void fetchDocument();
  }, [fetchDocument]);

  const handleDocumentChange = (nextKey: string) => {
    if (!projectId) return;
    setDownloadError(null);
    navigate(`/student/projects/${projectId}/blueprint/documents/${nextKey}`);
  };

  const handleDownload = async () => {
    if (!projectId || !documentDetail) return;
    setIsDownloading(true);
    setDownloadError(null);
    try {
      await downloadBlueprintDocument(projectId, documentDetail.document_key);
    } catch (err: any) {
      setDownloadError(err?.message || 'Failed to download document.');
    } finally {
      setIsDownloading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="gf-doc-loading" role="status" aria-live="polite">
        <div className="gf-doc-skeleton gf-doc-skeleton--header" />
        <div className="gf-doc-skeleton gf-doc-skeleton--content" />
        <span className="sr-only">Loading blueprint document...</span>
      </div>
    );
  }

  if (error || !project) {
    const isForbidden = errorCode === 'AUTH_FORBIDDEN' || error?.toLowerCase().includes('denied') || error?.toLowerCase().includes('forbidden');
    const isNotFound = errorCode === 'NOT_FOUND' || error?.toLowerCase().includes('not found');

    return (
      <div className="gf-doc-error" role="alert">
        <div className="gf-doc-error__card">
          <span className="gf-doc-error__icon" aria-hidden="true">
            {isForbidden ? '🔒' : isNotFound ? '🔍' : '⚠️'}
          </span>
          <h2>{isForbidden ? 'Access Denied' : isNotFound ? 'Document Not Found' : 'Document Error'}</h2>
          <p>{isForbidden ? 'You are not authorized to view this document.' : error}</p>
          <div className="gf-doc-error__actions">
            <Button as="link" to={`/student/projects/${projectId}/blueprint/workspace`} variant="primary">
              Back to Blueprint Workspace
            </Button>
            <Button as="link" to="/student/projects" variant="secondary">
              All Projects
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const availableDocs = documentDetail?.available_documents || [];

  return (
    <div className="gf-document-viewer" aria-label={`Document Viewer for ${project.name}`}>
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={project.is_mentor_project}
      />

      <div className="gf-doc-container">
        <div className="gf-doc-layout">
          {/* Document Navigation Drawer / Sidebar */}
          <aside className="gf-doc-sidebar" aria-label="Available Blueprint Documents">
            <h3 className="gf-doc-sidebar-title">Blueprint Documents</h3>
            <nav className="gf-doc-nav">
              {availableDocs.map((doc) => {
                const isActive = doc.key === documentKey;
                return (
                  <button
                    key={doc.key}
                    type="button"
                    className={`gf-doc-nav-item ${isActive ? 'gf-doc-nav-item--active' : ''}`}
                    onClick={() => handleDocumentChange(doc.key)}
                    id={`doc-select-${doc.key}`}
                    aria-selected={isActive}
                  >
                    <span className="gf-doc-nav-icon" aria-hidden="true">📄</span>
                    <span className="gf-doc-nav-label">{doc.title}</span>
                  </button>
                );
              })}
            </nav>
          </aside>

          {/* Document Content Viewport */}
          <main className="gf-doc-main">
            <Card className="gf-doc-card">
              {/* Document Action Toolbar */}
              <CardHeader className="gf-doc-toolbar">
                <div className="gf-doc-title-group">
                  <span className="gf-doc-breadcrumb">
                    Blueprint / {documentDetail?.document_key}.md
                  </span>
                  <CardTitle as="h2" className="gf-doc-title" id="document-viewer-title">
                    {documentDetail?.title}
                  </CardTitle>
                  <div className="gf-doc-meta-tags">
                    <Badge variant="accent">Version {documentDetail?.version || '1.0.0'}</Badge>
                    <Badge variant={documentDetail?.status === 'APPROVED' ? 'accent' : 'neutral'}>
                      {documentDetail?.status || 'APPROVED'}
                    </Badge>
                  </div>
                </div>

                <div className="gf-doc-controls">
                  {/* Mode Selector: Preview vs Raw Markdown */}
                  <div className="gf-doc-mode-toggle" role="tablist" aria-label="Document View Mode">
                    <button
                      type="button"
                      role="tab"
                      aria-selected={viewMode === 'preview'}
                      className={`gf-doc-mode-btn ${viewMode === 'preview' ? 'gf-doc-mode-btn--active' : ''}`}
                      onClick={() => setViewMode('preview')}
                      id="doc-view-preview-btn"
                    >
                      Preview
                    </button>
                    <button
                      type="button"
                      role="tab"
                      aria-selected={viewMode === 'raw'}
                      className={`gf-doc-mode-btn ${viewMode === 'raw' ? 'gf-doc-mode-btn--active' : ''}`}
                      onClick={() => setViewMode('raw')}
                      id="doc-view-raw-btn"
                    >
                      Raw Markdown
                    </button>
                  </div>

                  {/* Download Button (Constrained to active document/version) */}
                  <Button
                    as="button"
                    variant="secondary"
                    size="sm"
                    onClick={handleDownload}
                    disabled={isDownloading}
                    id="doc-download-btn"
                    title={`Download ${documentDetail?.document_key}.md`}
                  >
                    <span aria-hidden="true">↓</span> {isDownloading ? 'Downloading...' : 'Download .md'}
                  </Button>
                </div>
              </CardHeader>

              {downloadError && (
                <div style={{ padding: '1rem 1.5rem 0' }}>
                  <InlineErrorState
                    error={downloadError}
                    onRetry={handleDownload}
                    retryLabel="Retry Download"
                  />
                </div>
              )}

              {/* Document Content Body */}
              <CardContent className="gf-doc-content-body">
                {viewMode === 'preview' ? (
                  <div className="gf-doc-preview-wrapper">
                    <SafeMarkdownViewer content={documentDetail?.markdown || ''} />
                  </div>
                ) : (
                  <div className="gf-doc-raw-wrapper">
                    <pre className="gf-doc-raw-content" tabIndex={0} aria-label="Raw Markdown Content">
                      <code>{documentDetail?.markdown || ''}</code>
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </main>
        </div>
      </div>
    </div>
  );
}
