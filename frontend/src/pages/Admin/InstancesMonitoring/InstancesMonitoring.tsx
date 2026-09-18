import { useEffect, useState, useTransition } from 'react';
import { Link } from 'react-router';
import { getAdminInstancesMonitoring } from '@/lib/api/client';
import type {
  AdminInstanceMonitoringResponse,
  AdminProjectSummary,
} from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './InstancesMonitoring.css';

/**
 * AD10 — Project Instance Monitoring
 *
 * Operational governance monitoring of all student project instances across
 * the platform with live health distribution KPIs and lifecycle filters.
 * Clicking any instance navigates to the canonical detail route /admin/instances/:projectId.
 */
export function InstancesMonitoring() {
  const [data, setData] = useState<AdminInstanceMonitoringResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [phaseFilter, setPhaseFilter] = useState('ALL');
  const [healthFilter, setHealthFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [, startTransition] = useTransition();

  const fetchMonitoring = async (s: string, ph: string, hl: string, st: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminInstancesMonitoring({
        search: s.trim() || undefined,
        phase: ph !== 'ALL' ? ph : undefined,
        health: hl !== 'ALL' ? hl : undefined,
        status: st !== 'ALL' ? st : undefined,
      });
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve instance monitoring metrics.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonitoring(search, phaseFilter, healthFilter, statusFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phaseFilter, healthFilter, statusFilter]);

  const handleSearchChange = (val: string) => {
    setSearch(val);
    startTransition(() => {
      fetchMonitoring(val, phaseFilter, healthFilter, statusFilter);
    });
  };

  const getHealthBadge = (health?: string | null) => {
    switch (health?.toUpperCase()) {
      case 'HEALTHY':
        return <Badge variant="success">Healthy</Badge>;
      case 'WARNING':
      case 'NEEDS_ATTENTION':
        return <Badge variant="warning">Warning</Badge>;
      case 'CRITICAL':
      case 'AT_RISK':
        return <Badge variant="danger">Critical</Badge>;
      default:
        return <Badge variant="neutral">{health ?? 'UNKNOWN'}</Badge>;
    }
  };

  return (
    <div className="gf-inst-monitoring">
      <PageHeader
        eyebrow="OPERATIONAL GOVERNANCE"
        title="Project Instance Monitoring"
        description="Supervise execution health, lifecycle stages, and risk distributions across all student projects."
      />

      {error && (
        <div className="gf-inst-monitoring__alert" role="alert">
          <span>{error}</span>
          <Button
            variant="tertiary"
            size="sm"
            onClick={() => fetchMonitoring(search, phaseFilter, healthFilter, statusFilter)}
          >
            Retry
          </Button>
        </div>
      )}

      {/* KPI Summary Cards */}
      <div className="gf-inst-monitoring__kpi-grid">
        <Card className="gf-inst-monitoring__kpi-card">
          <CardHeader>
            <CardTitle>Total Instances</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="gf-inst-monitoring__kpi-val">
              {loading ? <Skeleton width="48px" height="32px" /> : data?.summary?.total_instances ?? 0}
            </span>
            <span className="gf-inst-monitoring__kpi-desc">Across all platform cohorts</span>
          </CardContent>
        </Card>

        <Card className="gf-inst-monitoring__kpi-card">
          <CardHeader>
            <CardTitle>Healthy State</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="gf-inst-monitoring__kpi-val gf-inst-monitoring__kpi-val--healthy">
              {loading ? <Skeleton width="48px" height="32px" /> : data?.summary?.healthy_count ?? 0}
            </span>
            <span className="gf-inst-monitoring__kpi-desc">Progressing smoothly</span>
          </CardContent>
        </Card>

        <Card className="gf-inst-monitoring__kpi-card">
          <CardHeader>
            <CardTitle>Warning Attention</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="gf-inst-monitoring__kpi-val gf-inst-monitoring__kpi-val--warning">
              {loading ? <Skeleton width="48px" height="32px" /> : data?.summary?.warning_count ?? 0}
            </span>
            <span className="gf-inst-monitoring__kpi-desc">Deadlines/milestones slipping</span>
          </CardContent>
        </Card>

        <Card className="gf-inst-monitoring__kpi-card">
          <CardHeader>
            <CardTitle>Critical Risk</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="gf-inst-monitoring__kpi-val gf-inst-monitoring__kpi-val--critical">
              {loading ? <Skeleton width="48px" height="32px" /> : data?.summary?.critical_count ?? 0}
            </span>
            <span className="gf-inst-monitoring__kpi-desc">Intervention recommended</span>
          </CardContent>
        </Card>

        <Card className="gf-inst-monitoring__kpi-card">
          <CardHeader>
            <CardTitle>Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="gf-inst-monitoring__kpi-val gf-inst-monitoring__kpi-val--completed">
              {loading ? <Skeleton width="48px" height="32px" /> : data?.summary?.completed_count ?? 0}
            </span>
            <span className="gf-inst-monitoring__kpi-desc">Successfully concluded</span>
          </CardContent>
        </Card>
      </div>

      {/* Toolbar & Filters */}
      <div className="gf-inst-monitoring__toolbar">
        <div className="gf-inst-monitoring__search-wrapper">
          <svg className="gf-inst-monitoring__search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="9" cy="9" r="6" />
            <line x1="13.5" y1="13.5" x2="18" y2="18" />
          </svg>
          <input
            type="search"
            placeholder="Search by project, student, mentor, or cohort..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="gf-inst-monitoring__search-input"
            aria-label="Search instances"
          />
        </div>

        <div className="gf-inst-monitoring__filters">
          <select
            value={phaseFilter}
            onChange={(e) => setPhaseFilter(e.target.value)}
            className="gf-inst-monitoring__select"
            aria-label="Filter by phase"
          >
            <option value="ALL">All Phases</option>
            <option value="IDEA">Idea</option>
            <option value="ASSESSMENT">Assessment</option>
            <option value="DRAFTING">Drafting</option>
            <option value="ARCHITECTURE">Architecture</option>
            <option value="IMPLEMENTATION">Implementation</option>
            <option value="TESTING">Testing</option>
            <option value="DEPLOYMENT">Deployment</option>
            <option value="EVALUATION">Evaluation</option>
            <option value="COMPLETION">Completion</option>
          </select>

          <select
            value={healthFilter}
            onChange={(e) => setHealthFilter(e.target.value)}
            className="gf-inst-monitoring__select"
            aria-label="Filter by health"
          >
            <option value="ALL">All Health</option>
            <option value="HEALTHY">Healthy</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="gf-inst-monitoring__select"
            aria-label="Filter by status"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="COMPLETED">Completed</option>
            <option value="PAUSED">Paused</option>
          </select>
        </div>
      </div>

      {/* Instances Table */}
      {loading ? (
        <Card className="gf-inst-monitoring__card">
          <div className="gf-inst-monitoring__skeleton-wrap">
            <Skeleton height="40px" className="gf-mb-3" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" className="gf-mb-2" />
            <Skeleton height="56px" />
          </div>
        </Card>
      ) : !data || data.instances.length === 0 ? (
        <EmptyState
          title="No instances matching criteria"
          description={
            search || phaseFilter !== 'ALL' || healthFilter !== 'ALL' || statusFilter !== 'ALL'
              ? 'No project instances meet your current search or filter filters.'
              : 'There are currently no student project instances to monitor.'
          }
        />
      ) : (
        <Card className="gf-inst-monitoring__card">
          <div className="gf-inst-monitoring__table-responsive">
            <table className="gf-inst-monitoring__table">
              <thead>
                <tr>
                  <th scope="col">Instance Name</th>
                  <th scope="col">Student</th>
                  <th scope="col">Cohort</th>
                  <th scope="col">Supervisor</th>
                  <th scope="col">Phase</th>
                  <th scope="col">Health</th>
                  <th scope="col">Progress</th>
                  <th scope="col">Status</th>
                  <th scope="col"><span className="gf-sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody>
                {data.instances.map((inst: AdminProjectSummary) => (
                  <tr key={inst.id}>
                    <td>
                      <div className="gf-inst-monitoring__title-cell">
                        <Link
                          to={`/admin/instances/${inst.id}`}
                          className="gf-inst-monitoring__title-link"
                        >
                          {inst.name}
                        </Link>
                      </div>
                    </td>
                    <td>
                      <Link
                        to={`/admin/students/${inst.student_id}`}
                        className="gf-inst-monitoring__sub-link"
                      >
                        {inst.student_name}
                      </Link>
                    </td>
                    <td>
                      {inst.group_id ? (
                        <Link
                          to={`/admin/groups/${inst.group_id}`}
                          className="gf-inst-monitoring__sub-link"
                        >
                          {inst.group_name || 'Cohort'}
                        </Link>
                      ) : (
                        <span className="gf-inst-monitoring__muted">Independent</span>
                      )}
                    </td>
                    <td>
                      {inst.mentor_name ? (
                        <span className="gf-inst-monitoring__mentor-name">{inst.mentor_name}</span>
                      ) : (
                        <span className="gf-inst-monitoring__muted">Unassigned</span>
                      )}
                    </td>
                    <td>
                      <span className="gf-inst-monitoring__phase-pill">
                        {inst.current_phase.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>{getHealthBadge(inst.health)}</td>
                    <td>
                      <div className="gf-inst-monitoring__progress-wrap">
                        <div
                          className="gf-inst-monitoring__progress-bar"
                          style={{ width: `${Math.min(100, Math.max(0, inst.progress_percentage))}%` }}
                        />
                        <span className="gf-inst-monitoring__progress-val">{inst.progress_percentage}%</span>
                      </div>
                    </td>
                    <td>
                      <Badge variant={inst.status === 'ACTIVE' ? 'success' : 'neutral'}>
                        {inst.status}
                      </Badge>
                    </td>
                    <td className="gf-inst-monitoring__actions">
                      <Button
                        as="link"
                        to={`/admin/instances/${inst.id}`}
                        variant="secondary"
                        size="sm"
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
