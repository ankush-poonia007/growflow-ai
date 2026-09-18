import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorProjectInstance, getMentorInstanceMilestones } from '@/lib/api/client';
import type { MentorProjectInstanceDetail, MilestoneResponse, MilestoneStatus } from '@/lib/api/types';
import { MentorInstanceHeader } from '@/components/navigation/MentorInstanceHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorInstanceMilestones.css';

export const MentorInstanceMilestones: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<MentorProjectInstanceDetail | null>(null);
  const [milestones, setMilestones] = useState<MilestoneResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      if (!projectId) return;
      try {
        setLoading(true);
        setError(null);
        const [projRes, milestonesRes] = await Promise.all([
          getMentorProjectInstance(projectId),
          getMentorInstanceMilestones(projectId),
        ]);
        if (mounted) {
          setProject(projRes);
          setMilestones(milestonesRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          setError(
            err instanceof Error
              ? err.message
              : 'Failed to retrieve project milestones or access denied.'
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

  const getMilestoneStatusBadge = (status: MilestoneStatus) => {
    switch (status) {
      case 'COMPLETED':
        return <Badge variant="success">Completed</Badge>;
      case 'IN_PROGRESS':
        return <Badge variant="info">In Progress</Badge>;
      case 'AT_RISK':
        return <Badge variant="danger">At Risk</Badge>;
      case 'UPCOMING':
      default:
        return <Badge variant="neutral">Upcoming</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-milestones-page" id="mentor-milestones-loading">
        <Skeleton width="100%" height="160px" style={{ borderRadius: '12px', marginBottom: '1.5rem' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Skeleton width="100%" height="120px" style={{ borderRadius: '12px' }} />
          <Skeleton width="100%" height="120px" style={{ borderRadius: '12px' }} />
          <Skeleton width="100%" height="120px" style={{ borderRadius: '12px' }} />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="gf-mentor-milestones-page" id="mentor-milestones-error">
        <div className="gf-mentor-milestones-error-card" role="alert">
          <h3>Milestone Supervision Restricted</h3>
          <p>{error || 'Project milestones not found or access denied.'}</p>
          <Button as="link" to="/mentor/project-instances" variant="secondary">
            Return to Project Instances
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-milestones-page" id="mentor-milestones-container">
      <MentorInstanceHeader project={project} activeTab="milestones" />

      <div className="gf-mentor-milestones__header-bar">
        <div>
          <span className="gf-mentor-milestones__eyebrow">VERIFICATION GATES & PROGRESSION</span>
          <h2 className="gf-mentor-milestones__heading">Execution Milestones</h2>
        </div>
        <span className="gf-mentor-milestones__read-only-tag">READ-ONLY SUPERVISION</span>
      </div>

      {milestones.length === 0 ? (
        <div className="gf-mentor-milestones__empty-state" id="mentor-milestones-empty">
          <p>No execution milestones have been generated or configured for this project instance.</p>
        </div>
      ) : (
        <div className="gf-mentor-milestones__list" id="mentor-milestones-list">
          {milestones.map((m) => (
            <div key={m.id} className="gf-mentor-milestone-card" id={`milestone-card-${m.id}`}>
              <div className="gf-mentor-milestone-card__header">
                <div className="gf-mentor-milestone-card__title-group">
                  <span className="gf-mentor-milestone-card__gate-code">{m.gate_code}</span>
                  <h3 className="gf-mentor-milestone-card__title">{m.title}</h3>
                </div>
                <div className="gf-mentor-milestone-card__badge-group">
                  {getMilestoneStatusBadge(m.status)}
                </div>
              </div>

              {m.description && (
                <p className="gf-mentor-milestone-card__desc">{m.description}</p>
              )}

              <div className="gf-mentor-milestone-card__progress-wrap">
                <div className="gf-mentor-milestone-card__progress-info">
                  <span>Progress Completion</span>
                  <strong>{m.progress_percent}%</strong>
                </div>
                <div className="gf-mentor-milestone-card__progress-track">
                  <div
                    className="gf-mentor-milestone-card__progress-bar"
                    style={{ width: `${m.progress_percent}%` }}
                  />
                </div>
              </div>

              <div className="gf-mentor-milestone-card__footer">
                <div className="gf-mentor-milestone-card__meta-item">
                  <span className="gf-mentor-milestone-card__meta-label">Tasks:</span>
                  <span>
                    <strong>{m.completed_task_count}</strong> of {m.task_count} completed
                  </span>
                </div>

                <div className="gf-mentor-milestone-card__meta-item">
                  <span className="gf-mentor-milestone-card__meta-label">Target Date:</span>
                  <span>{m.target_date ? new Date(m.target_date).toLocaleDateString() : 'Not Set'}</span>
                </div>

                {m.deliverables && m.deliverables.length > 0 && (
                  <div className="gf-mentor-milestone-card__deliverables">
                    <span className="gf-mentor-milestone-card__meta-label">Deliverables:</span>
                    <ul>
                      {m.deliverables.map((del, idx) => (
                        <li key={idx}>{del}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
