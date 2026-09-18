import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/auth/useAuth';
import { getStudentProfile, updateStudentProfile } from '@/lib/api/client';
import type { StudentProfile } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './StudentProfile.css';

export function StudentProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Edit state
  const [isEditing, setIsEditing] = useState(false);
  const [bio, setBio] = useState('');
  const [goals, setGoals] = useState('');
  const [interests, setInterests] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStudentProfile();
      setProfile(data);
      setBio(data.bio || '');
      setGoals(data.goals || '');
      setInterests(data.interests || '');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve student profile.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
    };
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setSaveError(null);
      setSaveSuccess(false);
      const updated = await updateStudentProfile({
        bio: bio.trim() || null,
        goals: goals.trim() || null,
        interests: interests.trim() || null,
      });
      setProfile(updated);
      setBio(updated.bio || '');
      setGoals(updated.goals || '');
      setInterests(updated.interests || '');
      setIsEditing(false);
      setSaveSuccess(true);
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
      feedbackTimerRef.current = setTimeout(() => {
        setSaveSuccess(false);
        feedbackTimerRef.current = null;
      }, 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update student profile.';
      setSaveError(msg);
    } finally {
      setSaving(false);
    }
  };

  const displayName = user?.fullName?.trim() || user?.email?.trim() || '—';
  const initials = displayName !== '—'
    ? displayName
        .split(/\s+/)
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2)
    : 'ST';

  if (loading) {
    return (
      <div className="gf-student-profile" id="student-profile-loading">
        <Skeleton width="220px" height="28px" style={{ marginBottom: '1rem' }} />
        <Skeleton width="100%" height="160px" style={{ borderRadius: '14px', marginBottom: '1.5rem' }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
          <Skeleton height="180px" style={{ borderRadius: '14px' }} />
          <Skeleton height="180px" style={{ borderRadius: '14px' }} />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-student-profile" id="student-profile-container">
      <PageHeader
        eyebrow="ACCOUNT & LEARNING CONTEXT"
        title="Student Profile"
        description="Canonical identity, learning objectives, and skill context for your build workspace."
        badge={<Badge variant="neutral">STUDENT WORKPLACE</Badge>}
        actions={
          !isEditing && (
            <Button
              variant="secondary"
              onClick={() => setIsEditing(true)}
              id="edit-student-profile-btn"
            >
              Edit Profile
            </Button>
          )
        }
      />

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadData} />
        </div>
      )}

      {saveSuccess && (
        <div className="gf-student-profile__alert gf-student-profile__alert--success" role="status">
          Profile updated successfully.
        </div>
      )}

      {/* Primary Identity Card */}
      <Card variant="bordered" className="gf-student-profile__identity-card">
        <CardContent>
          <div className="gf-student-profile__identity-row">
            <div className="gf-student-profile__avatar">
              <span>{initials}</span>
            </div>
            <div className="gf-student-profile__identity-meta">
              <div className="gf-student-profile__name-row">
                <h2 className="gf-student-profile__display-name">{displayName}</h2>
                <Badge variant="info">Student Account</Badge>
                <Badge variant="success">Active</Badge>
              </div>
              <p className="gf-student-profile__email">{user?.email}</p>
              <div className="gf-student-profile__id-tags">
                <span className="gf-student-profile__id-tag">
                  Student Code: <code>{profile?.student_id || 'STU-CANONICAL'}</code>
                </span>
                <span className="gf-student-profile__id-tag">
                  Account ID: <code>{user?.id ? user.id.slice(0, 8) + '...' : '--'}</code>
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Details or Edit Form */}
      {isEditing ? (
        <Card variant="bordered" className="gf-student-profile__edit-card">
          <CardHeader>
            <CardTitle as="h3">Edit Learning Context</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSave} className="gf-student-profile__form">
              {saveError && (
                <div className="gf-student-profile__alert gf-student-profile__alert--error" role="alert">
                  {saveError}
                </div>
              )}

              <div className="gf-student-profile__form-group">
                <label htmlFor="student-bio" className="gf-student-profile__label">
                  Biography
                </label>
                <textarea
                  id="student-bio"
                  rows={3}
                  className="gf-student-profile__textarea"
                  placeholder="Tell your mentors and team about yourself..."
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  maxLength={1000}
                />
              </div>

              <div className="gf-student-profile__form-group">
                <label htmlFor="student-goals" className="gf-student-profile__label">
                  Learning & Project Goals
                </label>
                <textarea
                  id="student-goals"
                  rows={3}
                  className="gf-student-profile__textarea"
                  placeholder="What skills or projects do you want to accomplish?"
                  value={goals}
                  onChange={(e) => setGoals(e.target.value)}
                  maxLength={1000}
                />
              </div>

              <div className="gf-student-profile__form-group">
                <label htmlFor="student-interests" className="gf-student-profile__label">
                  Technical Interests
                </label>
                <input
                  id="student-interests"
                  type="text"
                  className="gf-student-profile__input"
                  placeholder="e.g. Cloud Native, UI Systems, Machine Learning"
                  value={interests}
                  onChange={(e) => setInterests(e.target.value)}
                  maxLength={255}
                />
              </div>

              <div className="gf-student-profile__form-actions">
                <Button type="submit" variant="primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Profile'}
                </Button>
                <Button type="button" variant="secondary" onClick={() => setIsEditing(false)} disabled={saving}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : (
        <div className="gf-student-profile__grid">
          <Card variant="bordered" className="gf-student-profile__detail-card">
            <CardHeader>
              <CardTitle as="h3">Learning Goals</CardTitle>
            </CardHeader>
            <CardContent>
              {profile?.goals ? (
                <p className="gf-student-profile__text">{profile.goals}</p>
              ) : (
                <p className="gf-student-profile__placeholder-text">
                  No learning goals specified yet. Add goals to guide your mentor's guidance.
                </p>
              )}
            </CardContent>
          </Card>

          <Card variant="bordered" className="gf-student-profile__detail-card">
            <CardHeader>
              <CardTitle as="h3">Technical Interests</CardTitle>
            </CardHeader>
            <CardContent>
              {profile?.interests ? (
                <p className="gf-student-profile__text">{profile.interests}</p>
              ) : (
                <p className="gf-student-profile__placeholder-text">
                  No technical interests specified yet.
                </p>
              )}
            </CardContent>
          </Card>

          <Card variant="bordered" className="gf-student-profile__detail-card" style={{ gridColumn: '1 / -1' }}>
            <CardHeader>
              <CardTitle as="h3">Biography</CardTitle>
            </CardHeader>
            <CardContent>
              {profile?.bio ? (
                <p className="gf-student-profile__text">{profile.bio}</p>
              ) : (
                <p className="gf-student-profile__placeholder-text">
                  No biography provided yet.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
