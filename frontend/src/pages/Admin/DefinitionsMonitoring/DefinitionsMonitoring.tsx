import { useEffect, useState, useTransition } from 'react';
import { getAdminDefinitions, getAdminDefinition } from '@/lib/api/client';
import type {
  AdminProjectDefinitionSummary,
  AdminProjectDefinitionDetail,
} from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './DefinitionsMonitoring.css';

/**
 * AD09 — Project Definition Monitoring
 *
 * Governance view for inspecting mentor-created project templates,
 * immutable version trees, and student adoption volumes.
 */
export function DefinitionsMonitoring() {
  const [definitions, setDefinitions] = useState<AdminProjectDefinitionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [, startTransition] = useTransition();

  // Detail Modal State
  const [selectedDefinition, setSelectedDefinition] = useState<AdminProjectDefinitionDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const fetchDefinitions = async (s: string, st: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminDefinitions({
        search: s.trim() || undefined,
        status: st !== 'ALL' ? st : undefined,
      });
      setDefinitions(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve project definitions.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDefinitions(search, statusFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    startTransition(() => {
      fetchDefinitions(val, statusFilter);
    });
  };

  const handleInspect = async (defId: string) => {
    try {
      setLoadingDetail(true);
      setDetailError(null);
      const detail = await getAdminDefinition(defId);
      setSelectedDefinition(detail);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve version details.';
      setDetailError(msg);
    } finally {
      setLoadingDetail(false);
    }
  };

  const getStatusBadge = (status?: string | null) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE':
        return <Badge variant="success">Active</Badge>;
      case 'DRAFT':
        return <Badge variant="neutral">Draft</Badge>;
      case 'ARCHIVED':
        return <Badge variant="neutral">Archived</Badge>;
      default:
        return <Badge variant="neutral">{status ?? 'UNKNOWN'}</Badge>;
    }
  };

  return (
    <div className="gf-defs-monitoring">
      <PageHeader
        eyebrow="RESOURCE GOVERNANCE"
        title="Project Definition Monitoring"
        description="Inspect mentor-created project templates, immutable version trees, and student adoptions."
      />

      {error && (
        <div className="gf-defs-monitoring__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={() => fetchDefinitions(search, statusFilter)}>
            Retry
          </Button>
        </div>
      )}

      {/* Toolbar & Filters */}
      <div className="gf-defs-monitoring__toolbar">
        <div className="gf-defs-monitoring__search-wrapper">
          <svg className="gf-defs-monitoring__search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="9" cy="9" r="6" />
            <line x1="13.5" y1="13.5" x2="18" y2="18" />
          </svg>
          <input
            type="search"
            placeholder="Search by template name or owning mentor..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="gf-defs-monitoring__search-input"
            aria-label="Search definitions"
          />
        </div>

        <div className="gf-defs-monitoring__filters">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="gf-defs-monitoring__select"
            aria-label="Filter by definition status"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="DRAFT">Draft</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>
      </div>

      {/* Definitions Table */}
      {loading ? (
        <Card className="gf-defs-monitoring__card">
          <div className="gf-defs-monitoring__skeleton-wrap">
            <Skeleton height="40px" className="gf-mb-3" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" />
          </div>
        </Card>
      ) : definitions.length === 0 ? (
        <EmptyState
          title="No project definitions found"
          description={
            search || statusFilter !== 'ALL'
              ? 'No definitions match your search or filter criteria.'
              : 'There are currently no mentor project definitions registered on the platform.'
          }
        />
      ) : (
        <Card className="gf-defs-monitoring__card">
          <div className="gf-defs-monitoring__table-responsive">
            <table className="gf-defs-monitoring__table">
              <thead>
                <tr>
                  <th scope="col">Definition Title</th>
                  <th scope="col">Authoring Mentor</th>
                  <th scope="col">Current Version</th>
                  <th scope="col">Complexity</th>
                  <th scope="col">Adoptions</th>
                  <th scope="col">Status</th>
                  <th scope="col">Created Date</th>
                  <th scope="col"><span className="gf-sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {definitions.map((def) => (
                  <tr key={def.id}>
                    <td>
                      <div className="gf-defs-monitoring__title-cell">
                        <button
                          type="button"
                          onClick={() => handleInspect(def.id)}
                          className="gf-defs-monitoring__title-btn"
                        >
                          {def.name}
                        </button>
                      </div>
                    </td>
                    <td>
                      <div className="gf-defs-monitoring__mentor-cell">
                        <span className="gf-defs-monitoring__mentor-name">{def.owner_mentor_name}</span>
                        <span className="gf-defs-monitoring__mentor-email">{def.owner_mentor_email}</span>
                      </div>
                    </td>
                    <td>
                      <span className="gf-defs-monitoring__version-badge">
                        v{def.current_version_number ?? 1}
                      </span>
                    </td>
                    <td>
                      <Badge variant="neutral">{def.complexity || 'INTERMEDIATE'}</Badge>
                    </td>
                    <td>
                      <span className="gf-defs-monitoring__count-badge">
                        {def.instance_count} instance{def.instance_count === 1 ? '' : 's'}
                      </span>
                    </td>
                    <td>{getStatusBadge(def.status)}</td>
                    <td>
                      <span className="gf-defs-monitoring__date">
                        {def.created_at ? new Date(def.created_at).toLocaleDateString() : 'N/A'}
                      </span>
                    </td>
                    <td className="gf-defs-monitoring__actions">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleInspect(def.id)}
                      >
                        Inspect Tree
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Version Inspection Modal / Drawer */}
      {(selectedDefinition || loadingDetail || detailError) && (
        <div className="gf-defs-monitoring__modal-backdrop" role="dialog" aria-modal="true">
          <div className="gf-defs-monitoring__modal">
            <div className="gf-defs-monitoring__modal-header">
              <div>
                <span className="gf-defs-monitoring__modal-eyebrow">IMMUTABLE VERSION INSPECTION</span>
                <h2 className="gf-defs-monitoring__modal-title">
                  {selectedDefinition?.name || 'Loading Definition...'}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => {
                  setSelectedDefinition(null);
                  setDetailError(null);
                }}
                className="gf-defs-monitoring__close-btn"
                aria-label="Close modal"
              >
                &times;
              </button>
            </div>

            <div className="gf-defs-monitoring__modal-body">
              {loadingDetail ? (
                <div>
                  <Skeleton height="32px" className="gf-mb-3" />
                  <Skeleton height="120px" className="gf-mb-3" />
                  <Skeleton height="120px" />
                </div>
              ) : detailError ? (
                <div className="gf-defs-monitoring__alert" role="alert">
                  <span>{detailError}</span>
                </div>
              ) : selectedDefinition ? (
                <>
                  <div className="gf-defs-monitoring__immutability-notice">
                    <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" aria-hidden="true">
                      <path fillRule="evenodd" d="M10 1a9 9 0 100 18 9 9 0 000-18zm0 8.2a1 1 0 011 1v4a1 1 0 11-2 0v-4a1 1 0 011-1zm0-3.4a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clipRule="evenodd" />
                    </svg>
                    <span>
                      Immutable Version Tree • Pinned snapshots cannot be modified. Governance observation mode.
                    </span>
                  </div>

                  <div className="gf-defs-monitoring__meta-row">
                    <div>
                      <span className="gf-defs-monitoring__meta-label">Authoring Mentor:</span>
                      <span className="gf-defs-monitoring__meta-value">
                        {selectedDefinition.owner_mentor_name} ({selectedDefinition.owner_mentor_email})
                      </span>
                    </div>
                    <div>
                      <span className="gf-defs-monitoring__meta-label">Adoptions:</span>
                      <span className="gf-defs-monitoring__meta-value">
                        {selectedDefinition.instance_count} Student Project{selectedDefinition.instance_count === 1 ? '' : 's'}
                      </span>
                    </div>
                  </div>

                  {/* Versions List */}
                  <h3 className="gf-defs-monitoring__section-title">
                    Immutable Versions ({selectedDefinition.versions.length})
                  </h3>
                  <div className="gf-defs-monitoring__versions-list">
                    {selectedDefinition.versions.map((ver) => (
                      <div key={ver.id} className="gf-defs-monitoring__version-card">
                        <div className="gf-defs-monitoring__version-card-header">
                          <span className="gf-defs-monitoring__version-tag">Version {ver.version_number}</span>
                          <span className="gf-defs-monitoring__complexity-tag">{ver.complexity}</span>
                          <span className="gf-defs-monitoring__version-date">
                            Created {new Date(ver.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="gf-defs-monitoring__version-content">
                          {ver.problem && (
                            <div className="gf-defs-monitoring__ver-field">
                              <strong>Problem Statement:</strong>
                              <p>{ver.problem}</p>
                            </div>
                          )}
                          {ver.proposed_solution && (
                            <div className="gf-defs-monitoring__ver-field">
                              <strong>Proposed Solution:</strong>
                              <p>{ver.proposed_solution}</p>
                            </div>
                          )}
                          {ver.duration && (
                            <div className="gf-defs-monitoring__ver-field">
                              <strong>Estimated Duration:</strong> {ver.duration}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Adopted Instances */}
                  <h3 className="gf-defs-monitoring__section-title gf-mt-4">
                    Active Student Adoptions ({selectedDefinition.assigned_instances.length})
                  </h3>
                  {selectedDefinition.assigned_instances.length === 0 ? (
                    <p className="gf-defs-monitoring__muted-text">
                      No student project instances are currently assigned to this definition template.
                    </p>
                  ) : (
                    <div className="gf-defs-monitoring__instances-grid">
                      {selectedDefinition.assigned_instances.map((inst) => (
                        <div key={inst.id} className="gf-defs-monitoring__inst-item">
                          <span className="gf-defs-monitoring__inst-name">{inst.name}</span>
                          <span className="gf-defs-monitoring__inst-student">Student: {inst.student_name}</span>
                          <div className="gf-defs-monitoring__inst-tags">
                            <span className="gf-defs-monitoring__phase-tag">{inst.current_phase}</span>
                            <Badge variant={inst.health === 'HEALTHY' ? 'success' : inst.health === 'WARNING' ? 'warning' : 'danger'}>
                              {inst.health}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              ) : null}
            </div>

            <div className="gf-defs-monitoring__modal-footer">
              <Button
                variant="secondary"
                onClick={() => {
                  setSelectedDefinition(null);
                  setDetailError(null);
                }}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
