import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getMentorGroup, getGroupActivity } from '@/lib/api/client';
import type { GroupResponse, ActivityItemResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupActivity.css';

export function GroupActivity() {
  const { groupId } = useParams<{ groupId: string }>();
  const [group, setGroup] = useState<GroupResponse | null>(null);
  const [activity, setActivity] = useState<ActivityItemResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!groupId) return;
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [gRes, aRes] = await Promise.all([
          getMentorGroup(groupId!),
          getGroupActivity(groupId!),
        ]);

        if (mounted) {
          setGroup(gRes);
          setActivity(aRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to retrieve cohort activity or access denied.';
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
  }, [groupId]);

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
      <div className="gf-group-activity-page" id="group-activity-loading">
        <Skeleton height="60px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <Skeleton height="40px" style={{ borderRadius: '8px', marginBottom: '1.5rem', width: '380px' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Skeleton height="85px" style={{ borderRadius: '12px' }} />
          <Skeleton height="85px" style={{ borderRadius: '12px' }} />
          <Skeleton height="85px" style={{ borderRadius: '12px' }} />
        </div>
      </div>
    );
  }

  if (error || !group) {
    return (
      <div className="gf-group-activity-page" id="group-activity-error">
        <PageHeader
          eyebrow="COHORT SUPERVISION"
          title="Activity Restricted"
          breadcrumbs={[
            { label: 'Groups', to: '/mentor/groups' },
            { label: 'Activity' },
          ]}
        />
        <div className="gf-group-activity__error-card" role="alert">
          <h3>Cohort Activity Restricted</h3>
          <p>{error || 'This student group does not exist or you do not have permission to view its activity.'}</p>
          <Button as="link" to="/mentor/groups" variant="secondary">
            Return to Groups Directory
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-group-activity-page" id="group-activity-container">
      <PageHeader
        eyebrow="COHORT WORKSPACE"
        title={group.name}
        breadcrumbs={[
          { label: 'Groups', to: '/mentor/groups' },
          { label: group.name, to: `/mentor/groups/${groupId}` },
          { label: 'Activity' },
        ]}
        badge={
          <Badge variant={group.status === 'ACTIVE' ? 'success' : 'neutral'}>
            {group.status}
          </Badge>
        }
      />

      {/* Cohort Tabs */}
      <nav className="gf-group-workspace__tabs" aria-label="Cohort sections">
        <Link to={`/mentor/groups/${groupId}`} className="gf-group-workspace__tab">
          Overview
        </Link>
        <Link to={`/mentor/groups/${groupId}/students`} className="gf-group-workspace__tab">
          Students
        </Link>
        <Link to={`/mentor/groups/${groupId}/projects`} className="gf-group-workspace__tab">
          Projects
        </Link>
        <Link to={`/mentor/groups/${groupId}/at-risk`} className="gf-group-workspace__tab">
          At-Risk
        </Link>
        <Link
          to={`/mentor/groups/${groupId}/activity`}
          className="gf-group-workspace__tab gf-group-workspace__tab--active"
          aria-current="page"
        >
          Activity ({activity.length})
        </Link>
        <Link to={`/mentor/groups/${groupId}/ai`} className="gf-group-workspace__tab">
          AI Mentor
        </Link>
      </nav>

      {/* Activity Card */}
      <div className="gf-group-activity__card">
        <div className="gf-group-activity__header">
          <div>
            <span className="gf-group-activity__eyebrow">CANONICAL AUDIT TRAIL</span>
            <h2 className="gf-group-activity__heading">Cohort Domain Activity</h2>
          </div>
          <span className="gf-group-activity__read-only-pill">READ-ONLY SUPERVISION</span>
        </div>

        {activity.length === 0 ? (
          <div className="gf-group-activity__empty" id="group-activity-empty">
            <p>No activity yet.</p>
          </div>
        ) : (
          <div className="gf-group-activity__timeline" id="group-activity-timeline">
            {activity.map((evt) => (
              <div key={evt.id} className="gf-group-activity-item" id={`group-activity-item-${evt.id}`}>
                <div className="gf-group-activity-item__dot" />
                <div className="gf-group-activity-item__content">
                  <div className="gf-group-activity-item__top">
                    <div className="gf-group-activity-item__title-group">
                      <h3 className="gf-group-activity-item__title">{evt.title}</h3>
                      <span className="gf-group-activity-item__event-type">{evt.event_type}</span>
                    </div>
                    <div className="gf-group-activity-item__meta">
                      {getActorBadge(evt.actor_role)}
                      <time className="gf-group-activity-item__time" dateTime={evt.occurred_at || ''}>
                        {formatTimestamp(evt.occurred_at)}
                      </time>
                    </div>
                  </div>
                  <p className="gf-group-activity-item__desc">{evt.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
