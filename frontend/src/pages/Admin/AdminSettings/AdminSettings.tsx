import { useState, useEffect, useCallback, useRef } from 'react';
import { getUserPreferences, updateUserPreferences } from '@/lib/api/client';
import type { UserPreferencesResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { InlineErrorState } from '@/components/ui/InlineErrorState';
import './AdminSettings.css';

const TIMEZONE_OPTIONS = [
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
  { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
  { value: 'America/Chicago', label: 'Central Time (US & Canada)' },
  { value: 'America/Denver', label: 'Mountain Time (US & Canada)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (US & Canada)' },
  { value: 'Europe/London', label: 'London / GMT' },
  { value: 'Europe/Paris', label: 'Central European Time' },
  { value: 'Asia/Kolkata', label: 'India Standard Time (IST)' },
  { value: 'Asia/Singapore', label: 'Singapore Standard Time' },
  { value: 'Asia/Tokyo', label: 'Japan Standard Time' },
  { value: 'Australia/Sydney', label: 'Sydney / AEST' },
];

/**
 * AdminSettings — Configuration view for Platform Administrators.
 */
export function AdminSettings() {
  const [, setPreferences] = useState<UserPreferencesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [timezone, setTimezone] = useState('UTC');
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
      setCompactView(Boolean(prefs.compact_view));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve admin preferences.';
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
      }, 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update preferences.';
      setSaveError(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="gf-admin-settings">
      <PageHeader
        eyebrow="PLATFORM GOVERNANCE CONFIGURATION"
        title="Admin Settings"
        description="Configure governance notifications, display density, and operational preferences."
      />

      {error && (
        <div style={{ marginBottom: '1.5rem' }}>
          <InlineErrorState error={error} onRetry={loadPrefs} />
        </div>
      )}

      {saveSuccess && (
        <div className="gf-admin-settings__alert gf-admin-settings__alert--success" role="status">
          Governance preferences saved successfully.
        </div>
      )}

      {saveError && (
        <div className="gf-admin-settings__alert gf-admin-settings__alert--error" role="alert">
          {saveError}
        </div>
      )}

      {loading ? (
        <div className="gf-admin-settings__skeleton-container">
          <Skeleton height="160px" />
          <Skeleton height="160px" />
        </div>
      ) : (
        <form onSubmit={handleSave} className="gf-admin-settings__form">
          <Card>
            <CardHeader>
              <CardTitle>Governance Notifications</CardTitle>
              <CardDescription>Configure alerts for platform anomalies and critical project risks.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="gf-admin-settings__field-group">
                <label className="gf-admin-settings__toggle-label">
                  <input
                    type="checkbox"
                    checked={emailNotifications}
                    onChange={(e) => setEmailNotifications(e.target.checked)}
                    className="gf-admin-settings__checkbox"
                  />
                  <div>
                    <strong>System &amp; Risk Notifications</strong>
                    <p>Receive email notifications for at-risk project escalations.</p>
                  </div>
                </label>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Regional &amp; Display Preferences</CardTitle>
              <CardDescription>Adjust audit log timestamp timezones and interface density.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="gf-admin-settings__field-group">
                <div className="gf-admin-settings__field">
                  <label htmlFor="timezone-select" className="gf-admin-settings__label">
                    Audit Timezone
                  </label>
                  <select
                    id="timezone-select"
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="gf-admin-settings__select"
                  >
                    {TIMEZONE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <label className="gf-admin-settings__toggle-label">
                  <input
                    type="checkbox"
                    checked={compactView}
                    onChange={(e) => setCompactView(e.target.checked)}
                    className="gf-admin-settings__checkbox"
                  />
                  <div>
                    <strong>Compact Directory View</strong>
                    <p>Display denser table rows in mentor and student directories.</p>
                  </div>
                </label>
              </div>
            </CardContent>
          </Card>

          <div className="gf-admin-settings__actions">
            <Button type="submit" variant="primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Settings'}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}
