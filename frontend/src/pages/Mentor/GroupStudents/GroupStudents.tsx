import { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { getMentorGroup, getGroupStudents } from '@/lib/api/client';
import type { GroupResponse, GroupStudentResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import './GroupStudents.css';

export function GroupStudents() {
  const { groupId } = useParams<{ groupId: string }>();
  const [group, setGroup] = useState<GroupResponse | null>(null);
  const [students, setStudents] = useState<GroupStudentResponse[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!groupId) return;
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [gRes, sRes] = await Promise.all([
          getMentorGroup(groupId!),
          getGroupStudents(groupId!),
        ]);
        if (mounted) {
          setGroup(gRes);
          setStudents(sRes);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : 'Failed to load group students.';
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

  const filteredStudents = students.filter((s) => {
    const q = search.toLowerCase().trim();
    if (!q) return true;
    return (
      (s.full_name && s.full_name.toLowerCase().includes(q)) ||
      s.email.toLowerCase().includes(q)
    );
  });

  return (
    <div className="gf-group-students">
      <PageHeader
        eyebrow="COHORT ROSTER"
        title="Enrolled Students"
        description={`Manage students currently enrolled in ${group ? group.name : 'this group'}.`}
        breadcrumbs={[
          { label: 'Groups', to: '/mentor/groups' },
          {
            label: group?.name || 'Cohort',
            to: groupId ? `/mentor/groups/${groupId}` : undefined,
          },
          { label: 'Students' },
        ]}
      />

      {error && (
        <div className="gf-group-students__error" role="alert">
          {error}
        </div>
      )}

      {/* Roster Controls */}
      <div className="gf-group-students__controls">
        <div className="gf-group-students__search">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search students by name or email..."
            aria-label="Filter students roster"
          />
        </div>
        <div className="gf-group-students__count">
          {students.length} {students.length === 1 ? 'Student' : 'Students'} Enrolled
        </div>
      </div>

      {loading ? (
        <div className="gf-group-students__loading">
          <Skeleton height="60px" />
          <Skeleton height="60px" />
          <Skeleton height="60px" />
        </div>
      ) : students.length === 0 ? (
        <EmptyState
          title="No Students Enrolled"
          description={
            group
              ? `Share the join code "${group.join_code}" with your students so they can join this cohort.`
              : 'No students have joined this cohort yet.'
          }
        />
      ) : filteredStudents.length === 0 ? (
        <EmptyState
          title="No Matching Students"
          description={`No students found matching "${search}".`}
        />
      ) : (
        <Card className="gf-group-students__table-card">
          <div className="gf-group-students__table-wrap">
            <table className="gf-group-students__table" aria-label="Students roster table">
              <thead>
                <tr>
                  <th scope="col">Student</th>
                  <th scope="col">Email</th>
                  <th scope="col">Status</th>
                  <th scope="col">Enrolled Date</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map((s) => (
                  <tr key={s.student_id}>
                    <td>
                      <div className="gf-group-students__cell-student">
                        <div className="gf-group-students__avatar" aria-hidden="true">
                          {(s.full_name?.[0] || s.email[0] || '?').toUpperCase()}
                        </div>
                        <span className="gf-group-students__name">
                          {s.full_name || 'GrowFlow Student'}
                        </span>
                      </div>
                    </td>
                    <td className="gf-group-students__cell-email">{s.email}</td>
                    <td>
                      <Badge variant={s.status === 'ACTIVE' ? 'success' : 'neutral'}>
                        {s.status}
                      </Badge>
                    </td>
                    <td className="gf-group-students__cell-date">
                      {new Date(s.joined_at).toLocaleDateString()}
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
