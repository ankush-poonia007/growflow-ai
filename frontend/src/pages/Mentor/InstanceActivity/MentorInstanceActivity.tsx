import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectInstance, getMentorInstanceActivity } from '@/lib/api/client';
import type { MentorProjectInstanceDetail, ActivityItemResponse } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceActivity.css';

export const MentorInstanceActivity: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [activity, setActivity] = useState<ActivityItemResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const [projRes, actRes] = await Promise.all([
          getMentorProjectInstance(projectId),
          getMentorInstanceActivity(projectId),
        ]);
        if (mounted) {
          setProject(projRes);
          setActivity(actRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          setError(
            err instanceof Error ? err.message : 'Failed to retrieve project activity or access denied.'
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

  const getActorBadge = (role: string) => {
    switch (role.toUpperCase()) {
      case 'STUDENT':
        return <Badge variant="info">Student</Badge>;
      case 'MENTOR':
        return <Badge variant="warning">Mentor</Badge>;
      case 'AI_MENTOR':
      case 'AI':
        return <Badge variant="neutral">AI Copilot</Badge>;
      default:
        return <Badge variant="neutral">{role}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-activity-page" id="mentor-activity-loading">
        <Skeleton width="100%" height="160px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Skeleton width="100%" height="80px" style={{ borderRadius: '12px' }} />
          <Skeleton width="100%" height="80px" style={{ borderRadius: '12px' }} />
          <Skeleton width="100%" height="80px" style={{ borderRadius: '12px' }} />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-mentor-activity-page" id="mentor-activity-error">
        <div className="gf-mentor-activity-error-card" role="alert">
          <h3>Activity Supervision Restricted</h3>
          <p>{error || 'Project activity not found or access denied.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-activity-page" id="mentor-activity-container">
      <MentorInstanceHeader project={project} activeTab="activity" />

      <div className="gf-mentor-activity__card">
        <div className="gf-mentor-activity__header">
          <div>
            <span className="gf-mentor-activity__eyebrow">CANONICAL AUDIT TRAIL</span>
            <h2 className="gf-mentor-activity__heading">Project Event History</h2>
          </div>
          <span className="gf-mentor-activity__read-only-pill">READ-ONLY SUPERVISION</span>
        </div>

        {activity.length === 0 ? (
          <div className="gf-mentor-activity__empty" id="mentor-activity-empty">
            <p>No domain events have been recorded for this project instance yet.</p>
          </div>
        ) : (
          <div className="gf-mentor-activity__timeline" id="mentor-activity-timeline">
            {activity.map((evt) => (
              <div key={evt.id} className="gf-mentor-activity-item" id={`activity-item-${evt.id}`}>
                <div className="gf-mentor-activity-item__dot" />
                <div className="gf-mentor-activity-item__content">
                  <div className="gf-mentor-activity-item__top">
                    <div className="gf-mentor-activity-item__title-group">
                      <h3 className="gf-mentor-activity-item__title">{evt.title}</h3>
                      <span className="gf-mentor-activity-item__event-type">{evt.event_type}</span>
                    </div>
                    <div className="gf-mentor-activity-item__badges">
                      {getActorBadge(evt.actor_role)}
                      <span className="gf-mentor-activity-item__time">
                        {evt.occurred_at ? new Date(evt.occurred_at).toLocaleString() : '—'}
                      </span>
                    </div>
                  </div>

                  <p className="gf-mentor-activity-item__desc">{evt.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
