import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectInstance, getMentorInstanceRisks } from '@/lib/api/client';
import type { MentorProjectInstanceDetail, RiskResponse, RiskSeverity, RiskStatus } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceRisks.css';

export const MentorInstanceRisks: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [risks, setRisks] = useState<RiskResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const [projRes, risksRes] = await Promise.all([
          getMentorProjectInstance(projectId),
          getMentorInstanceRisks(projectId),
        ]);
        if (mounted) {
          setProject(projRes);
          setRisks(risksRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          setError(
            err instanceof Error ? err.message : 'Failed to retrieve project risks or access denied.'
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadData();
    return () => {
      mounted = false;
    };
  }, [projectId]);

  const filteredRisks = useMemo(() => {
    return risks.filter((r) => {
      if (severityFilter !== 'ALL' && r.severity !== severityFilter) return false;
      if (statusFilter !== 'ALL' && r.status !== statusFilter) return false;
      if (search.trim()) {
        const query = search.toLowerCase();
        const matchesCode = r.risk_code.toLowerCase().includes(query);
        const matchesTitle = r.title.toLowerCase().includes(query);
        const matchesDesc = (r.description || '').toLowerCase().includes(query);
        if (!matchesCode && !matchesTitle && !matchesDesc) return false;
      }
      return true;
    });
  }, [risks, severityFilter, statusFilter, search]);

  const getSeverityBadge = (sev: RiskSeverity) => {
    switch (sev) {
      case 'CRITICAL':
        return <Badge variant="danger">Critical Risk</Badge>;
      case 'HIGH':
        return <Badge variant="warning">High Risk</Badge>;
      case 'MEDIUM':
        return <Badge variant="neutral">Medium</Badge>;
      case 'LOW':
      default:
        return <Badge variant="neutral">Low</Badge>;
    }
  };

  const getStatusBadge = (status: RiskStatus) => {
    switch (status) {
      case 'RESOLVED':
        return <Badge variant="success">Resolved</Badge>;
      case 'MITIGATING':
        return <Badge variant="info">Mitigating</Badge>;
      case 'ACCEPTED':
        return <Badge variant="neutral">Accepted</Badge>;
      case 'OPEN':
      default:
        return <Badge variant="danger">Open</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-risks-page" id="mentor-risks-loading">
        <Skeleton width="100%" height="160px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <Skeleton width="100%" height="56px" style={{ borderRadius: '8px', marginBottom: '1rem' }} />
        <Skeleton width="100%" height="300px" style={{ borderRadius: '12px' }} />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-mentor-risks-page" id="mentor-risks-error">
        <div className="gf-mentor-risks-error-card" role="alert">
          <h3>Risk Supervision Restricted</h3>
          <p>{error || 'Project risks not found or access denied.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-risks-page" id="mentor-risks-container">
      <MentorInstanceHeader project={project} activeTab="risks" />

      {/* Filter and Search Bar (Read-Only) */}
      <div className="gf-mentor-risks__toolbar" id="mentor-risks-toolbar">
        <div className="gf-mentor-risks__search-wrap">
          <Input
            id="mentor-risks-search"
            type="search"
            placeholder="Search risks by code, title, or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="gf-mentor-risks__filters">
          <label className="gf-mentor-risks__filter-label">
            <span>Severity:</span>
            <select
              id="filter-risk-severity"
              className="gf-mentor-risks__select"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </label>

          <label className="gf-mentor-risks__filter-label">
            <span>Status:</span>
            <select
              id="filter-risk-status"
              className="gf-mentor-risks__select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="MITIGATING">Mitigating</option>
              <option value="RESOLVED">Resolved</option>
              <option value="ACCEPTED">Accepted</option>
            </select>
          </label>
        </div>
      </div>

      <div className="gf-mentor-risks__content">
        <div className="gf-mentor-risks__header-info">
          <span>
            Showing <strong>{filteredRisks.length}</strong> of <strong>{risks.length}</strong> risks
          </span>
          <span className="gf-mentor-risks__read-only-indicator">READ-ONLY SUPERVISION</span>
        </div>

        {filteredRisks.length === 0 ? (
          <div className="gf-mentor-risks__empty-state" id="mentor-risks-empty">
            <p>No risks match the selected filter criteria or no risks have been logged.</p>
          </div>
        ) : (
          <div className="gf-mentor-risks__list" id="mentor-risks-list">
            {filteredRisks.map((r) => (
              <div key={r.id} className="gf-mentor-risk-card" id={`risk-card-${r.id}`}>
                <div className="gf-mentor-risk-card__top">
                  <div className="gf-mentor-risk-card__title-group">
                    <span className="gf-mentor-risk-card__code">{r.risk_code}</span>
                    <h3 className="gf-mentor-risk-card__title">{r.title}</h3>
                  </div>
                  <div className="gf-mentor-risk-card__badges">
                    {getSeverityBadge(r.severity)}
                    {getStatusBadge(r.status)}
                  </div>
                </div>

                {r.description && (
                  <p className="gf-mentor-risk-card__desc">{r.description}</p>
                )}

                <div className="gf-mentor-risk-card__matrix">
                  <div className="gf-mentor-risk-card__matrix-item">
                    <span className="gf-mentor-risk-card__label">Probability:</span>
                    <strong>{r.probability}</strong>
                  </div>
                  <div className="gf-mentor-risk-card__matrix-item">
                    <span className="gf-mentor-risk-card__label">Impact:</span>
                    <strong>{r.impact}</strong>
                  </div>
                  <div className="gf-mentor-risk-card__matrix-item">
                    <span className="gf-mentor-risk-card__label">Owner:</span>
                    <span>{r.owner || 'Unassigned'}</span>
                  </div>
                </div>

                <div className="gf-mentor-risk-card__mitigation-box">
                  <span className="gf-mentor-risk-card__mitigation-label">Mitigation Strategy:</span>
                  <p className="gf-mentor-risk-card__mitigation-text">
                    {r.mitigation || 'No mitigation recorded yet.'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
