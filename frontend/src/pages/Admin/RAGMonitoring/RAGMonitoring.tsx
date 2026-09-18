import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminRAGDiagnostics } from '@/lib/api/client';
import type { AdminRAGDiagnostics } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './RAGMonitoring.css';

/**
 * Format ISO datetime string to localized date/time.
 */
function formatDateTime(iso: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

/**
 * AD22 — RAG Subsystem Monitoring
 *
 * Operational governance interface reflecting the truthful architecture posture of RAG:
 * displays deferred/standby state without synthetic vectors, latency charts, or fake metrics.
 */
export function RAGMonitoring() {
  const [data, setData] = useState<AdminRAGDiagnostics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDiagnostics = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminRAGDiagnostics();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve RAG diagnostics.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
  }, []);

  const getStatusBadge = (status?: string) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE':
        return <Badge variant="success">Active</Badge>;
      case 'DEFERRED_INTEGRATION':
      case 'STANDBY':
        return <Badge variant="warning">Deferred Integration</Badge>;
      case 'NONE_CONFIGURED':
        return <Badge variant="neutral">None Configured</Badge>;
      default:
        return <Badge variant="neutral">{status || 'Standby'}</Badge>;
    }
  };

  return (
    <div className="gf-rag-monitoring">
      <div className="gf-rag-monitoring__breadcrumb">
        <Link to="/admin/documents" className="gf-rag-monitoring__back-link">
          ← Back to Documents & Knowledge
        </Link>
      </div>

      <PageHeader
        eyebrow="INTELLIGENCE INFRASTRUCTURE"
        title="RAG Subsystem Monitoring"
        description="Truthful operational diagnostics for platform retrieval-augmented generation and vector indexing posture."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchDiagnostics}>
            Refresh Diagnostics
          </Button>
        }
      />

      {error && (
        <div className="gf-rag-monitoring__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchDiagnostics}>
            Retry
          </Button>
        </div>
      )}

      {loading && !data ? (
        <div className="gf-rag-monitoring__loading">
          <Skeleton height="100px" className="mb-4" />
          <Skeleton height="160px" className="mb-4" />
          <Skeleton height="240px" />
        </div>
      ) : data ? (
        <>
          {/* Truthful Architectural Posture Callout */}
          <div className="gf-rag-monitoring__posture-banner" role="status">
            <div className="gf-rag-monitoring__posture-indicator">
              {getStatusBadge(data.status)}
            </div>
            <div className="gf-rag-monitoring__posture-text">
              <h2 className="gf-rag-monitoring__posture-title">
                Vector Database Integration Posture: {data.status}
              </h2>
              <p className="gf-rag-monitoring__posture-desc">
                {data.posture_description ||
                  'Vector storage and retrieval infrastructure is currently deferred in this deployment. No external vector stores (ChromaDB, pgvector, Qdrant) are persisted.'}
              </p>
            </div>
          </div>

          {/* Primary Safe Configuration Metrics */}
          <div className="gf-rag-monitoring__stat-grid">
            <StatTile
              label="Vector Store"
              value={data.vector_store_type || 'NONE_CONFIGURED'}
              subtext="Vector database driver"
            />
            <StatTile
              label="Embedding Model"
              value={data.embedding_model || 'text-embedding-3-small'}
              subtext="Configured embedding engine"
            />
            <StatTile
              label="Eligible Corpus"
              value={data.eligible_documents_count}
              subtext="Platform documents available for indexing"
            />
            <StatTile
              label="Chunk Target"
              value={`${data.target_chunk_size} chars`}
              subtext={`Overlap: ${data.target_chunk_overlap} chars`}
            />
          </div>

          {/* Detailed Safe Configuration Card */}
          <Card className="gf-rag-monitoring__config-card">
            <CardHeader>
              <CardTitle>Configured Pipeline Parameters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="gf-rag-monitoring__params-grid">
                <div className="gf-rag-monitoring__param-item">
                  <span className="gf-rag-monitoring__param-label">Vector Storage Driver</span>
                  <span className="gf-rag-monitoring__param-value">
                    <code>{data.vector_store_type}</code>
                  </span>
                </div>
                <div className="gf-rag-monitoring__param-item">
                  <span className="gf-rag-monitoring__param-label">Target Embedding Model</span>
                  <span className="gf-rag-monitoring__param-value">
                    <code>{data.embedding_model}</code>
                  </span>
                </div>
                <div className="gf-rag-monitoring__param-item">
                  <span className="gf-rag-monitoring__param-label">Target Chunk Size</span>
                  <span className="gf-rag-monitoring__param-value">
                    {data.target_chunk_size} characters
                  </span>
                </div>
                <div className="gf-rag-monitoring__param-item">
                  <span className="gf-rag-monitoring__param-label">Target Chunk Overlap</span>
                  <span className="gf-rag-monitoring__param-value">
                    {data.target_chunk_overlap} characters
                  </span>
                </div>
                <div className="gf-rag-monitoring__param-item">
                  <span className="gf-rag-monitoring__param-label">Retrieval Top-K</span>
                  <span className="gf-rag-monitoring__param-value">
                    {data.target_top_k} nearest neighbors
                  </span>
                </div>
                <div className="gf-rag-monitoring__param-item">
                  <span className="gf-rag-monitoring__param-label">Index Generated Documents</span>
                  <span className="gf-rag-monitoring__param-value">
                    <Badge variant={data.index_generated_documents ? 'success' : 'neutral'}>
                      {data.index_generated_documents ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Ingestion / Document Domain Events */}
          <Card className="gf-rag-monitoring__events-card">
            <CardHeader className="gf-rag-monitoring__events-header">
              <CardTitle>Recent Pipeline & Deliverable Events</CardTitle>
            </CardHeader>
            <CardContent className="gf-rag-monitoring__events-content">
              {!data.recent_events || data.recent_events.length === 0 ? (
                <div className="gf-rag-monitoring__events-empty">
                  <EmptyState
                    title="No Ingestion Events"
                    description="No RAG indexing or deliverable pipeline events have been recorded in the platform event log."
                  />
                </div>
              ) : (
                <div className="gf-table-container">
                  <table className="gf-table gf-rag-monitoring__table" aria-label="Recent RAG Events">
                    <thead>
                      <tr>
                        <th scope="col">Event</th>
                        <th scope="col">Description</th>
                        <th scope="col">Status</th>
                        <th scope="col">Occurred</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.recent_events.map((evt) => (
                        <tr key={evt.id}>
                          <td>
                            <code className="gf-rag-monitoring__event-type">
                              {evt.event_type}
                            </code>
                          </td>
                          <td>
                            <div className="gf-rag-monitoring__event-desc">
                              <span className="gf-rag-monitoring__event-title">{evt.title}</span>
                              {evt.description && (
                                <span className="gf-rag-monitoring__event-subtitle">
                                  {evt.description}
                                </span>
                              )}
                            </div>
                          </td>
                          <td>
                            <Badge
                              variant={
                                evt.status === 'PUBLISHED'
                                  ? 'success'
                                  : evt.status === 'FAILED'
                                  ? 'danger'
                                  : 'neutral'
                              }
                            >
                              {evt.status}
                            </Badge>
                          </td>
                          <td>
                            <span className="gf-rag-monitoring__date">
                              {formatDateTime(evt.occurred_at)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}
