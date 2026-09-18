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
import './StudentSettings.css';

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

export function StudentSettingsPage() {
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
      <div className="gf-student-settings" id="student-settings-loading">
        <Skeleton width="220px" height="28px" style={{ marginBottom: '1rem' }} />
        <Skeleton width="100%" height="180px" style={{ borderRadius: '14px', marginBottom: '1.5rem' }} />
        <Skeleton width="100%" height="220px" style={{ borderRadius: '14px' }} />
      </div>
    );
  }

  return (
    <div className="gf-student-settings" id="student-settings-container">
      <PageHeader
        eyebrow="PREFERENCES"
        title="Workspace Settings"
        description="Notification preferences, regional timezone, and display options for your student workspace."
        badge={<Badge variant="neutral">BUILD SETTINGS</Badge>}
      />

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadPrefs} />
        </div>
      )}

      {saveSuccess && (
        <div className="gf-student-settings__alert gf-student-settings__alert--success" role="status">
          Settings saved successfully.
        </div>
      )}

      {saveError && (
        <div className="gf-student-settings__alert gf-student-settings__alert--error" role="alert">
          {saveError}
        </div>
      )}

      <form onSubmit={handleSave} className="gf-student-settings__form">
        {/* Notification Preferences */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Notifications</CardTitle>
            <CardDescription>
              Stay updated on mentor reviews, help request responses, and project updates.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-student-settings__card-content">
            <div className="gf-student-settings__toggle-row">
              <div className="gf-student-settings__toggle-meta">
                <span className="gf-student-settings__toggle-label">Email Notifications</span>
                <span className="gf-student-settings__toggle-desc">
                  Receive email alerts when mentors review your blueprints or answer help requests.
                </span>
              </div>
              <label className="gf-student-settings__switch">
                <input
                  type="checkbox"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  id="student-email-toggle"
                  aria-label="Email Notifications"
                />
                <span className="gf-student-settings__slider" />
              </label>
            </div>

            <div className="gf-student-settings__form-group">
              <label htmlFor="student-digest-frequency" className="gf-student-settings__label">
                Digest Frequency
              </label>
              <select
                id="student-digest-frequency"
                className="gf-student-settings__select"
                value={digestFrequency}
                onChange={(e) => setDigestFrequency(e.target.value)}
              >
                <option value="INSTANT">Instant (Real-time)</option>
                <option value="DAILY">Daily Digest</option>
                <option value="WEEKLY">Weekly Summary</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Regional & Localization */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Regional & Timezone</CardTitle>
            <CardDescription>
              Task deadlines and milestone due dates will be computed and displayed in this timezone.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-student-settings__card-content">
            <div className="gf-student-settings__form-group">
              <label htmlFor="student-timezone" className="gf-student-settings__label">
                Timezone
              </label>
              <select
                id="student-timezone"
                className="gf-student-settings__select"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
              >
                {TIMEZONE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Interface Density */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Display & Layout</CardTitle>
            <CardDescription>
              Personalize your task and milestone display density.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-student-settings__card-content">
            <div className="gf-student-settings__toggle-row">
              <div className="gf-student-settings__toggle-meta">
                <span className="gf-student-settings__toggle-label">Compact Task Cards</span>
                <span className="gf-student-settings__toggle-desc">
                  Reduce card padding in task and milestone boards.
                </span>
              </div>
              <label className="gf-student-settings__switch">
                <input
                  type="checkbox"
                  checked={compactView}
                  onChange={(e) => setCompactView(e.target.checked)}
                  id="student-compact-toggle"
                />
                <span className="gf-student-settings__slider" />
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Security & Session Information */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle as="h3">Security & Session</CardTitle>
            <CardDescription>
              Active authenticated student identity verified by GrowFlow session.
            </CardDescription>
          </CardHeader>
          <CardContent className="gf-student-settings__card-content">
            <div className="gf-student-settings__info-grid">
              <div>
                <span className="gf-student-settings__info-label">Email</span>
                <span className="gf-student-settings__info-val">{user?.email || '—'}</span>
              </div>
              <div>
                <span className="gf-student-settings__info-label">Role</span>
                <span className="gf-student-settings__info-val">{user?.role || 'STUDENT'}</span>
              </div>
              <div>
                <span className="gf-student-settings__info-label">Status</span>
                <span className="gf-student-settings__info-val">ACTIVE</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="gf-student-settings__actions">
          <Button type="submit" variant="primary" disabled={saving} id="save-student-settings-btn">
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </form>
    </div>
  );
}
