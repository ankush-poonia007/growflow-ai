import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, Link } from 'react-router';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import { getDocuments, createDocument, downloadDocument } from '@/lib/api';
import type { DocumentResponse, DocumentType, DocumentCreatePayload } from '@/lib/api/types';
import { ProjectWorkspaceHeader } from '@/components/navigation/ProjectWorkspaceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import './StudentDocuments.css';

export function StudentDocuments() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, isLoading: isProjectLoading, error: projectError } = useProjectWorkspace(projectId);

  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDocType, setNewDocType] = useState<DocumentType>('SPECIFICATION');
  const [newContent, setNewContent] = useState<string>('');

  const fetchDocs = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDocuments(projectId);
      setDocuments(data);
    } catch (err: any) {
      setError(err?.message || 'Unable to load project documents.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void fetchDocs();
  }, [fetchDocs]);

  const handleCreateDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;
    if (!newTitle.trim()) {
      setModalError('Document title is required.');
      return;
    }

    setIsSubmitting(true);
    setModalError(null);

    const payload: DocumentCreatePayload = {
      title: newTitle.trim(),
      doc_type: newDocType,
      format: 'markdown',
      content: newContent.trim(),
    };

    try {
      const created = await createDocument(projectId, payload);
      setDocuments((prev) => [...prev, created]);
      setIsModalOpen(false);
      setNewTitle('');
      setNewContent('');
      setNewDocType('SPECIFICATION');
    } catch (err: any) {
      setModalError(err?.message || 'Failed to create document.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = async (e: React.MouseEvent, doc: DocumentResponse) => {
    e.preventDefault();
    e.stopPropagation();
    if (!projectId) return;
    try {
      setError(null);
      await downloadDocument(projectId, doc.id, `${doc.document_key}.md`);
    } catch (err: any) {
      setError(`Download failed: ${err?.message || 'Unknown error'}`);
    }
  };

  const filteredDocs = useMemo(() => {
    return documents.filter((doc) => {
      if (typeFilter !== 'ALL' && doc.doc_type !== typeFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (
          !doc.title.toLowerCase().includes(q) &&
          !doc.document_key.toLowerCase().includes(q) &&
          !doc.content.toLowerCase().includes(q)
        ) {
          return false;
        }
      }
      return true;
    });
  }, [documents, typeFilter, searchQuery]);

  const getDocTypeBadgeVariant = (type: DocumentType): 'neutral' | 'accent' | 'warning' | 'danger' => {
    switch (type) {
      case 'BLUEPRINT':
        return 'accent';
      case 'SPECIFICATION':
        return 'neutral';
      case 'README':
        return 'warning';
      case 'ARCHITECTURE':
        return 'accent';
      default:
        return 'neutral';
    }
  };

  if (isProjectLoading) {
    return (
      <div className="gf-docs-page">
        <div style={{ padding: '2rem', textAlign: 'center' }}>Loading project documents...</div>
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="gf-docs-page">
        <div style={{ padding: '2rem', textAlign: 'center', color: '#ef4444' }}>
          {(typeof projectError === 'string' ? projectError : projectError?.message) || 'Project workspace not found.'}
        </div>
      </div>
    );
  }

  return (
    <div className="gf-docs-page" id="student-documents-view">
      <ProjectWorkspaceHeader
        projectId={project.id}
        projectName={project.name}
        currentPhase={project.current_phase}
        health={project.health}
        isMentorProject={Boolean(project.group_id)}
      />

      <main className="gf-docs-container">
        {/* Controls Bar */}
        <div className="gf-docs-controls">
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', flex: 1 }}>
            <input
              type="text"
              id="docs-search-input"
              placeholder="Search documents by title or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="gf-form-input"
              style={{ minWidth: '240px', maxWidth: '360px' }}
            />

            <select
              id="docs-type-filter"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="gf-form-select"
            >
              <option value="ALL">All Document Types</option>
              <option value="BLUEPRINT">Blueprint</option>
              <option value="SPECIFICATION">Specification</option>
              <option value="README">README</option>
              <option value="ARCHITECTURE">Architecture</option>
              <option value="REPORT">Report</option>
              <option value="GENERAL">General</option>
            </select>
          </div>

          <Button
            as="button"
            variant="primary"
            id="create-doc-btn"
            onClick={() => setIsModalOpen(true)}
          >
            + New Document
          </Button>
        </div>

        {error && (
          <div style={{ padding: '1rem', background: '#fef2f2', color: '#b91c1c', borderRadius: '8px', marginBottom: '1.5rem' }}>
            {error}
          </div>
        )}

        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: '#64748b' }}>
            Loading project documentation...
          </div>
        ) : filteredDocs.length === 0 ? (
          <EmptyState
            icon="📄"
            title="No documents found"
            description="Manage architectural blueprints, technical specs, and setup guides here. Create your first document to begin."
            action={
              <Button as="button" variant="primary" onClick={() => setIsModalOpen(true)}>
                Create Document
              </Button>
            }
          />
        ) : (
          <div className="gf-docs-grid" role="list">
            {filteredDocs.map((doc) => (
              <div
                key={doc.id}
                className="gf-doc-card"
                id={`doc-card-${doc.document_key}`}
                role="listitem"
              >
                <div className="gf-doc-card__top">
                  <span className="gf-doc-card__key">{doc.document_key}</span>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <Badge variant={getDocTypeBadgeVariant(doc.doc_type)}>
                      {doc.doc_type}
                    </Badge>
                    <Badge variant="neutral">v{doc.version}</Badge>
                  </div>
                </div>

                <Link
                  to={`/student/projects/${projectId}/documents/${doc.id}`}
                  className="gf-doc-card__title"
                  id={`doc-link-${doc.id}`}
                >
                  {doc.title}
                </Link>

                <p className="gf-doc-card__snippet">
                  {doc.content.slice(0, 160) || 'No preview content available.'}
                </p>

                <div className="gf-doc-card__footer">
                  <span>Updated {new Date(doc.updated_at).toLocaleDateString()}</span>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <button
                      type="button"
                      className="gf-task-quick-btn"
                      onClick={(e) => handleDownload(e, doc)}
                      title="Download Markdown"
                    >
                      📥 .md
                    </button>
                    <Link
                      to={`/student/projects/${projectId}/documents/${doc.id}`}
                      style={{ color: '#0284c7', fontWeight: 600, textDecoration: 'none' }}
                    >
                      Read & Edit →
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Document Modal */}
      {isModalOpen && (
        <div className="gf-modal-backdrop" role="dialog" aria-modal="true">
          <div className="gf-modal-card">
            <div className="gf-modal-header">
              <h2 className="gf-modal-title">Create Project Document</h2>
              <button
                type="button"
                className="gf-modal-close-btn"
                onClick={() => setIsModalOpen(false)}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateDocument}>
              <div className="gf-modal-body">
                {modalError && (
                  <div style={{ padding: '0.75rem', background: '#fef2f2', color: '#b91c1c', borderRadius: '6px', fontSize: '0.875rem' }}>
                    {modalError}
                  </div>
                )}

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-doc-title">
                    Document Title *
                  </label>
                  <input
                    type="text"
                    id="new-doc-title"
                    className="gf-form-input"
                    placeholder="e.g. Deployment & Infrastructure Architecture"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    required
                    autoFocus
                  />
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-doc-type">
                    Document Type
                  </label>
                  <select
                    id="new-doc-type"
                    className="gf-form-select"
                    value={newDocType}
                    onChange={(e) => setNewDocType(e.target.value as DocumentType)}
                  >
                    <option value="SPECIFICATION">Specification</option>
                    <option value="ARCHITECTURE">Architecture</option>
                    <option value="BLUEPRINT">Blueprint</option>
                    <option value="README">README</option>
                    <option value="REPORT">Report</option>
                    <option value="GENERAL">General</option>
                  </select>
                </div>

                <div className="gf-form-group">
                  <label className="gf-form-label" htmlFor="new-doc-content">
                    Markdown Content
                  </label>
                  <textarea
                    id="new-doc-content"
                    className="gf-form-textarea"
                    style={{ minHeight: '140px', fontFamily: 'monospace' }}
                    placeholder="# Document Header&#10;&#10;Write initial markdown here..."
                    value={newContent}
                    onChange={(e) => setNewContent(e.target.value)}
                  />
                </div>
              </div>

              <div className="gf-modal-footer">
                <Button
                  as="button"
                  variant="secondary"
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  as="button"
                  variant="primary"
                  type="submit"
                  id="submit-doc-btn"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Creating...' : 'Create Document'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
