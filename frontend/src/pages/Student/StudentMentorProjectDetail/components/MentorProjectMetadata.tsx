import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

interface MentorProjectMetadataProps {
  definition: ProjectDefinitionCatalogItem;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

export function MentorProjectMetadata({ definition }: MentorProjectMetadataProps) {
  return (
    <Card as="section" className="gf-detail-sidebar-card" variant="bordered" aria-labelledby="sidebar-metadata-title">
      <CardHeader className="gf-detail-sidebar-card__header">
        <CardTitle as="h2" id="sidebar-metadata-title" className="gf-detail-sidebar-card__title">
          Project Metadata
        </CardTitle>
      </CardHeader>

      <CardContent className="gf-detail-sidebar-card__content">
        <dl className="gf-detail-meta-list">
          {/* Complexity */}
          <div className="gf-detail-meta-item">
            <dt className="gf-detail-meta-item__term">Complexity</dt>
            <dd className="gf-detail-meta-item__detail">
              {definition.complexity ? (
                <Badge variant="accent">{definition.complexity}</Badge>
              ) : (
                <span className="gf-detail-meta-item__value">Intermediate</span>
              )}
            </dd>
          </div>

          {/* Expected Duration */}
          <div className="gf-detail-meta-item">
            <dt className="gf-detail-meta-item__term">Duration</dt>
            <dd className="gf-detail-meta-item__detail">
              <span className="gf-detail-meta-item__value">
                {definition.duration || 'Flexible timeline'}
              </span>
            </dd>
          </div>

          {/* Published Version */}
          <div className="gf-detail-meta-item">
            <dt className="gf-detail-meta-item__term">Published Version</dt>
            <dd className="gf-detail-meta-item__detail">
              <span className="gf-detail-meta-item__value">
                v{definition.version_number ?? 1}
              </span>
            </dd>
          </div>

          {/* Definition Status */}
          <div className="gf-detail-meta-item">
            <dt className="gf-detail-meta-item__term">Catalog Status</dt>
            <dd className="gf-detail-meta-item__detail">
              <Badge variant="neutral">{definition.status}</Badge>
            </dd>
          </div>

          {/* Published Date */}
          {definition.created_at && (
            <div className="gf-detail-meta-item">
              <dt className="gf-detail-meta-item__term">Published</dt>
              <dd className="gf-detail-meta-item__detail">
                <span className="gf-detail-meta-item__value">
                  {formatDate(definition.created_at)}
                </span>
              </dd>
            </div>
          )}

          {/* Last Updated */}
          {definition.updated_at && definition.updated_at !== definition.created_at && (
            <div className="gf-detail-meta-item">
              <dt className="gf-detail-meta-item__term">Last Updated</dt>
              <dd className="gf-detail-meta-item__detail">
                <span className="gf-detail-meta-item__value">
                  {formatDate(definition.updated_at)}
                </span>
              </dd>
            </div>
          )}
        </dl>
      </CardContent>
    </Card>
  );
}
