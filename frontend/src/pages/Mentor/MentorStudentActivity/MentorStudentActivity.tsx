import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router';
import { getMentorStudent, getMentorStudentActivity } from '@/lib/api/client';
import type { MentorStudentDetail, ActivityItemResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import './MentorStudentActivity.css';

export function MentorStudentActivity() {
  const { studentId } = useParams<{ studentId: string }>();
  const [student, setStudent] = useState<MentorStudentDetail | null>(null);
  const [activity, setActivity] = useState<ActivityItemResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!studentId) return;
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [sRes, aRes] = await Promise.all([
          getMentorStudent(studentId!),
          getMentorStudentActivity(studentId!),
        ]);

        if (mounted) {
          setStudent(sRes);
          setActivity(aRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to retrieve student activity or access was denied.';
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
  }, [studentId]);

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
      <div className="gf-mentor-student-activity" id="student-activity-loading">
        <Skeleton width="220px" height="24px" style={{ marginBottom: '1rem' }} />
        <Skeleton width="100%" height="80px" style={{ borderRadius: '14px', marginBottom: '1.5rem' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Skeleton height="85px" style={{ borderRadius: '12px' }} />
          <Skeleton height="85px" style={{ borderRadius: '12px' }} />
          <Skeleton height="85px" style={{ borderRadius: '12px' }} />
        </div>
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="gf-mentor-student-activity" id="student-activity-error">
        <div className="gf-mentor-student-activity__nav">
          <Link to="/mentor/students">← Back to Supervised Students</Link>
        </div>
        <div className="gf-mentor-student-activity__error-card" role="alert">
          <h3>Supervision Access Restriction</h3>
          <p>{error || 'Student activity not found or you do not supervise this student.'}</p>
          <Button as="link" to="/mentor/students" variant="secondary">
            Return to Students Directory
          </Button>
        </div>
      </div>
    );
  }

  const initials = student.full_name
    ? student.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2)
    : student.email.substring(0, 2).toUpperCase();

  return (
    <div className="gf-mentor-student-activity" id="student-activity-container">
      <div className="gf-mentor-student-activity__nav">
        <Link to="/mentor/students">← Supervised Students</Link>
        <span>/</span>
        <Link to={`/mentor/students/${student.id || student.student_id || studentId}`}>{student.full_name}</Link>
        <span>/</span>
        <span>Activity</span>
      </div>

      <PageHeader
        eyebrow="STUDENT SUPERVISION · AUDIT TRAIL"
        title={`${student.full_name} — Activity`}
        description={`Domain activity audit trail for ${student.full_name} (${student.email})`}
        badge={<Badge variant="neutral">READ-ONLY SUPERVISION</Badge>}
        actions={
          <div className="gf-mentor-student-activity__actions">
            <Button
              as="link"
              to={`/mentor/students/${student.id || student.student_id || studentId}`}
              variant="tertiary"
              size="sm"
            >
              Profile
            </Button>
            <Button
              as="link"
              to={`/mentor/students/${student.id || student.student_id || studentId}/projects`}
              variant="tertiary"
              size="sm"
            >
              Projects
            </Button>
          </div>
        }
      />

      {/* Student Badge Card */}
      <div className="gf-mentor-student-activity__student-card">
        <div className="gf-mentor-student-activity__avatar" aria-hidden="true">
          {student.avatar_url ? (
            <img src={student.avatar_url} alt={student.full_name} />
          ) : (
            <span>{initials}</span>
          )}
        </div>
        <div className="gf-mentor-student-activity__student-info">
          <h2 className="gf-mentor-student-activity__student-name">{student.full_name}</h2>
          <span className="gf-mentor-student-activity__student-email">{student.email}</span>
          <div className="gf-mentor-student-activity__groups-list">
            {student.groups?.map((g) => (
              <span key={g.id} className="gf-mentor-student-activity__group-tag">
                Cohort: {g.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Activity Timeline Card */}
      <div className="gf-mentor-student-activity__timeline-card">
        <div className="gf-mentor-student-activity__timeline-header">
          <div>
            <span className="gf-mentor-student-activity__eyebrow">CANONICAL DOMAIN EVENTS</span>
            <h3 className="gf-mentor-student-activity__timeline-title">Event Timeline</h3>
          </div>
          <span className="gf-mentor-student-activity__event-count">
            {activity.length} event{activity.length === 1 ? '' : 's'}
          </span>
        </div>

        {activity.length === 0 ? (
          <div className="gf-mentor-student-activity__empty" id="student-activity-empty">
            <p>No activity yet.</p>
          </div>
        ) : (
          <div className="gf-mentor-student-activity__timeline" id="student-activity-timeline">
            {activity.map((evt) => (
              <div key={evt.id} className="gf-student-activity-item" id={`student-activity-item-${evt.id}`}>
                <div className="gf-student-activity-item__dot" />
                <div className="gf-student-activity-item__content">
                  <div className="gf-student-activity-item__top">
                    <div className="gf-student-activity-item__title-group">
                      <h4 className="gf-student-activity-item__title">{evt.title}</h4>
                      <span className="gf-student-activity-item__event-type">{evt.event_type}</span>
                    </div>
                    <div className="gf-student-activity-item__meta">
                      {getActorBadge(evt.actor_role)}
                      <time className="gf-student-activity-item__time" dateTime={evt.occurred_at || ''}>
                        {formatTimestamp(evt.occurred_at)}
                      </time>
                    </div>
                  </div>
                  <p className="gf-student-activity-item__desc">{evt.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
