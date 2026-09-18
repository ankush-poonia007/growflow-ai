import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminAITraceDetail } from '@/lib/api/client';
import type { AdminAITraceDetailResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AITraceDetail.css';

function formatDate(iso?: string | null): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return iso;
  }
}

/**
 * AD14 — AI Trace Detail
 *
 * Truthful partial execution trace displaying pipeline stage milestones,
 * correlated QA Judge evaluations, outbox domain events, and sanitized diagnostics.
 */
export function AITraceDetail() {
  const { executionId } = useParams<{ executionId: string }>();
  const [data, setData] = useState<AdminAITraceDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrace = async () => {
    if (!executionId) return;
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAITraceDetail(executionId);
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Execution trace not found.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrace();
  }, [executionId]);

  const stages = data?.pipeline_stages || [];
  const qa = data?.qa_result;
  const events = data?.domain_events || [];

  return (
    <div className="gf-ai-trace">
      <div className="gf-ai-trace__nav-bar">
        <Link to="/admin/ai/executions" className="gf-ai-trace__back-link">
          ← Back to Agent Executions
        </Link>
      </div>

      <PageHeader
        eyebrow="EXECUTION TRACE OBSERVABILITY"
        title={`Trace: ${executionId ? executionId.slice(0, 13) + '…' : 'Detail'}`}
        description="Correlated pipeline stages, QA Judge evaluation, and domain event lifecycle for blueprint synthesis runs."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchTrace}>
            Refresh Trace
          </Button>
        }
      />

      <AISubNav />

      {error ? (
        <div className="gf-ai-trace__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchTrace}>
            Retry
          </Button>
        </div>
      ) : loading ? (
        <div className="gf-ai-trace__loading">
          <Skeleton height="180px" />
          <Skeleton height="240px" />
          <Skeleton height="200px" />
        </div>
      ) : !data ? (
        <EmptyState
          title="Trace Not Found"
          description="The requested execution ID could not be resolved against canonical blueprint jobs."
        />
      ) : (
        <>
          {/* Execution Identity & Context */}
          <section className="gf-ai-trace__section" aria-label="Execution Context">
            <Card>
              <CardHeader className="gf-ai-trace__header">
                <div>
                  <CardTitle className="gf-ai-trace__title">Execution Overview</CardTitle>
                  <p className="gf-ai-trace__subtitle">Job: {data.id}</p>
                </div>
                <Badge
                  variant={
                    data.status === 'COMPLETED'
                      ? 'success'
                      : data.status === 'FAILED'
                      ? 'danger'
                      : data.status === 'RUNNING'
                      ? 'warning'
                      : 'neutral'
                  }
                >
                  {data.status}
                </Badge>
              </CardHeader>
              <CardContent>
                <div className="gf-ai-trace__grid">
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Project</span>
                    <span className="gf-ai-trace__prop-value">{data.project_name}</span>
                  </div>
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Job Type</span>
                    <span className="gf-ai-trace__prop-value">{data.job_type}</span>
                  </div>
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Current / Final Step</span>
                    <span className="gf-ai-trace__prop-value gf-ai-trace__mono">
                      {data.current_step || '—'}
                    </span>
                  </div>
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Duration</span>
                    <span className="gf-ai-trace__prop-value">
                      {data.duration_seconds !== null ? `${data.duration_seconds} seconds` : '—'}
                    </span>
                  </div>
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Progress</span>
                    <span className="gf-ai-trace__prop-value">{data.progress_percent}%</span>
                  </div>
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Target Section</span>
                    <span className="gf-ai-trace__prop-value gf-ai-trace__mono">
                      {data.target_output || 'FULL_BLUEPRINT'}
                    </span>
                  </div>
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Created At</span>
                    <span className="gf-ai-trace__prop-value">{formatDate(data.created_at)}</span>
                  </div>
                  <div className="gf-ai-trace__prop-item">
                    <span className="gf-ai-trace__prop-label">Completed At</span>
                    <span className="gf-ai-trace__prop-value">{formatDate(data.completed_at)}</span>
                  </div>
                </div>

                {data.sanitized_error && (
                  <div className="gf-ai-trace__error-box">
                    <span className="gf-ai-trace__error-title">Sanitized Failure Diagnostic:</span>
                    <p className="gf-ai-trace__error-text">{data.sanitized_error}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Canonical Pipeline Stages */}
          <section className="gf-ai-trace__section" aria-label="Pipeline Stages">
            <Card>
              <CardHeader>
                <CardTitle>Canonical Synthesis Pipeline Stages</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="gf-ai-trace__stages-list">
                  {stages.map((stg) => (
                    <div
                      key={stg.section_key}
                      className={`gf-ai-trace__stage-row gf-ai-trace__stage-row--${stg.status.toLowerCase()}`}
                    >
                      <div className="gf-ai-trace__stage-num">{stg.stage_order}</div>
                      <div className="gf-ai-trace__stage-info">
                        <div className="gf-ai-trace__stage-head">
                          <span className="gf-ai-trace__stage-title">{stg.title}</span>
                          <span className="gf-ai-trace__mono gf-ai-trace__stage-key">
                            [{stg.section_key}]
                          </span>
                        </div>
                        <span className="gf-ai-trace__stage-milestone">
                          Milestone: {stg.progress_milestone}%
                        </span>
                      </div>
                      <Badge
                        variant={
                          stg.status === 'COMPLETED'
                            ? 'success'
                            : stg.status === 'FAILED'
                            ? 'danger'
                            : 'neutral'
                        }
                      >
                        {stg.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </section>

          {/* QA Judge Evaluation Result */}
          <section className="gf-ai-trace__section" aria-label="QA Judge Evaluation">
            <Card>
              <CardHeader className="gf-ai-trace__header">
                <div>
                  <CardTitle>Correlated QA Judge Evaluation</CardTitle>
                  <p className="gf-ai-trace__subtitle">
                    Automated architecture review and criteria scoring on generated blueprint.
                  </p>
                </div>
                {qa ? (
                  <Badge variant={qa.qa_status === 'PASS' ? 'success' : 'danger'}>
                    {qa.qa_status}
                  </Badge>
                ) : (
                  <Badge variant="neutral">NOT EVALUATED</Badge>
                )}
              </CardHeader>
              <CardContent>
                {!qa ? (
                  <p className="gf-ai-trace__muted">
                    No QA Judge evaluation record is correlated with this execution.
                  </p>
                ) : (
                  <div className="gf-ai-trace__qa-container">
                    <div className="gf-ai-trace__qa-score-row">
                      <div className="gf-ai-trace__qa-score-card">
                        <span className="gf-ai-trace__qa-score-label">Overall Score</span>
                        <span className="gf-ai-trace__qa-score-num">
                          {qa.qa_score !== null && qa.qa_score !== undefined
                            ? `${qa.qa_score}/100`
                            : '—'}
                        </span>
                      </div>
                      <div className="gf-ai-trace__qa-summary">
                        <strong>Evaluator Narrative:</strong>
                        <p className="gf-ai-trace__qa-summary-text">
                          {qa.summary || 'Evaluation completed with canonical feedback.'}
                        </p>
                      </div>
                    </div>

                    {/* Criteria Breakdown */}
                    {Object.keys(qa.evaluated_criteria || {}).length > 0 && (
                      <div className="gf-ai-trace__criteria-block">
                        <span className="gf-ai-trace__block-title">Criteria Evaluation</span>
                        <div className="gf-ai-trace__criteria-grid">
                          {Object.entries(qa.evaluated_criteria).map(([criterion, val]) => (
                            <div key={criterion} className="gf-ai-trace__criterion-item">
                              <span className="gf-ai-trace__criterion-key">
                                {criterion.replace(/_/g, ' ')}
                              </span>
                              <span className="gf-ai-trace__criterion-val">
                                {typeof val === 'number'
                                  ? `${val}/100`
                                  : typeof val === 'object' && val !== null
                                  ? JSON.stringify(val)
                                  : String(val)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Issues */}
                    {qa.issues && qa.issues.length > 0 && (
                      <div className="gf-ai-trace__issues-block">
                        <span className="gf-ai-trace__block-title">Identified Issues</span>
                        <div className="gf-ai-trace__issues-list">
                          {qa.issues.map((iss, idx) => (
                            <div key={idx} className="gf-ai-trace__issue-item">
                              <div className="gf-ai-trace__issue-head">
                                <span className="gf-ai-trace__issue-sec">
                                  Section: {iss.section || 'General'}
                                </span>
                                <Badge variant={iss.severity === 'HIGH' ? 'danger' : 'warning'}>
                                  {iss.severity || 'ISSUE'}
                                </Badge>
                              </div>
                              <p className="gf-ai-trace__issue-desc">
                                {iss.description || iss.feedback || JSON.stringify(iss)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {qa.recommendations && qa.recommendations.length > 0 && (
                      <div className="gf-ai-trace__recs-block">
                        <span className="gf-ai-trace__block-title">Recommendations</span>
                        <ul className="gf-ai-trace__recs-list">
                          {qa.recommendations.map((rec, idx) => (
                            <li key={idx} className="gf-ai-trace__rec-item">
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Correlated Domain Events */}
          <section className="gf-ai-trace__section" aria-label="Domain Events">
            <Card>
              <CardHeader>
                <CardTitle>Correlated Domain Outbox Events</CardTitle>
              </CardHeader>
              <CardContent>
                {events.length === 0 ? (
                  <p className="gf-ai-trace__muted">No domain outbox events linked to this execution.</p>
                ) : (
                  <div className="gf-ai-trace__table-wrapper">
                    <table className="gf-ai-trace__table">
                      <thead>
                        <tr>
                          <th>Event Type</th>
                          <th>Status</th>
                          <th>Correlation ID</th>
                          <th>Occurred At</th>
                        </tr>
                      </thead>
                      <tbody>
                        {events.map((ev) => (
                          <tr key={ev.id}>
                            <td className="gf-ai-trace__mono">{ev.event_type}</td>
                            <td>
                              <Badge
                                variant={
                                  ev.status === 'PUBLISHED'
                                    ? 'success'
                                    : ev.status === 'FAILED'
                                    ? 'danger'
                                    : 'neutral'
                                }
                              >
                                {ev.status}
                              </Badge>
                            </td>
                            <td className="gf-ai-trace__mono">
                              {ev.correlation_id ? ev.correlation_id.slice(0, 10) + '…' : '—'}
                            </td>
                            <td>{formatDate(ev.occurred_at)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Telemetry Disclaimers */}
          <section className="gf-ai-trace__notices" aria-label="Unavailable Telemetry Disclosures">
            <Card>
              <CardHeader>
                <CardTitle className="gf-ai-trace__notice-head">
                  Telemetry Boundaries & Security Posture
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="gf-ai-trace__notice-grid">
                  <div className="gf-ai-trace__notice-item">
                    <span className="gf-ai-trace__notice-tag">UNAVAILABLE</span>
                    <span className="gf-ai-trace__notice-title">Low-Level Wire Telemetry</span>
                    <p className="gf-ai-trace__notice-desc">
                      OpenRouter HTTP packet traces, DNS/TLS timings, and TTFT are unmetered at the application layer.
                    </p>
                  </div>
                  <div className="gf-ai-trace__notice-item">
                    <span className="gf-ai-trace__notice-tag">UNAVAILABLE</span>
                    <span className="gf-ai-trace__notice-title">LangGraph Checkpoints</span>
                    <p className="gf-ai-trace__notice-desc">
                      Internal LangGraph graph state snapshots are ephemeral and not persisted into relational storage.
                    </p>
                  </div>
                  <div className="gf-ai-trace__notice-item">
                    <span className="gf-ai-trace__notice-tag">REDACTED / SECURED</span>
                    <span className="gf-ai-trace__notice-title">Credential & Prompt Protection</span>
                    <p className="gf-ai-trace__notice-desc">
                      API authorization headers, environment secrets, internal server paths, and system prompts are never exposed.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
        </>
      )}
    </div>
  );
}
