import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectInstance, getMentorInstanceDocuments } from '@/lib/api/client';
import type { MentorProjectInstanceDetail, DocumentResponse } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceDocuments.css';

export const MentorInstanceDocuments: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [activeDoc, setActiveDoc] = useState<DocumentResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const [projRes, docsRes] = await Promise.all([
          getMentorProjectInstance(projectId),
          getMentorInstanceDocuments(projectId),
        ]);
        if (mounted) {
          setProject(projRes);
          setDocuments(docsRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          setError(
            err instanceof Error
              ? err.message
              : 'Failed to retrieve project documents or access denied.'
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

  const filteredDocs = useMemo(() => {
    return documents.filter((d) => {
      if (typeFilter !== 'ALL' && d.doc_type !== typeFilter) return false;
      if (search.trim()) {
        const query = search.toLowerCase();
        const matchesTitle = d.title.toLowerCase().includes(query);
        const matchesKey = d.document_key.toLowerCase().includes(query);
        if (!matchesTitle && !matchesKey) return false;
      }
      return true;
    });
  }, [documents, typeFilter, search]);

  if (loading) {
    return (
      <div className="gf-mentor-docs-page" id="mentor-docs-loading">
        <Skeleton width="100%" height="160px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <Skeleton width="100%" height="56px" style={{ borderRadius: '8px', marginBottom: '1rem' }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          <Skeleton width="100%" height="180px" style={{ borderRadius: '12px' }} />
          <Skeleton width="100%" height="180px" style={{ borderRadius: '12px' }} />
          <Skeleton width="100%" height="180px" style={{ borderRadius: '12px' }} />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-mentor-docs-page" id="mentor-docs-error">
        <div className="gf-mentor-docs-error-card" role="alert">
          <h3>Document Supervision Restricted</h3>
          <p>{error || 'Project documents not found or access denied.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-docs-page" id="mentor-docs-container">
      <MentorInstanceHeader project={project} activeTab="documents" />

      {/* Filter and Search Bar (Read-Only) */}
      <div className="gf-mentor-docs__toolbar" id="mentor-docs-toolbar">
        <div className="gf-mentor-docs__search-wrap">
          <Input
            id="mentor-docs-search"
            type="search"
            placeholder="Search documents by title or key..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="gf-mentor-docs__filters">
          <label className="gf-mentor-docs__filter-label">
            <span>Type:</span>
            <select
              id="filter-doc-type"
              className="gf-mentor-docs__select"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="ALL">All Types</option>
              <option value="BLUEPRINT">Blueprint</option>
              <option value="SPECIFICATION">Specification</option>
              <option value="README">README</option>
              <option value="REPORT">Report</option>
              <option value="OTHER">Other</option>
            </select>
          </label>
        </div>
      </div>

      <div className="gf-mentor-docs__content">
        <div className="gf-mentor-docs__header-info">
          <span>
            Showing <strong>{filteredDocs.length}</strong> of <strong>{documents.length}</strong> documents
          </span>
          <span className="gf-mentor-docs__read-only-indicator">READ-ONLY SUPERVISION</span>
        </div>

        {filteredDocs.length === 0 ? (
          <div className="gf-mentor-docs__empty-state" id="mentor-docs-empty">
            <p>No project documents match the criteria or no documents have been published.</p>
          </div>
        ) : (
          <div className="gf-mentor-docs__grid" id="mentor-docs-grid">
            {filteredDocs.map((doc) => (
              <div key={doc.id} className="gf-mentor-doc-card" id={`doc-card-${doc.id}`}>
                <div className="gf-mentor-doc-card__top">
                  <Badge variant="info">{doc.doc_type}</Badge>
                  <span className="gf-mentor-doc-card__version">v{doc.version}</span>
                </div>

                <h3 className="gf-mentor-doc-card__title">{doc.title}</h3>
                <div className="gf-mentor-doc-card__key">{doc.document_key}</div>

                <div className="gf-mentor-doc-card__meta">
                  <span>Format: <strong>{doc.format.toUpperCase()}</strong></span>
                  <span>Status: <strong>{doc.status}</strong></span>
                </div>

                <div className="gf-mentor-doc-card__footer">
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    id={`view-doc-btn-${doc.id}`}
                    onClick={() => setActiveDoc(doc)}
                  >
                    Inspect Document
                  </Button>
                  <span className="gf-mentor-doc-card__date">
                    Updated {new Date(doc.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Read-Only Document Inspection Modal */}
      {activeDoc && (
        <div className="gf-mentor-doc-modal-overlay" role="dialog" aria-modal="true" id="doc-inspect-modal">
          <div className="gf-mentor-doc-modal">
            <div className="gf-mentor-doc-modal__header">
              <div>
                <span className="gf-mentor-doc-modal__tag">READ-ONLY INSPECTION</span>
                <h3 className="gf-mentor-doc-modal__title">{activeDoc.title}</h3>
              </div>
              <button
                type="button"
                className="gf-mentor-doc-modal__close-btn"
                id="close-doc-modal-btn"
                onClick={() => setActiveDoc(null)}
              >
                ✕
              </button>
            </div>

            <div className="gf-mentor-doc-modal__body">
              <pre className="gf-mentor-doc-modal__preview">{activeDoc.content}</pre>
            </div>

            <div className="gf-mentor-doc-modal__footer">
              <Button type="button" variant="secondary" onClick={() => setActiveDoc(null)}>
                Close Preview
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
