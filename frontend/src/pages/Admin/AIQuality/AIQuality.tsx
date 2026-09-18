import { useEffect, useState } from 'react';
import { getAdminAIQuality } from '@/lib/api/client';
import type { AdminAIQualityResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AIQuality.css';

/**
 * AD15 — AI Quality
 *
 * Real QA Judge evaluation telemetry, scoring brackets, architectural criteria breakdown,
 * and top identified synthesis issues.
 */
export function AIQuality() {
  const [data, setData] = useState<AdminAIQualityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQuality = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAIQuality();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve AI Quality telemetry.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuality();
  }, []);

  const totalEvaluated = data?.total_evaluated ?? 0;
  const dist = data?.score_distribution;
  const criteria = data?.criteria_averages || {};
  const issues = data?.top_issues || [];

  const brackets = [
    { label: 'Exemplary (85–100)', count: dist?.range_85_100 ?? 0, color: '#10b981' },
    { label: 'Acceptable (70–84)', count: dist?.range_70_84 ?? 0, color: '#0284c7' },
    { label: 'Low / Degraded (50–69)', count: dist?.range_50_69 ?? 0, color: '#f59e0b' },
    { label: 'Critical / Fail (0–49)', count: dist?.range_0_49 ?? 0, color: '#ef4444' },
  ];

  return (
    <div className="gf-ai-quality">
      <PageHeader
        eyebrow="EVALUATION TELEMETRY"
        title="AI Quality & QA Judge"
        description="Authoritative architectural evaluation benchmarks, score distribution curves, and criteria metrics persisted by the QA Judge."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchQuality}>
            Refresh
          </Button>
        }
      />

      <AISubNav />

      {error && (
        <div className="gf-ai-quality__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchQuality}>
            Retry
          </Button>
        </div>
      )}

      {/* KPI Tiles */}
      <section className="gf-ai-quality__kpi-grid" aria-label="Quality KPIs">
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
              label="Evaluated Deliverables"
              value={totalEvaluated}
              subtext={`${data?.passed_count ?? 0} passed / ${data?.failed_count ?? 0} failed`}
            />
            <StatTile
              label="QA Pass Rate"
              value={data?.pass_rate_percent !== null && data?.pass_rate_percent !== undefined ? `${data.pass_rate_percent}%` : '—'}
              subtext="Percent meeting approval threshold"
            />
            <StatTile
              label="Average QA Score"
              value={data?.average_qa_score !== null && data?.average_qa_score !== undefined ? `${data.average_qa_score}/100` : '—'}
              subtext={data?.min_qa_score !== null ? `Min: ${data?.min_qa_score} | Max: ${data?.max_qa_score}` : 'Evaluated records'}
            />
            <StatTile
              label="Approval Conversion"
              value={data?.approval_conversion_rate !== null && data?.approval_conversion_rate !== undefined ? `${data.approval_conversion_rate}%` : '—'}
              subtext="Passed blueprints adopted"
            />
          </>
        )}
      </section>

      {/* 2-Column: Score Distribution + Architectural Criteria Breakdown */}
      <div className="gf-ai-quality__grid-2col">
        {/* Score Distribution Brackets */}
        <Card className="gf-ai-quality__card">
          <CardHeader>
            <CardTitle>QA Score Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="180px" />
            ) : totalEvaluated === 0 ? (
              <p className="gf-ai-quality__muted">No evaluated blueprint records recorded.</p>
            ) : (
              <div className="gf-ai-quality__bracket-list">
                {brackets.map((brk) => {
                  const pct = totalEvaluated > 0 ? Math.round((brk.count / totalEvaluated) * 100) : 0;
                  return (
                    <div key={brk.label} className="gf-ai-quality__bracket-item">
                      <div className="gf-ai-quality__bracket-meta">
                        <span className="gf-ai-quality__bracket-label">{brk.label}</span>
                        <span className="gf-ai-quality__bracket-val">
                          {brk.count} ({pct}%)
                        </span>
                      </div>
                      <div className="gf-ai-quality__bracket-track">
                        <div
                          className="gf-ai-quality__bracket-fill"
                          style={{ width: `${pct}%`, backgroundColor: brk.color }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Criteria Averages */}
        <Card className="gf-ai-quality__card">
          <CardHeader>
            <CardTitle>Criteria Evaluation Averages</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="180px" />
            ) : Object.keys(criteria).length === 0 ? (
              <p className="gf-ai-quality__muted">No criteria breakdowns available in evaluated records.</p>
            ) : (
              <div className="gf-ai-quality__criteria-list">
                {Object.entries(criteria).map(([criterion, score]) => (
                  <div key={criterion} className="gf-ai-quality__criterion-row">
                    <span className="gf-ai-quality__crit-label">
                      {criterion.replace(/_/g, ' ')}
                    </span>
                    <div className="gf-ai-quality__crit-meter">
                      <div
                        className="gf-ai-quality__crit-fill"
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <span className="gf-ai-quality__crit-val">{score}/100</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top QA Issues Identified */}
      <section className="gf-ai-quality__section" aria-label="Aggregated Issues">
        <Card>
          <CardHeader>
            <CardTitle>Aggregated Architectural Issues & Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton height="180px" />
            ) : issues.length === 0 ? (
              <EmptyState
                title="No Critical Issues Identified"
                description="QA Judge evaluations have not logged unresolved architectural issues."
              />
            ) : (
              <div className="gf-ai-quality__issues-table-wrap">
                <table className="gf-ai-quality__table">
                  <thead>
                    <tr>
                      <th>Section</th>
                      <th>Severity</th>
                      <th>Occurrences</th>
                      <th>Sample Feedback</th>
                      <th>Recommendation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {issues.map((iss, idx) => (
                      <tr key={idx}>
                        <td className="gf-ai-quality__sec-cell">{iss.section}</td>
                        <td>
                          <Badge variant={iss.severity === 'HIGH' ? 'danger' : 'warning'}>
                            {iss.severity}
                          </Badge>
                        </td>
                        <td>
                          <strong>{iss.count}</strong>
                        </td>
                        <td className="gf-ai-quality__desc-cell">{iss.sample_description}</td>
                        <td className="gf-ai-quality__rec-cell">{iss.recommendation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Deferred Capabilities Posture */}
      <section className="gf-ai-quality__notices" aria-label="Deferred Capability Disclosures">
        <Card>
          <CardHeader>
            <CardTitle className="gf-ai-quality__notice-head">
              Quality Subsystem Posture & Deferred Benchmarks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-ai-quality__notice-grid">
              <div className="gf-ai-quality__notice-item">
                <span className="gf-ai-quality__pill gf-ai-quality__pill--deferred">DEFERRED</span>
                <span className="gf-ai-quality__notice-title">Continuous RAG Faithfulness</span>
                <p className="gf-ai-quality__notice-desc">
                  Automated continuous embedding faithfulness scoring is scheduled for future evaluation pipelines.
                </p>
              </div>
              <div className="gf-ai-quality__notice-item">
                <span className="gf-ai-quality__pill gf-ai-quality__pill--unavailable">UNAVAILABLE</span>
                <span className="gf-ai-quality__notice-title">Automated Hallucination Benchmarks</span>
                <p className="gf-ai-quality__notice-desc">
                  Synthetic test suite hallucination probing is not currently run against student deliverables.
                </p>
              </div>
              <div className="gf-ai-quality__notice-item">
                <span className="gf-ai-quality__pill gf-ai-quality__pill--unavailable">UNAVAILABLE</span>
                <span className="gf-ai-quality__notice-title">Student CSAT / AI Feedback</span>
                <p className="gf-ai-quality__notice-desc">
                  Direct student CSAT star ratings on AI outputs are not captured in the current database schema.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
