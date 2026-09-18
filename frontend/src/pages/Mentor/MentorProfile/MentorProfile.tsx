import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/auth/useAuth';
import { getMentorProfile, updateMentorProfile } from '@/lib/api/client';
import type { MentorProfileResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './MentorProfile.css';

export function MentorProfile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<MentorProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Edit state
  const [isEditing, setIsEditing] = useState(false);
  const [bio, setBio] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMentorProfile();
      setProfile(data);
      setBio(data.bio || '');
      setSpecialization(data.specialization || '');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve mentor profile.';
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
      const updated = await updateMentorProfile({
        bio: bio.trim() || null,
        specialization: specialization.trim() || null,
      });
      setProfile(updated);
      setBio(updated.bio || '');
      setSpecialization(updated.specialization || '');
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
      const msg = err instanceof Error ? err.message : 'Failed to update profile.';
      setSaveError(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setBio(profile?.bio || '');
    setSpecialization(profile?.specialization || '');
    setSaveError(null);
    setIsEditing(false);
  };

  const displayName = user?.fullName?.trim() || user?.email?.trim() || '—';
  const initials = displayName !== '—'
    ? displayName
        .split(/\s+/)
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2)
    : 'ME';

  if (loading) {
    return (
      <div className="gf-mentor-profile" id="mentor-profile-loading">
        <Skeleton width="220px" height="28px" style={{ marginBottom: '1rem' }} />
        <Skeleton width="100%" height="160px" style={{ borderRadius: '14px', marginBottom: '1.5rem' }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
          <Skeleton height="200px" style={{ borderRadius: '14px' }} />
          <Skeleton height="200px" style={{ borderRadius: '14px' }} />
        </div>
      </div>
    );
  }

  return (
    <div className="gf-mentor-profile" id="mentor-profile-container">
      <PageHeader
        eyebrow="ACCOUNT & SUPERVISION"
        title="Mentor Profile"
        description="Canonical identity, domain specialization, and mentor supervision credentials."
        badge={<Badge variant="neutral">MENTOR SUPERVISOR</Badge>}
        actions={
          !isEditing && (
            <Button
              variant="secondary"
              onClick={() => setIsEditing(true)}
              id="edit-mentor-profile-btn"
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
        <div className="gf-mentor-profile__alert gf-mentor-profile__alert--success" role="status">
          Profile updated successfully.
        </div>
      )}

      {/* Primary Identity Card */}
      <Card variant="bordered" className="gf-mentor-profile__identity-card">
        <CardContent>
          <div className="gf-mentor-profile__identity-row">
            <div className="gf-mentor-profile__avatar">
              {user?.avatarUrl ? (
                <img src={user.avatarUrl} alt={displayName} className="gf-mentor-profile__avatar-img" />
              ) : (
                <span>{initials}</span>
              )}
            </div>
            <div className="gf-mentor-profile__identity-meta">
              <div className="gf-mentor-profile__name-row">
                <h2 className="gf-mentor-profile__display-name">{displayName}</h2>
                <Badge variant="warning">Mentor Account</Badge>
                <Badge variant="success">Active</Badge>
              </div>
              <p className="gf-mentor-profile__email">{user?.email}</p>
              <div className="gf-mentor-profile__id-tags">
                <span className="gf-mentor-profile__id-tag">
                  Mentor Code: <code>{profile?.mentor_id || 'MTR-CANONICAL'}</code>
                </span>
                <span className="gf-mentor-profile__id-tag">
                  Account ID: <code>{user?.id ? user.id.slice(0, 8) + '...' : '--'}</code>
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Details or Edit Form */}
      {isEditing ? (
        <Card variant="bordered" className="gf-mentor-profile__edit-card">
          <CardHeader>
            <CardTitle as="h3">Edit Supervision Context</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSave} className="gf-mentor-profile__form">
              {saveError && (
                <div className="gf-mentor-profile__alert gf-mentor-profile__alert--error" role="alert">
                  {saveError}
                </div>
              )}

              <div className="gf-mentor-profile__form-group">
                <label htmlFor="mentor-specialization" className="gf-mentor-profile__label">
                  Domain Specialization
                </label>
                <input
                  id="mentor-specialization"
                  type="text"
                  className="gf-mentor-profile__input"
                  placeholder="e.g. Distributed Systems, Enterprise Architecture, Machine Learning"
                  value={specialization}
                  onChange={(e) => setSpecialization(e.target.value)}
                  maxLength={255}
                />
                <span className="gf-mentor-profile__help-text">
                  Your primary engineering focus area for student portfolio matching.
                </span>
              </div>

              <div className="gf-mentor-profile__form-group">
                <label htmlFor="mentor-bio" className="gf-mentor-profile__label">
                  Professional Biography
                </label>
                <textarea
                  id="mentor-bio"
                  rows={4}
                  className="gf-mentor-profile__textarea"
                  placeholder="Describe your industry experience, supervisory background, and mentorship style..."
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  maxLength={1000}
                />
              </div>

              <div className="gf-mentor-profile__form-actions">
                <Button type="submit" variant="primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Profile'}
                </Button>
                <Button type="button" variant="secondary" onClick={handleCancel} disabled={saving}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : (
        <div className="gf-mentor-profile__grid">
          <Card variant="bordered" className="gf-mentor-profile__detail-card">
            <CardHeader>
              <CardTitle as="h3">Domain Specialization</CardTitle>
            </CardHeader>
            <CardContent>
              {profile?.specialization ? (
                <p className="gf-mentor-profile__text">{profile.specialization}</p>
              ) : (
                <p className="gf-mentor-profile__placeholder-text">
                  No domain specialization specified yet. Click "Edit Profile" to set your focus areas.
                </p>
              )}
            </CardContent>
          </Card>

          <Card variant="bordered" className="gf-mentor-profile__detail-card">
            <CardHeader>
              <CardTitle as="h3">Professional Biography</CardTitle>
            </CardHeader>
            <CardContent>
              {profile?.bio ? (
                <p className="gf-mentor-profile__text">{profile.bio}</p>
              ) : (
                <p className="gf-mentor-profile__placeholder-text">
                  No biography provided yet. Add a short summary of your background to help supervise cohort projects.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
