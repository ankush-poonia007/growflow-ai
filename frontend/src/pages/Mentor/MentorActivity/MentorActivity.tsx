import { useEffect, useState } from 'react';
import { getMentorPortfolioActivity } from '@/lib/api/client';
import type { ActivityItemResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorActivity.css';

export function MentorActivity() {
  const [activity, setActivity] = useState<ActivityItemResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const data = await getMentorPortfolioActivity();
        if (mounted) {
          setActivity(data);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to retrieve portfolio activity or access denied.';
          setError(msg);
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
  }, []);

  const getActorBadge = (role?: string) => {
    switch ((role || '').toUpperCase()) {
      case 'STUDENT':
        return <Badge variant="info">Student</Badge>;
      case 'MENTOR':
        return <Badge variant="warning">Mentor</Badge>;
      case 'AI_MENTOR':
      case 'AI':
        return <Badge variant="neutral">AI Copilot</Badge>;
      default:
        return <Badge variant="neutral">{role || 'System'}</Badge>;
    }
  };

  const formatTimestamp = (ts: string | null) => {
    if (!ts) return '--';
    try {
      return new Date(ts).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return ts;
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-activity-view" id="mentor-portfolio-activity-loading">
        <Skeleton width="280px" height="32px" style={{ marginBottom: '1rem' }} />
        <Skeleton width="450px" height="20px" style={{ marginBottom: '2rem' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Skeleton height="90px" style={{ borderRadius: '12px' }} />
          <Skeleton height="90px" style={{ borderRadius: '12px' }} />
          <Skeleton height="90px" style={{ borderRadius: '12px' }} />
          <Skeleton height="90px" style={{ borderRadius: '12px' }} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="gf-mentor-activity-view" id="mentor-portfolio-activity-error">
        <PageHeader
          eyebrow="PORTFOLIO AUDIT TRAIL"
          title="Mentor Portfolio Activity"
          breadcrumbs={[
            { label: 'Overview', to: '/mentor/overview' },
            { label: 'Activity' },
          ]}
        />
        <div className="gf-mentor-activity-view__error-card" role="alert">
          <h3>Supervision Access Restricted</h3>
          <p>{error}</p>
          <Button as="link" to="/mentor/overview" variant="secondary">
            Return to Overview
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-activity-view" id="mentor-portfolio-activity-container">
      <PageHeader
        eyebrow="SUPERVISORY AUDIT TRAIL"
        title="Mentor Portfolio Activity"
        description="Comprehensive chronological domain events across all your supervised cohorts, students, and project instances."
        badge={
          <div className="gf-mentor-activity-view__badges">
            <Badge variant="neutral">READ-ONLY SUPERVISION</Badge>
            <span className="gf-mentor-activity-view__count-pill">
              {activity.length} event{activity.length === 1 ? '' : 's'}
            </span>
          </div>
        }
      />

      <div className="gf-mentor-activity-view__card">
        <div className="gf-mentor-activity-view__header">
          <div>
            <span className="gf-mentor-activity-view__eyebrow">CANONICAL DOMAIN EVENTS</span>
            <h2 className="gf-mentor-activity-view__heading">Portfolio Activity Stream</h2>
          </div>
          <span className="gf-mentor-activity-view__scope-label">AUTHORIZED PORTFOLIO SCOPE</span>
        </div>

        {activity.length === 0 ? (
          <div className="gf-mentor-activity-view__empty" id="mentor-portfolio-activity-empty">
            <p>No activity yet.</p>
          </div>
        ) : (
          <div className="gf-mentor-activity-view__timeline" id="mentor-portfolio-activity-timeline">
            {activity.map((evt) => (
              <div key={evt.id} className="gf-portfolio-activity-item" id={`portfolio-activity-item-${evt.id}`}>
                <div className="gf-portfolio-activity-item__dot" />
                <div className="gf-portfolio-activity-item__content">
                  <div className="gf-portfolio-activity-item__top">
                    <div className="gf-portfolio-activity-item__title-group">
                      <h3 className="gf-portfolio-activity-item__title">{evt.title}</h3>
                      <span className="gf-portfolio-activity-item__event-type">{evt.event_type}</span>
                    </div>
                    <div className="gf-portfolio-activity-item__meta">
                      {getActorBadge(evt.actor_role)}
                      <time className="gf-portfolio-activity-item__time" dateTime={evt.occurred_at || ''}>
                        {formatTimestamp(evt.occurred_at)}
                      </time>
                    </div>
                  </div>
                  <p className="gf-portfolio-activity-item__desc">{evt.description}</p>
                  <div className="gf-portfolio-activity-item__context-row">
                    {evt.group_id && (
                      <span className="gf-portfolio-activity-item__context-tag">
                        Cohort ID: {evt.group_id.slice(0, 8)}...
                      </span>
                    )}
                    {evt.project_instance_id && (
                      <span className="gf-portfolio-activity-item__context-tag">
                        Project ID: {evt.project_instance_id.slice(0, 8)}...
                      </span>
                    )}
                    <span className="gf-portfolio-activity-item__context-tag">
                      Resource: {evt.resource_type}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
