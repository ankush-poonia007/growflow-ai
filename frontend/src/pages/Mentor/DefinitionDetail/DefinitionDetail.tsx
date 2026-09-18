import { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorDefinition, getDefinitionVersions } from '@/lib/api/client';
import type { ProjectDefinition, ProjectDefinitionVersion } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import './DefinitionDetail.css';

export function DefinitionDetail() {
  const { definitionId } = useParams<{ definitionId: string }>();
  const [definition, setDefinition] = useState<ProjectDefinition | null>(null);
  const [versions, setVersions] = useState<ProjectDefinitionVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedVersionId, setExpandedVersionId] = useState<string | null>(null);

  async function loadData() {
    if (!definitionId) return;
    try {
      setLoading(true);
      setError(null);
      const [defRes, verRes] = await Promise.all([
        getMentorDefinition(definitionId),
        getDefinitionVersions(definitionId),
      ]);
      setDefinition(defRes);
      setVersions(verRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load project definition details.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [definitionId]);

  if (loading) {
    return (
      <div className="gf-definition-detail gf-definition-detail--loading" aria-busy="true">
        <Skeleton height="64px" />
        <div className="gf-definition-detail__body-grid">
          <Skeleton height="240px" />
          <Skeleton height="240px" />
        </div>
        <Skeleton height="180px" />
      </div>
    );
  }

  if (error || !definition) {
    return (
      <div className="gf-definition-detail gf-definition-detail--error" role="alert">
        <div className="gf-definition-detail__error-card">
          <h1 className="gf-definition-detail__error-title">Unable to Load Definition</h1>
          <p className="gf-definition-detail__error-desc">
            {error || 'The requested project definition does not exist or you lack authorization.'}
          </p>
          <div className="gf-definition-detail__error-actions">
            <Button as="link" to="/mentor/projects" variant="secondary">
              Back to Definitions
            </Button>
            <Button variant="primary" onClick={loadData}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const curVer = definition.current_version;
  const verNum = curVer?.version_number ?? 1;

  const getComplexityVariant = (complexity?: string): 'neutral' | 'accent' | 'warning' => {
    switch (complexity?.toUpperCase()) {
      case 'BEGINNER':
        return 'neutral';
      case 'INTERMEDIATE':
        return 'accent';
      case 'ADVANCED':
        return 'warning';
      default:
        return 'neutral';
    }
  };

  const getStatusVariant = (status: string): 'success' | 'warning' | 'neutral' => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return 'success';
      case 'DRAFT':
        return 'warning';
      case 'ARCHIVED':
        return 'neutral';
      default:
        return 'neutral';
    }
  };

  return (
    <div className="gf-definition-detail" role="main" aria-labelledby="definition-title">
      <PageHeader
        eyebrow="PROJECT DEFINITION"
        title={definition.name}
        description={`Reusable mentor-authored specification. Current snapshot is version ${verNum}.`}
        breadcrumbs={[
          { label: 'Definitions', to: '/mentor/projects' },
          { label: definition.name },
        ]}
        action={
          <div className="gf-definition-detail__header-actions">
            <Button
              as="link"
              to={`/mentor/projects/${definition.id}/edit`}
              variant="secondary"
              size="sm"
            >
              Edit Definition
            </Button>
            <Button
              as="link"
              to={`/mentor/projects/${definition.id}/assign`}
              variant="primary"
              size="sm"
            >
              Assign to Student
            </Button>
          </div>
        }
      />

      {/* Meta Bar */}
      <div className="gf-definition-detail__meta-bar">
        <div className="gf-definition-detail__badges">
          <Badge variant="accent" size="sm">
            Current: v{verNum}
          </Badge>
          <Badge variant={getStatusVariant(definition.status)} size="sm">
            {definition.status}
          </Badge>
          <Badge variant={getComplexityVariant(curVer?.complexity)} size="sm">
            {curVer?.complexity || 'INTERMEDIATE'}
          </Badge>
          {curVer?.duration && (
            <span className="gf-definition-detail__duration">
              Estimated Duration: <strong>{curVer.duration}</strong>
            </span>
          )}
        </div>
        <div className="gf-definition-detail__timestamps">
          {definition.updated_at && (
            <span>
              Last Updated:{' '}
              {new Date(definition.updated_at).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </span>
          )}
        </div>
      </div>

      {/* Grid: Core Specs & Scope */}
      <div className="gf-definition-detail__body-grid">
        {/* Core Specs Card */}
        <Card className="gf-definition-detail__card">
          <h2 className="gf-definition-detail__card-title">Specification Snapshot</h2>

          <div className="gf-definition-detail__field">
            <h3 className="gf-definition-detail__field-label">Problem Statement</h3>
            <p className="gf-definition-detail__field-text">
              {curVer?.problem || 'No problem statement defined.'}
            </p>
          </div>

          <div className="gf-definition-detail__field">
            <h3 className="gf-definition-detail__field-label">Proposed Solution</h3>
            <p className="gf-definition-detail__field-text">
              {curVer?.proposed_solution || 'No proposed solution defined.'}
            </p>
          </div>

          {curVer?.description && (
            <div className="gf-definition-detail__field">
              <h3 className="gf-definition-detail__field-label">Description & Objectives</h3>
              <p className="gf-definition-detail__field-text">{curVer.description}</p>
            </div>
          )}
        </Card>

        {/* Parameters & Tech Card */}
        <Card className="gf-definition-detail__card">
          <h2 className="gf-definition-detail__card-title">Scope & Guardrails</h2>

          <div className="gf-definition-detail__field">
            <h3 className="gf-definition-detail__field-label">Constraints</h3>
            <p className="gf-definition-detail__field-text">
              {curVer?.constraints || 'No explicit constraints specified.'}
            </p>
          </div>

          <div className="gf-definition-detail__field">
            <h3 className="gf-definition-detail__field-label">Assumptions</h3>
            <p className="gf-definition-detail__field-text">
              {curVer?.assumptions || 'No explicit assumptions specified.'}
            </p>
          </div>

          <div className="gf-definition-detail__field">
            <h3 className="gf-definition-detail__field-label">Technology Snapshot</h3>
            {curVer?.technology_snapshot && curVer.technology_snapshot.length > 0 ? (
              <div className="gf-definition-detail__tech-tags">
                {curVer.technology_snapshot.map((tech, idx) => (
                  <Badge key={idx} variant="neutral" size="sm">
                    {String(tech.name || tech.label || tech.title || JSON.stringify(tech))}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="gf-definition-detail__field-text" style={{ color: 'var(--text-tertiary)' }}>
                No initial technologies pinned to this snapshot.
              </p>
            )}
          </div>
        </Card>
      </div>

      {/* Version History Section */}
      <Card className="gf-definition-detail__versions-card">
        <div className="gf-definition-detail__versions-header">
          <div>
            <h2 className="gf-definition-detail__card-title">Version History</h2>
            <p className="gf-definition-detail__versions-sub">
              Auditable immutable snapshots. Historical versions remain frozen to preserve student project isolation.
            </p>
          </div>
          <Badge variant="neutral" size="sm">
            {versions.length} {versions.length === 1 ? 'Version' : 'Versions'} Total
          </Badge>
        </div>

        <div className="gf-definition-detail__versions-list">
          {versions.map((ver) => {
            const isCurrent = ver.id === definition.current_version_id;
            const isExpanded = expandedVersionId === ver.id;
            const createdDate = ver.created_at
              ? new Date(ver.created_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              : 'Unknown date';

            return (
              <div
                key={ver.id}
                className={`gf-definition-detail__version-item ${
                  isCurrent ? 'gf-definition-detail__version-item--current' : ''
                }`}
              >
                <div className="gf-definition-detail__version-main">
                  <div className="gf-definition-detail__version-badge-col">
                    <span className="gf-definition-detail__version-num">
                      v{ver.version_number}
                    </span>
                    {isCurrent ? (
                      <Badge variant="success" size="sm">
                        Current
                      </Badge>
                    ) : (
                      <Badge variant="neutral" size="sm">
                        Historical
                      </Badge>
                    )}
                  </div>

                  <div className="gf-definition-detail__version-info">
                    <div className="gf-definition-detail__version-title-row">
                      <span className="gf-definition-detail__version-name">{ver.name}</span>
                      <span className="gf-definition-detail__version-date">{createdDate}</span>
                    </div>
                    <p className="gf-definition-detail__version-snippet">
                      {ver.problem}
                    </p>
                  </div>

                  <Button
                    variant="tertiary"
                    size="sm"
                    onClick={() =>
                      setExpandedVersionId(isExpanded ? null : ver.id)
                    }
                    aria-expanded={isExpanded}
                  >
                    {isExpanded ? 'Hide Details' : 'View Snapshot'}
                  </Button>
                </div>

                {isExpanded && (
                  <div className="gf-definition-detail__version-expanded">
                    <div className="gf-definition-detail__expanded-row">
                      <strong>Complexity:</strong> {ver.complexity}
                    </div>
                    <div className="gf-definition-detail__expanded-row">
                      <strong>Proposed Solution:</strong> {ver.proposed_solution}
                    </div>
                    {ver.description && (
                      <div className="gf-definition-detail__expanded-row">
                        <strong>Description:</strong> {ver.description}
                      </div>
                    )}
                    {ver.duration && (
                      <div className="gf-definition-detail__expanded-row">
                        <strong>Duration:</strong> {ver.duration}
                      </div>
                    )}
                    {ver.constraints && (
                      <div className="gf-definition-detail__expanded-row">
                        <strong>Constraints:</strong> {ver.constraints}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
