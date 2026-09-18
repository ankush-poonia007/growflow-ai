import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getDocument, updateDocument, downloadDocument } from '@/lib/api';
import type { DocumentResponse } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { SafeMarkdownViewer } from '@/components/ui/SafeMarkdownViewer/SafeMarkdownViewer';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import './StudentDocumentDetail.css';

export function StudentDocumentDetail() {
  const { projectId, documentId } = useParams<{ projectId: string; documentId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [mode, setMode] = useState<'preview' | 'edit'>('preview');
  const [title, setTitle] = useState<string>('');
  const [content, setContent] = useState<string>('');

  const fetchDoc = useCallback(async () => {
    if (!projectId || !documentId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDocument(projectId, documentId);
      setDocument(data);
      setTitle(data.title);
      setContent(data.content);
    } catch (err: any) {
      setError(err?.message || 'Unable to load document details.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, documentId]);

  useEffect(() => {
    void fetchDoc();
  }, [fetchDoc]);

  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
    };
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !documentId) return;
    if (!title.trim()) {
      setError('Document title cannot be empty.');
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const updated = await updateDocument(projectId, documentId, {
        title: title.trim(),
        content,
      });
      setDocument(updated);
      setSuccessMsg(`Document updated successfully to version v${updated.version}.`);
      setMode('preview');
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
      feedbackTimerRef.current = setTimeout(() => {
        setSuccessMsg(null);
        feedbackTimerRef.current = null;
      }, 3500);
    } catch (err: any) {
      setError(err?.message || 'Failed to update document.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDownloadRaw = async () => {
    if (!projectId || !documentId || !document) return;
    try {
      setError(null);
      await downloadDocument(projectId, documentId, `${document.document_key}.md`);
    } catch (err: any) {
      setError(`Download failed: ${err?.message || 'Unknown error'}`);
    }
  };

  if (isProjectLoading || isLoading) {
    return (
      <div className="gf-doc-detail-page">
        <div style={{ padding: '2rem', textAlign: 'center' }}>Loading document contents...</div>
      </div>
    );
  }

  if (projectError || !project || !document) {
    return (
      <div className="gf-doc-detail-page">
        <div style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
          {(typeof projectError === 'string' ? projectError : projectError?.message) || error || 'Document not found.'}
        </div>
      </div>
    );
  }

  return (
    <div className="gf-doc-detail-page" id="student-document-detail-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-doc-detail-container">
        {/* Top Header Card */}
        <div className="gf-doc-detail-header-card">
          <div>
            <Link
              to={`/student/projects/${projectId}/documents`}
              style={{ color: '#64748b', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}
              id="back-to-docs-btn"
            >
              ← Back to Project Documents
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
              <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700, color: '#0f172a' }}>
                {document.title}
              </h1>
              <Badge variant="accent">{document.doc_type}</Badge>
              <Badge variant="neutral">v{document.version}</Badge>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
              Key: <code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>{document.document_key}</code> • Source: {document.source}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Button
              as="button"
              variant="secondary"
              id="download-doc-btn"
              onClick={handleDownloadRaw}
            >
              📥 Download .md
            </Button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div style={{ padding: '1rem', background: '#fef2f2', color: '#b91c1c', borderRadius: '8px', marginBottom: '1.5rem' }}>
            {error}
          </div>
        )}
        {successMsg && (
          <div style={{ padding: '1rem', background: '#f0fdf4', color: '#16a34a', borderRadius: '8px', marginBottom: '1.5rem' }}>
            {successMsg}
          </div>
        )}

        {/* View Mode Switcher */}
        <div className="gf-doc-detail-view-tabs" role="tablist">
          <button
            type="button"
            className={`gf-doc-detail-tab-btn ${mode === 'preview' ? 'gf-doc-detail-tab-btn--active' : ''}`}
            id="tab-preview-doc"
            onClick={() => setMode('preview')}
            role="tab"
            aria-selected={mode === 'preview'}
          >
            Markdown Preview
          </button>
          <button
            type="button"
            className={`gf-doc-detail-tab-btn ${mode === 'edit' ? 'gf-doc-detail-tab-btn--active' : ''}`}
            id="tab-edit-doc"
            onClick={() => setMode('edit')}
            role="tab"
            aria-selected={mode === 'edit'}
          >
            Edit Document
          </button>
        </div>

        {/* Body Content */}
        {mode === 'preview' ? (
          <div className="gf-doc-content-wrapper" id="document-markdown-preview">
            <SafeMarkdownViewer content={content} />
          </div>
        ) : (
          <form onSubmit={handleSave} className="gf-doc-content-wrapper">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="gf-form-group">
                <label className="gf-form-label" htmlFor="doc-edit-title">
                  Document Title
                </label>
                <input
                  type="text"
                  id="doc-edit-title"
                  className="gf-form-input"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div className="gf-form-group">
                <label className="gf-form-label" htmlFor="doc-edit-content">
                  Markdown Source Content
                </label>
                <textarea
                  id="doc-edit-content"
                  className="gf-doc-edit-area"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="# Enter markdown content..."
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <Button
                  as="button"
                  variant="secondary"
                  type="button"
                  onClick={() => {
                    setTitle(document.title);
                    setContent(document.content);
                    setMode('preview');
                  }}
                >
                  Cancel
                </Button>
                <Button
                  as="button"
                  variant="primary"
                  type="submit"
                  id="save-doc-btn"
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving Changes...' : 'Save & Bump Version'}
                </Button>
              </div>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}
