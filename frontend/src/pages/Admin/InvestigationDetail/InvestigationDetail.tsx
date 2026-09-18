import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getAdminInvestigationDetail } from '@/lib/api/client';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import './InvestigationDetail.css';

/**
 * AD27 — Admin Investigation Detail
 *
 * Truthfully inspects designated canonical resources or reports that persistent
 * investigation tickets are not supported in the current database schema.
 */
export function InvestigationDetail() {
  const { investigationId } = useParams<{ investigationId: string }>();
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!investigationId) return;

    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const res = await getAdminInvestigationDetail(investigationId!);
        if (mounted) {
          setData(res);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Investigation record not found.';
          setError(msg);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [investigationId]);

  return (
    <div className="gf-inv-detail">
      <div className="gf-inv-detail__breadcrumb">
        <Link to="/admin/security/investigations" className="gf-inv-detail__back-link">
          ← Back to Governed Inspection
        </Link>
      </div>

      {loading ? (
        <div className="gf-inv-detail__skeleton">
          <Skeleton height="80px" />
          <Skeleton height="200px" />
        </div>
      ) : error || !data ? (
        <div className="gf-inv-detail__unsupported">
          <PageHeader
            eyebrow="INVESTIGATION ENTITY UNAVAILABLE"
            title="Canonical Investigation Limitation"
            description="AD27 requires persistent investigation identity that is not present in the current canonical schema."
          />
          <Card className="gf-inv-detail__notice-card">
            <CardHeader>
              <CardTitle>Architectural Assessment Notice</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="gf-inv-detail__notice-msg">
                Investigation record <code>{investigationId}</code> could not be resolved to an active entity.
                GrowFlow currently does not maintain a dedicated <code>investigation_requests</code> persistence table in PostgreSQL.
              </p>
              <p className="gf-inv-detail__notice-sub">
                To inspect platform activity, use the direct governance interfaces for Users, Project Instances, and the Canonical Audit Log.
              </p>
              <div className="gf-inv-detail__btn-row">
                <Button as="link" to="/admin/security/investigations" variant="primary">
                  Return to Governed Inspection
                </Button>
                <Button as="link" to="/admin/security/audit" variant="secondary">
                  View Platform Audit Log
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <>
          <PageHeader
            eyebrow="CANONICAL RESOURCE INSPECTION"
            title={data.label || 'Inspected Entity'}
            description={`Type: ${data.target_type} • ID: ${data.target_id}`}
            actions={
              <Badge variant="accent">{data.inspection_mode}</Badge>
            }
          />
          <Card className="gf-inv-detail__card">
            <CardHeader>
              <CardTitle>Canonical Record Attributes</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="gf-inv-detail__dl">
                {Object.entries(data).map(([k, v]) => (
                  <div key={k} className="gf-inv-detail__dl-row">
                    <dt className="gf-inv-detail__dt">{k.replace(/_/g, ' ')}</dt>
                    <dd className="gf-inv-detail__dd">{String(v ?? '—')}</dd>
                  </div>
                ))}
              </dl>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
