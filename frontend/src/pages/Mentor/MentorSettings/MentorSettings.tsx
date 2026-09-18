import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/auth/useAuth';
import { getUserPreferences, updateUserPreferences } from '@/lib/api/client';
import type { UserPreferencesResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './MentorSettings.css';

const TIMEZONE_OPTIONS = [
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
  { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
  { value: 'America/Chicago', label: 'Central Time (US & Canada)' },
  { value: 'America/Denver', label: 'Mountain Time (US & Canada)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (US & Canada)' },
  { value: 'Europe/London', label: 'London / GMT' },
  { value: 'Europe/Paris', label: 'Central European Time' },
  { value: 'Asia/Kolkata', label: 'India Standard Time (IST)' },
  { value: 'Asia/Singapore', label: 'Singapore / Hong Kong' },
  { value: 'Asia/Tokyo', label: 'Japan Standard Time' },
  { value: 'Australia/Sydney', label: 'Sydney / AEST' },
];

export function MentorSettings() {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<UserPreferencesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [timezone, setTimezone] = useState('UTC');
  const [digestFrequency, setDigestFrequency] = useState('DAILY');
  const [compactView, setCompactView] = useState(false);

  // Status
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadPrefs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getUserPreferences();
      setPreferences(data);
      setEmailNotifications(data.email_notifications ?? true);
      setTimezone(data.timezone || 'UTC');
      const prefs = (data.preferences || {}) as Record<string, unknown>;
      setDigestFrequency(typeof prefs.digest_frequency === 'string' ? prefs.digest_frequency : 'DAILY');
      setCompactView(Boolean(prefs.compact_view));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve user preferences.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPrefs();
  }, [loadPrefs]);

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

      const updated = await updateUserPreferences({
        email_notifications: emailNotifications,
        timezone,
        preferences: {
          ...(preferences?.preferences || {}),
          digest_frequency: digestFrequency,
          compact_view: compactView,
        },
      });

      setPreferences(updated);
      setSaveSuccess(true);
      if (feedbackTimerRef.current) {
        clearTimeout(feedbackTimerRef.current);
      }
      feedbackTimerRef.current = setTimeout(() => {
        setSaveSuccess(false);
        feedbackTimerRef.current = null;
      }, 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to save settings.';
      setSaveError(msg);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="gf-mentor-settings" id="mentor-settings-loading">
        <Skeleton width="220px" height="28px" style={{ marginBottom: '1rem' }} />
        <Skeleton width="100%" height="180px" style={{ borderRadius: '14px', marginBottom: '1.5rem' }} />
        <Skeleton width="100%" height="220px" style={{ borderRadius: '14px' }} />
      </div>
    );
  }

  return (
    <div className="gf-mentor-settings" id="mentor-settings-container">
      <PageHeader
        eyebrow="CONFIGURATION"
        title="Workspace Settings"
        description="Notification routing, regional timezone, and supervisory display preferences."
        badge={<Badge variant="neutral">PREFERENCES</Badge>}
      />

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadPrefs} />
        </div>
      )}

      {saveSuccess && (
        <div className="gf-mentor-settings__alert gf-mentor-settings__alert--success" role="status">
          Settings saved successfully.
        </div>
      )}

      {saveError && (
        <div className="gf-mentor-settings__alert gf-mentor-settings__alert--error" role="alert">
          {saveError}
        </div>
      )}

      <form onSubmit={handleSave} className="gf-mentor-settings__form">
        {/* Notification Preferences */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Notification Dispatch</CardTitle>
            <CardDescription>
              Control automated outbox domain alerts and student milestone dispatches.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-mentor-settings__card-content">
            <div className="gf-mentor-settings__toggle-row">
              <div className="gf-mentor-settings__toggle-meta">
                <span className="gf-mentor-settings__toggle-label">Email Notifications</span>
                <span className="gf-mentor-settings__toggle-desc">
                  Receive email alerts for critical student blockers and help request submissions.
                </span>
              </div>
              <label className="gf-mentor-settings__switch">
                <input
                  type="checkbox"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  id="email-notifications-toggle"
                  aria-label="Email Notifications"
                />
                <span className="gf-mentor-settings__slider" />
              </label>
            </div>

            <div className="gf-mentor-settings__form-group">
              <label htmlFor="digest-frequency" className="gf-mentor-settings__label">
                Cohort Activity Digest Frequency
              </label>
              <select
                id="digest-frequency"
                className="gf-mentor-settings__select"
                value={digestFrequency}
                onChange={(e) => setDigestFrequency(e.target.value)}
              >
                <option value="INSTANT">Instant (As events occur)</option>
                <option value="DAILY">Daily Summary Digest</option>
                <option value="WEEKLY">Weekly Supervision Overview</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Regional & Localization */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Regional & Timezone</CardTitle>
            <CardDescription>
              Timestamps for outbox events, milestone verification, and activity logs will display in this timezone.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-mentor-settings__card-content">
            <div className="gf-mentor-settings__form-group">
              <label htmlFor="mentor-timezone" className="gf-mentor-settings__label">
                System Timezone
              </label>
              <select
                id="mentor-timezone"
                className="gf-mentor-settings__select"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
              >
                {TIMEZONE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <span className="gf-mentor-settings__help-text">
                Current UTC offset is applied to all audit trail timestamps.
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Supervision Display */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Supervisory Workspace Display</CardTitle>
            <CardDescription>
              Adjust layout density across student directories and project instance tables.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-mentor-settings__card-content">
            <div className="gf-mentor-settings__toggle-row">
              <div className="gf-mentor-settings__toggle-meta">
                <span className="gf-mentor-settings__toggle-label">Compact Tables View</span>
                <span className="gf-mentor-settings__toggle-desc">
                  Increase row density for high-volume student rosters and cross-cohort queues.
                </span>
              </div>
              <label className="gf-mentor-settings__switch">
                <input
                  type="checkbox"
                  checked={compactView}
                  onChange={(e) => setCompactView(e.target.checked)}
                  id="compact-view-toggle"
                />
                <span className="gf-mentor-settings__slider" />
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Read-Only Identity & Session Info */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Security & Session</CardTitle>
            <CardDescription>
              Backend-authoritative identity verified by GrowFlow token.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-mentor-settings__card-content">
            <div className="gf-mentor-settings__info-grid">
              <div>
                <span className="gf-mentor-settings__info-label">Account Email</span>
                <span className="gf-mentor-settings__info-val">{user?.email || '—'}</span>
              </div>
              <div>
                <span className="gf-mentor-settings__info-label">Enforced Role</span>
                <span className="gf-mentor-settings__info-val">{user?.role || 'MENTOR'}</span>
              </div>
              <div>
                <span className="gf-mentor-settings__info-label">Account Status</span>
                <span className="gf-mentor-settings__info-val">ACTIVE</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="gf-mentor-settings__actions">
          <Button type="submit" variant="primary" disabled={saving} id="save-settings-btn">
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </form>
    </div>
  );
}
