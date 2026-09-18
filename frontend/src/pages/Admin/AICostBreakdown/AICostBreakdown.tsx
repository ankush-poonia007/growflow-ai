import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminAICostDimension } from '@/lib/api/client';
import type { AdminAICostDimensionResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AICostBreakdown.css';

/**
 * AD17 — Cost Breakdown (Execution Volume by Dimension)
 *
 * Dimension-specific drilldown across capabilities, projects, time buckets, and execution statuses.
 * Discloses usage-volume semantics rather than fabricated dollar charges.
 */
export function AICostBreakdown() {
  const { dimension } = useParams<{ dimension: string }>();
  const [data, setData] = useState<AdminAICostDimensionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBreakdown = async () => {
    if (!dimension) return;
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAICostDimension(dimension);
      setData(res);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Failed to retrieve dimensional volume breakdown.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBreakdown();
  }, [dimension]);

  const items = data?.items || [];
  const totalVolume = data?.total_volume || 0;

  return (
    <div className="gf-ai-cost-dim">
      <div className="gf-ai-cost-dim__nav-bar">
        <Link to="/admin/ai/cost" className="gf-ai-cost-dim__back-link">
          ← Back to Cost & Capacity Accounting
        </Link>
      </div>

      <PageHeader
        eyebrow="CAPACITY DIMENSION DRILLDOWN"
        title={data?.title || `Execution Volume by ${dimension || 'Dimension'}`}
        description="Authoritative transaction volume aggregation grouped by canonical dimension attributes."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchBreakdown}>
            Refresh
          </Button>
        }
      />

      <AISubNav />

      {error ? (
        <div className="gf-ai-cost-dim__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchBreakdown}>
            Retry
          </Button>
        </div>
      ) : loading ? (
        <div className="gf-ai-cost-dim__loading">
          <Skeleton height="100px" />
          <Skeleton height="320px" />
        </div>
      ) : !data ? (
        <EmptyState
          title="Dimension Not Found"
          description="The requested breakdown dimension is not supported. Supported dimensions are agent, project, time, and status."
        />
      ) : (
        <>
          {/* Truthful Cost Notice Banner */}
          <section className="gf-ai-cost-dim__notice-banner" aria-label="Usage Volume Semantics">
            <div className="gf-ai-cost-dim__notice-meta">
              <span className="gf-ai-cost-dim__metric-tag">
                METRIC: {data.metric_type} (NOT DOLLAR COST)
              </span>
              <span className="gf-ai-cost-dim__total-tag">
                Total Dimension Volume: <strong>{totalVolume}</strong>
              </span>
            </div>
            <p className="gf-ai-cost-dim__notice-text">{data.cost_notice}</p>
          </section>

          {/* Breakdown Items List */}
          <section className="gf-ai-cost-dim__section" aria-label="Dimension Records">
            <Card>
              <CardHeader>
                <CardTitle>Distribution Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                {items.length === 0 ? (
                  <p className="gf-ai-cost-dim__muted">
                    No transactions recorded for this dimension.
                  </p>
                ) : (
                  <div className="gf-ai-cost-dim__items-list">
                    {items.map((item) => (
                      <div key={item.key} className="gf-ai-cost-dim__item">
                        <div className="gf-ai-cost-dim__item-header">
                          <div className="gf-ai-cost-dim__item-titles">
                            <span className="gf-ai-cost-dim__item-label">{item.label}</span>
                            {item.detail && (
                              <span className="gf-ai-cost-dim__item-detail">({item.detail})</span>
                            )}
                          </div>
                          <div className="gf-ai-cost-dim__item-stats">
                            <span className="gf-ai-cost-dim__count">{item.execution_count} runs</span>
                            <span className="gf-ai-cost-dim__pct">{item.percentage}%</span>
                          </div>
                        </div>
                        <div className="gf-ai-cost-dim__track">
                          <div
                            className="gf-ai-cost-dim__fill"
                            style={{ width: `${item.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </section>
        </>
      )}
    </div>
  );
}
