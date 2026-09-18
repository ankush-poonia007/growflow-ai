import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminDocuments } from '@/lib/api/client';
import type { AdminDocumentsResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './DocumentsRAG.css';

/**
 * Format raw byte length into human-readable size.
 */
function formatBytes(bytes: number): string {
  if (!bytes || bytes <= 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/**
 * Format ISO datetime string to localized date.
 */
function formatDate(iso: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

/**
 * AD21 — Documents & Knowledge Management
 *
 * Platform-wide deliverable governance exposing canonical project_documents,
 * blueprints, specifications, readmes, and architecture records with bounded pagination.
 */
export function DocumentsRAG() {
  const [data, setData] = useState<AdminDocumentsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Pagination
  const [search, setSearch] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [page, setPage] = useState(0);
  const pageSize = 25;
  const [, startTransition] = useTransition();

  const fetchDocs = async (s: string, dt: string, st: string, p: number) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminDocuments({
        search: s.trim() || undefined,
        doc_type: dt !== 'ALL' ? dt : undefined,
        status: st !== 'ALL' ? st : undefined,
        limit: pageSize,
        offset: p * pageSize,
      });
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve documents.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs(search, docTypeFilter, statusFilter, page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [docTypeFilter, statusFilter, page]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    setPage(0);
    startTransition(() => {
      fetchDocs(val, docTypeFilter, statusFilter, 0);
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE':
        return <Badge variant="success">Active</Badge>;
      case 'DRAFT':
        return <Badge variant="warning">Draft</Badge>;
      case 'ARCHIVED':
        return <Badge variant="neutral">Archived</Badge>;
      default:
        return <Badge variant="neutral">{status || 'Unknown'}</Badge>;
    }
  };

  const getDocTypeBadge = (docType: string) => {
    switch (docType?.toUpperCase()) {
      case 'BLUEPRINT':
        return <Badge variant="neutral">Blueprint</Badge>;
      case 'SPECIFICATION':
        return <Badge variant="neutral">Specification</Badge>;
      case 'README':
        return <Badge variant="neutral">Readme</Badge>;
      case 'ARCHITECTURE':
        return <Badge variant="neutral">Architecture</Badge>;
      default:
        return <Badge variant="neutral">{docType || 'Document'}</Badge>;
    }
  };

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;
  const docCounts = data?.doc_type_counts || {};

  return (
    <div className="gf-docs-rag">
      <PageHeader
        eyebrow="DELIVERABLE GOVERNANCE"
        title="Documents & Knowledge"
        description="Platform deliverable inventory tracking blueprints, specifications, project documentation, and retrieval corpus."
        actions={
          <div className="gf-docs-rag__header-actions">
            <Link to="/admin/documents/rag">
              <Button variant="secondary" size="sm">
                RAG Monitoring
              </Button>
            </Link>
            <Link to="/admin/documents/generation">
              <Button variant="secondary" size="sm">
                Generation Runs
              </Button>
            </Link>
            <Button
              variant="tertiary"
              size="sm"
              onClick={() => fetchDocs(search, docTypeFilter, statusFilter, page)}
            >
              Refresh
            </Button>
          </div>
        }
      />

      {error && (
        <div className="gf-docs-rag__alert" role="alert">
          <span>{error}</span>
          <Button
            variant="tertiary"
            size="sm"
            onClick={() => fetchDocs(search, docTypeFilter, statusFilter, page)}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Summary Metrics */}
      <div className="gf-docs-rag__summary-grid">
        <StatTile
          label="Total Documents"
          value={loading && !data ? '—' : (data?.total ?? 0)}
          subtext="Authoritative database records"
        />
        <StatTile
          label="Blueprints"
          value={loading && !data ? '—' : (docCounts['BLUEPRINT'] ?? 0)}
          subtext="Generated system blueprints"
        />
        <StatTile
          label="Specifications"
          value={loading && !data ? '—' : (docCounts['SPECIFICATION'] ?? 0)}
          subtext="Technical & module specs"
        />
        <StatTile
          label="Readmes"
          value={loading && !data ? '—' : (docCounts['README'] ?? 0)}
          subtext="Project documentation files"
        />
      </div>

      {/* Filters Toolbar */}
      <Card className="gf-docs-rag__filter-card">
        <div className="gf-docs-rag__filters">
          <div className="gf-docs-rag__filter-group gf-docs-rag__filter-group--search">
            <label htmlFor="docs-search" className="gf-docs-rag__filter-label">
              Search
            </label>
            <input
              id="docs-search"
              type="text"
              className="gf-docs-rag__input"
              placeholder="Search by title, key, or format..."
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
            />
          </div>

          <div className="gf-docs-rag__filter-group">
            <label htmlFor="docs-type" className="gf-docs-rag__filter-label">
              Document Type
            </label>
            <select
              id="docs-type"
              className="gf-docs-rag__select"
              value={docTypeFilter}
              onChange={(e) => {
                setDocTypeFilter(e.target.value);
                setPage(0);
              }}
            >
              <option value="ALL">All Types</option>
              <option value="BLUEPRINT">Blueprint</option>
              <option value="SPECIFICATION">Specification</option>
              <option value="README">Readme</option>
              <option value="ARCHITECTURE">Architecture</option>
            </select>
          </div>

          <div className="gf-docs-rag__filter-group">
            <label htmlFor="docs-status" className="gf-docs-rag__filter-label">
              Status
            </label>
            <select
              id="docs-status"
              className="gf-docs-rag__select"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(0);
              }}
            >
              <option value="ALL">All Statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="DRAFT">Draft</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Documents Table */}
      <Card className="gf-docs-rag__table-card">
        {loading && !data ? (
          <div className="gf-docs-rag__loading">
            <Skeleton height="40px" className="mb-2" />
            <Skeleton height="56px" className="mb-2" />
            <Skeleton height="56px" className="mb-2" />
            <Skeleton height="56px" className="mb-2" />
            <Skeleton height="56px" />
          </div>
        ) : !data?.documents || data.documents.length === 0 ? (
          <EmptyState
            title="No Documents Found"
            description={
              search || docTypeFilter !== 'ALL' || statusFilter !== 'ALL'
                ? 'No documents match your filter criteria. Try resetting your search filters.'
                : 'No project documents or blueprint records have been recorded yet.'
            }
          />
        ) : (
          <div className="gf-table-container">
            <table className="gf-table gf-docs-rag__table" aria-label="Platform Documents">
              <thead>
                <tr>
                  <th scope="col">Document</th>
                  <th scope="col">Project</th>
                  <th scope="col">Type</th>
                  <th scope="col">Format</th>
                  <th scope="col">Version</th>
                  <th scope="col">Status</th>
                  <th scope="col">Source</th>
                  <th scope="col">Size</th>
                  <th scope="col">Created</th>
                </tr>
              </thead>
              <tbody>
                {data.documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <div className="gf-docs-rag__doc-cell">
                        <span className="gf-docs-rag__doc-title">{doc.title}</span>
                        <code className="gf-docs-rag__doc-key">{doc.document_key}</code>
                      </div>
                    </td>
                    <td>
                      <span className="gf-docs-rag__project-name">
                        {doc.project_name || '—'}
                      </span>
                    </td>
                    <td>{getDocTypeBadge(doc.doc_type)}</td>
                    <td>
                      <span className="gf-docs-rag__format-tag">
                        {doc.format?.toUpperCase() || 'MD'}
                      </span>
                    </td>
                    <td>
                      <span className="gf-docs-rag__version">v{doc.version || '1.0'}</span>
                    </td>
                    <td>{getStatusBadge(doc.status)}</td>
                    <td>
                      <span className="gf-docs-rag__source">{doc.source || 'CANONICAL'}</span>
                    </td>
                    <td>
                      <span className="gf-docs-rag__size">{formatBytes(doc.size_bytes)}</span>
                    </td>
                    <td>
                      <span className="gf-docs-rag__date">{formatDate(doc.created_at)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Toolbar */}
        {data && data.total > 0 && (
          <div className="gf-docs-rag__pagination">
            <span className="gf-docs-rag__pagination-info">
              Showing {data.offset + 1} to {Math.min(data.offset + data.limit, data.total)} of{' '}
              {data.total} documents
            </span>
            <div className="gf-docs-rag__pagination-controls">
              <Button
                variant="secondary"
                size="sm"
                disabled={page === 0 || loading}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
              >
                Previous
              </Button>
              <span className="gf-docs-rag__page-indicator">
                Page {page + 1} of {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages - 1 || loading}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
