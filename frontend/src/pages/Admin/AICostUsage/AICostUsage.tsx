import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminAICost } from '@/lib/api/client';
import type { AdminAICostResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AICostUsage.css';

/**
 * AD16 — Cost & Capacity Accounting
 *
 * Truthful execution volume and upstream provider capacity governance.
 * No dollar charges or simulated billing ledgers are calculated.
 */
export function AICostUsage() {
  const [data, setData] = useState<AdminAICostResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCost = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAICost();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve AI cost & capacity data.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCost();
  }, []);

  const dimensions = [
    {
      key: 'agent',
      title: 'Execution Volume by Capability / Agent',
      desc: 'Distribution of transactional volume across blueprint generation, targeted repairs, mentor chats, and change analyses.',
      to: '/admin/ai/cost/agent',
    },
    {
      key: 'project',
      title: 'Execution Volume by Project',
      desc: 'Allocation of AI transactions across active project instances.',
      to: '/admin/ai/cost/project',
    },
    {
      key: 'time',
      title: 'Execution Volume over Time',
      desc: 'Time-series volume aggregation over the past 14 days.',
      to: '/admin/ai/cost/time',
    },
    {
      key: 'status',
      title: 'Execution Volume by Status',
      desc: 'Execution volume grouped by outcome status (completed, failed, running, pending).',
      to: '/admin/ai/cost/status',
    },
  ];

  return (
    <div className="gf-ai-cost">
      <PageHeader
        eyebrow="CAPACITY & BILLING GOVERNANCE"
        title="AI Capacity & Upstream Billing"
        description="Authoritative platform transaction volume and upstream provider billing model disclosures."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchCost}>
            Refresh
          </Button>
        }
      />

      <AISubNav />

      {error && (
        <div className="gf-ai-cost__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchCost}>
            Retry
          </Button>
        </div>
      )}

      {/* Upstream Billing Posture Banner */}
      <section className="gf-ai-cost__billing-banner" aria-label="Upstream Billing Model">
        <div className="gf-ai-cost__billing-header">
          <div className="gf-ai-cost__pill-group">
            <span className="gf-ai-cost__pill gf-ai-cost__pill--primary">
              BILLING MODEL: {data?.billing_model || 'DIRECT_PROVIDER_BILLED — OPENROUTER'}
            </span>
            <span className="gf-ai-cost__pill gf-ai-cost__pill--neutral">
              COST TELEMETRY: {data?.cost_telemetry_state || 'UNMETERED / NOT PERSISTED'}
            </span>
            <span className="gf-ai-cost__pill gf-ai-cost__pill--neutral">
              TOKEN LEDGER: {data?.token_metering_state || 'UNMETERED / NOT PERSISTED'}
            </span>
          </div>
        </div>
        <p className="gf-ai-cost__disclaimer">
          {data?.disclaimer ||
            'OpenRouter billing is managed upstream via external provider accounts. Per-token accounting tables and dollar pricing schedules are not configured in the current database schema.'}
        </p>
      </section>

      {/* Execution Capacity Tiles */}
      <section className="gf-ai-cost__kpi-grid" aria-label="Capacity Volume Metrics">
        {loading ? (
          <>
            <Skeleton height="110px" />
            <Skeleton height="110px" />
            <Skeleton height="110px" />
            <Skeleton height="110px" />
          </>
        ) : (
          <>
            <StatTile
              label="Total Executions Logged"
              value={data?.execution_volume_total ?? 0}
              subtext="Across all platform AI systems"
            />
            <StatTile
              label="Synthesis Runs"
              value={data?.blueprint_jobs_count ?? 0}
              subtext="Full generation & targeted repairs"
            />
            <StatTile
              label="AI Mentor Assistant Messages"
              value={data?.ai_mentor_messages_count ?? 0}
              subtext="Logged student assistance interactions"
            />
            <StatTile
              label="Change Impact Analyses"
              value={data?.change_analyses_count ?? 0}
              subtext="Proposal evaluations logged"
            />
          </>
        )}
      </section>

      {/* Configured Active Models */}
      <section className="gf-ai-cost__section" aria-label="Configured AI Models">
        <Card>
          <CardHeader>
            <CardTitle>Configured Active Models</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="80px" />
            ) : !data?.active_models || data.active_models.length === 0 ? (
              <p className="gf-ai-cost__muted">No models configured in active settings.</p>
            ) : (
              <div className="gf-ai-cost__models-grid">
                {data.active_models.map((model) => (
                  <div key={model} className="gf-ai-cost__model-box">
                    <span className="gf-ai-cost__model-name">{model}</span>
                    <Badge variant="neutral">OpenRouter Upstream</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Dimensional Breakdown Exploration */}
      <section className="gf-ai-cost__section" aria-label="Breakdown Dimensions">
        <div className="gf-ai-cost__section-head">
          <h2 className="gf-ai-cost__section-title">Execution Volume Dimensions</h2>
          <span className="gf-ai-cost__subtext">
            Volume accounting drilldowns across canonical entities
          </span>
        </div>

        <div className="gf-ai-cost__dim-grid">
          {dimensions.map((dim) => (
            <Card key={dim.key} className="gf-ai-cost__dim-card">
              <CardHeader>
                <CardTitle className="gf-ai-cost__dim-title">{dim.title}</CardTitle>
              </CardHeader>
              <CardContent className="gf-ai-cost__dim-content">
                <p className="gf-ai-cost__dim-desc">{dim.desc}</p>
                <Link to={dim.to} className="gf-ai-cost__dim-link">
                  <Button variant="secondary" size="sm">
                    View Breakdown →
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
