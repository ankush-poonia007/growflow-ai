import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router';
import { getMentorStudents, getMentorGroups } from '@/lib/api/client';
import type { MentorStudentSummary, GroupResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentsDirectory.css';

export function StudentsDirectory() {
  const [students, setStudents] = useState<MentorStudentSummary[]>([]);
  const [groups, setGroups] = useState<GroupResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [studentsData, groupsData] = await Promise.all([
        getMentorStudents({
          search: search.trim() || undefined,
          group_id: selectedGroup || undefined,
        }),
        getMentorGroups(),
      ]);
      setStudents(studentsData);
      setGroups(groupsData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve students.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [search, selectedGroup]);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadData();
    }, 200);
    return () => {
      clearTimeout(timer);
    };
  }, [loadData]);

  const totalStudents = students.length;
  const atRiskCount = students.reduce((sum, s) => sum + s.at_risk_project_count, 0);
  const totalProjects = students.reduce((sum, s) => sum + s.project_count, 0);

  return (
    <div className="gf-students-directory" id="mentor-students-directory">
      <PageHeader
        eyebrow="SUPERVISE"
        title="Supervised Students"
        description="Directory of students enrolled in your supervised cohorts. Monitor engagement, assigned projects, and risk indicators."
      />

      <div className="gf-students-directory__stats">
        <div className="gf-students-directory__stat-card" id="stat-total-students">
          <span className="gf-students-directory__stat-label">Total Supervised Students</span>
          <span className="gf-students-directory__stat-value">{totalStudents}</span>
        </div>
        <div className="gf-students-directory__stat-card" id="stat-total-projects">
          <span className="gf-students-directory__stat-label">Total Student Projects</span>
          <span className="gf-students-directory__stat-value">{totalProjects}</span>
        </div>
        <div className="gf-students-directory__stat-card" id="stat-at-risk-projects">
          <span className="gf-students-directory__stat-label">Projects At Risk</span>
          <span
            className={`gf-students-directory__stat-value ${
              atRiskCount > 0 ? 'gf-students-directory__stat-value--danger' : ''
            }`}
          >
            {atRiskCount}
          </span>
        </div>
      </div>

      <div className="gf-students-directory__filters">
        <div className="gf-students-directory__search">
          <Input
            id="students-search-input"
            type="search"
            placeholder="Search by student name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          id="students-group-filter"
          className="gf-students-directory__filter-select"
          value={selectedGroup}
          onChange={(e) => setSelectedGroup(e.target.value)}
        >
          <option value="">All Cohorts / Groups</option>
          {groups.map((grp) => (
            <option key={grp.id} value={grp.id}>
              {grp.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadData} />
        </div>
      )}

      {loading ? (
        <div className="gf-students-directory__grid" id="students-directory-loading">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="gf-student-card" style={{ gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <Skeleton width="48px" height="48px" variant="circle" />
                <div style={{ flex: 1 }}>
                  <Skeleton width="60%" height="18px" />
                  <div style={{ height: '6px' }} />
                  <Skeleton width="40%" height="14px" />
                </div>
              </div>
              <Skeleton width="100%" height="40px" style={{ borderRadius: '8px' }} />
              <Skeleton width="100%" height="36px" style={{ borderRadius: '8px' }} />
            </div>
          ))}
        </div>
      ) : students.length === 0 ? (
        <EmptyState
          title="No supervised students found"
          description={
            search || selectedGroup
              ? 'No students matched your search criteria or selected cohort.'
              : 'You do not have any students enrolled in your supervised groups yet.'
          }
        />
      ) : (
        <div className="gf-students-directory__grid" id="students-directory-grid">
          {students.map((student) => {
            const initials = student.full_name
              ? student.full_name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
                  .substring(0, 2)
              : student.email.substring(0, 2).toUpperCase();

            return (
              <div
                key={student.id}
                className="gf-student-card"
                id={`student-card-${student.id}`}
              >
                <div className="gf-student-card__header">
                  <div className="gf-student-card__avatar">
                    {student.avatar_url ? (
                      <img src={student.avatar_url} alt={student.full_name} />
                    ) : (
                      <span>{initials}</span>
                    )}
                  </div>
                  <div className="gf-student-card__info">
                    <Link
                      to={`/mentor/students/${student.id}`}
                      className="gf-student-card__name"
                      id={`student-name-link-${student.id}`}
                    >
                      {student.full_name}
                    </Link>
                    <span className="gf-student-card__email">{student.email}</span>
                  </div>
                </div>

                <div className="gf-student-card__groups">
                  {student.groups.length > 0 ? (
                    student.groups.map((grp) => (
                      <Badge key={grp.id} variant="neutral">
                        {grp.name}
                      </Badge>
                    ))
                  ) : (
                    <span style={{ fontSize: '0.75rem', color: 'var(--gf-text-secondary)' }}>
                      No cohort assigned
                    </span>
                  )}
                </div>

                <div className="gf-student-card__metrics">
                  <div className="gf-student-card__metric-item">
                    <span className="gf-student-card__metric-title">Projects</span>
                    <span className="gf-student-card__metric-num">{student.project_count}</span>
                  </div>
                  <div className="gf-student-card__metric-item">
                    <span className="gf-student-card__metric-title">Health / Risk</span>
                    <span className="gf-student-card__metric-num">
                      {student.at_risk_project_count > 0 ? (
                        <Badge variant="danger">{student.at_risk_project_count} At Risk</Badge>
                      ) : (
                        <Badge variant="success">All Healthy</Badge>
                      )}
                    </span>
                  </div>
                </div>

                <div className="gf-student-card__actions">
                  <Button
                    as="link"
                    to={`/mentor/students/${student.id}`}
                    variant="secondary"
                    size="sm"
                    id={`view-student-${student.id}`}
                  >
                    View Detail
                  </Button>
                  <Button
                    as="link"
                    to={`/mentor/students/${student.id}/projects`}
                    variant="tertiary"
                    size="sm"
                    id={`view-student-projects-${student.id}`}
                  >
                    Projects ({student.project_count})
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
export default StudentsDirectory;
