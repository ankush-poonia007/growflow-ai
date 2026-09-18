import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router';
import { getAdminAnalyticsDimension } from '@/lib/api/client';
import type { AdminAnalyticsDimensionDetail } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './AnalyticsDetail.css';

const VALID_DIMENSIONS = ['projects', 'users', 'documents', 'activity'] as const;

/**
 * Format label keys from snake_case to Title Case.
 */
function formatKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

/**
 * Format ISO datetime string.
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
 * Render key-value pair metrics or sub-dictionary items.
 */
function MetricTable({ data }: { data: Record<string, any> }) {
  const entries = Object.entries(data);
  if (entries.length === 0) {
    return <span className="gf-dim-detail__empty-sub">No metrics recorded</span>;
  }

  return (
    <div className="gf-dim-detail__metric-grid">
      {entries.map(([key, val]) => (
        <div key={key} className="gf-dim-detail__metric-tile">
          <span className="gf-dim-detail__metric-label">{formatKey(key)}</span>
          <span className="gf-dim-detail__metric-val">
            {typeof val === 'number'
              ? Number.isInteger(val)
                ? val
                : val.toFixed(1)
              : String(val ?? '—')}
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * Render dictionary distribution with percentage meters.
 */
function DistributionSubBlock({
  title,
  data,
}: {
  title: string;
  data: Record<string, number>;
}) {
  const entries = Object.entries(data);
  const total = entries.reduce((acc, [, val]) => acc + val, 0);

  return (
    <Card className="gf-dim-detail__sub-card">
      <CardHeader className="gf-dim-detail__sub-header">
        <CardTitle className="gf-dim-detail__sub-title">{title}</CardTitle>
        <span className="gf-dim-detail__sub-total">{total} Total</span>
      </CardHeader>
      <CardContent className="gf-dim-detail__sub-content">
        {entries.length === 0 ? (
          <span className="gf-dim-detail__empty-sub">No distribution records</span>
        ) : (
          <ul className="gf-dim-detail__dist-list">
            {entries.map(([key, count]) => {
              const pct = total > 0 ? Math.round((count / total) * 100) : 0;
              return (
                <li key={key} className="gf-dim-detail__dist-item">
                  <div className="gf-dim-detail__dist-meta">
                    <span className="gf-dim-detail__dist-key">{key}</span>
                    <span className="gf-dim-detail__dist-count">
                      {count} ({pct}%)
                    </span>
                  </div>
                  <div className="gf-dim-detail__meter-bg">
                    <div
                      className="gf-dim-detail__meter-fill"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * AD29 — Analytics Dimensional Detail
 *
 * Granular telemetric inspection for canonical platform dimensions:
 * projects, users, documents, and event activity.
 */
export function AnalyticsDetail() {
  const { dimension } = useParams<{ dimension: string }>();
  const [data, setData] = useState<AdminAnalyticsDimensionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isNotFound, setIsNotFound] = useState(false);

  const dim = (dimension || '').toLowerCase();
  const isValidDim = (VALID_DIMENSIONS as readonly string[]).includes(dim);

  const fetchDimension = async () => {
    if (!isValidDim) {
      setIsNotFound(true);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setIsNotFound(false);
      const res = await getAdminAnalyticsDimension(dim);
      setData(res);
    } catch (err: any) {
      if (err?.status === 404 || err?.statusCode === 404) {
        setIsNotFound(true);
      } else {
        const msg = err instanceof Error ? err.message : 'Failed to retrieve dimensional analytics.';
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDimension();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dim]);

  // 404 Dimension State
  if (isNotFound || (!loading && !isValidDim)) {
    return (
      <div className="gf-dim-detail">
        <div className="gf-dim-detail__breadcrumb">
          <Link to="/admin/analytics" className="gf-dim-detail__back-link">
            ← Back to Platform Analytics
          </Link>
        </div>
        <Card className="gf-dim-detail__404-card">
          <EmptyState
            title="Dimension Not Found"
            description={`The analytics dimension "${dimension}" is not recognized by the platform. Supported canonical dimensions: projects, users, documents, activity.`}
            action={
              <Link to="/admin/analytics">
                <Button variant="primary">Return to Platform Analytics</Button>
              </Link>
            }
          />
        </Card>
      </div>
    );
  }

  return (
    <div className="gf-dim-detail">
      <div className="gf-dim-detail__breadcrumb">
        <Link to="/admin/analytics" className="gf-dim-detail__back-link">
          ← Back to Platform Analytics
        </Link>
      </div>

      <PageHeader
        eyebrow="DIMENSIONAL TELEMETRY"
        title={data?.title || `${dim.toUpperCase()} Telemetry`}
        description={
          data?.description ||
          `Canonical telemetry and distribution metrics for the ${dim} domain.`
        }
        actions={
          <div className="gf-dim-detail__header-actions">
            {data?.generated_at && (
              <span className="gf-dim-detail__gen-time">
                Generated: {formatDateTime(data.generated_at)}
              </span>
            )}
            <Button variant="secondary" size="sm" onClick={fetchDimension}>
              Refresh
            </Button>
          </div>
        }
      />

      {error && (
        <div className="gf-dim-detail__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchDimension}>
            Retry
          </Button>
        </div>
      )}

      {loading && !data ? (
        <div className="gf-dim-detail__loading">
          <Skeleton height="100px" className="mb-4" />
          <Skeleton height="180px" className="mb-4" />
          <Skeleton height="260px" />
        </div>
      ) : data ? (
        <>
          {/* Overview Metric Banner */}
          <div className="gf-dim-detail__stat-grid">
            <StatTile
              label="Total Records"
              value={data.total_records}
              subtext={`Canonical records indexed in ${dim}`}
            />
            <StatTile
              label="Dimension Target"
              value={data.dimension.toUpperCase()}
              subtext="Authorized telemetric partition"
            />
          </div>

          {/* Render Dimension-Specific Sections */}
          <div className="gf-dim-detail__content-layout">
            {Object.entries(data.data || {}).map(([sectionKey, sectionVal]) => {
              if (
                typeof sectionVal === 'object' &&
                sectionVal !== null &&
                !Array.isArray(sectionVal)
              ) {
                // Check if values are all numbers (distribution block)
                const isDistribution = Object.values(sectionVal).every(
                  (v) => typeof v === 'number'
                );

                if (isDistribution && Object.keys(sectionVal).length > 0) {
                  return (
                    <DistributionSubBlock
                      key={sectionKey}
                      title={formatKey(sectionKey)}
                      data={sectionVal as Record<string, number>}
                    />
                  );
                }

                // Otherwise render as key-value metric card
                return (
                  <Card key={sectionKey} className="gf-dim-detail__sub-card">
                    <CardHeader className="gf-dim-detail__sub-header">
                      <CardTitle className="gf-dim-detail__sub-title">
                        {formatKey(sectionKey)}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="gf-dim-detail__sub-content">
                      <MetricTable data={sectionVal} />
                    </CardContent>
                  </Card>
                );
              }

              return null;
            })}
          </div>
        </>
      ) : null}
    </div>
  );
}
