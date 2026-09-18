import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getAdminInvestigations } from '@/lib/api/client';
import type { AdminInvestigationOverviewResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './InvestigationRequests.css';

/**
 * AD26 — Admin Investigation Requests (Governed Inspection Entry Surface)
 *
 * Truthful administrative inspection entry point that identifies canonical
 * platform entities requiring review (e.g., suspended accounts, critical-health projects,
 * delivery errors) without inventing synthetic tickets.
 */
export function InvestigationRequests() {
  const [data, setData] = useState<AdminInvestigationOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInvestigations = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminInvestigations();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve investigation targets.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigations();
  }, []);

  const getReasonBadge = (reason: string) => {
    switch (reason) {
      case 'ACCOUNT_SUSPENDED':
        return <Badge variant="danger">Suspended User</Badge>;
      case 'CRITICAL_HEALTH':
        return <Badge variant="warning">Critical Project</Badge>;
      case 'DELIVERY_FAILURE':
        return <Badge variant="danger">Delivery Failure</Badge>;
      default:
        return <Badge variant="neutral">{reason}</Badge>;
    }
  };

  return (
    <div className="gf-inv-requests">
      <div className="gf-inv-requests__breadcrumb">
        <Link to="/admin/security" className="gf-inv-requests__back-link">
          ← Back to Security & Audit
        </Link>
      </div>

      <PageHeader
        eyebrow="GOVERNED AUDIT INSPECTION"
        title="Investigation & Governed Inspection"
        description="Controlled review surface for flagged platform resources requiring administrative oversight."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchInvestigations}>
            Refresh
          </Button>
        }
      />

      {error && (
        <div className="gf-inv-requests__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchInvestigations}>
            Retry
          </Button>
        </div>
      )}

      {/* Schema Notice Banner */}
      <div className="gf-inv-requests__notice">
        <div className="gf-inv-requests__notice-icon">ℹ</div>
        <div className="gf-inv-requests__notice-text">
          <strong>Governed Resource Inspection:</strong>
          {' '}This surface evaluates authoritative platform signals (suspended accounts, critical risks, and outbox failures) for controlled investigation. Persistent asynchronous ticket tracking is not configured in the current canonical schema.
        </div>
      </div>

      {loading ? (
        <Card className="gf-inv-requests__card">
          <div className="gf-inv-requests__skeleton-wrap">
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" />
          </div>
        </Card>
      ) : !data || data.flagged_resources.length === 0 ? (
        <EmptyState
          title="Zero flagged resources requiring inspection"
          description="All platform user accounts are active, project instance health is nominal, and transactional event delivery has no logged failures."
        />
      ) : (
        <Card className="gf-inv-requests__card">
          <CardHeader>
            <CardTitle>
              Candidate Resources for Review ({data.total_flagged})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-inv-requests__table-responsive">
              <table className="gf-inv-requests__table">
                <thead>
                  <tr>
                    <th>Candidate Target</th>
                    <th>Flag Reason</th>
                    <th>Governance Context</th>
                    <th>Detected</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {data.flagged_resources.map((item, idx) => (
                    <tr key={`${item.resource_id}-${idx}`}>
                      <td>
                        <span className="gf-inv-requests__label">{item.label}</span>
                        <span className="gf-inv-requests__res-id">
                          {item.resource_type}: {item.resource_id.slice(0, 10)}...
                        </span>
                      </td>
                      <td>{getReasonBadge(item.flag_reason)}</td>
                      <td>
                        <span className="gf-inv-requests__detail">{item.detail}</span>
                      </td>
                      <td>
                        <span className="gf-inv-requests__time">
                          {item.flagged_at ? new Date(item.flagged_at).toLocaleDateString() : '—'}
                        </span>
                      </td>
                      <td>
                        <Button
                          as="link"
                          to={item.canonical_inspection_url}
                          variant="secondary"
                          size="sm"
                        >
                          Inspect →
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
