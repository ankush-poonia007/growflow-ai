import { type ReactNode } from 'react';
import { Button } from '@/components/ui/Button';
import './SystemStates.css';

export interface AIServiceUnavailableNoticeProps {
  serviceName?: string;
  reason?: string;
  deterministicAvailable?: boolean;
  action?: ReactNode;
  onRetry?: () => void;
  compact?: boolean;
  className?: string;
}

/**
 * SYS07 — AI Service Unavailable System State Component.
 *
 * Requirements:
 * - Clearly indicates that AI capability is temporarily unavailable or in standby
 * - Explicitly communicates that deterministic core workspace operations remain usable
 * - Never discloses provider keys, secrets, or internal model telemetry
 * - Supports optional contextual retry or action without making rogue backend calls
 */
export function AIServiceUnavailableNotice({
  serviceName,
  reason,
  deterministicAvailable = true,
  action,
  onRetry,
  compact = false,
  className = '',
}: AIServiceUnavailableNoticeProps) {
  const title = serviceName
    ? `${serviceName} Temporarily Unavailable`
    : 'AI Service Temporarily Unavailable';

  return (
    <div
      className={`gf-system-card ${compact ? 'gf-system-card--compact' : ''} ${className}`.trim()}
      role="region"
      aria-label="AI Service Notice"
    >
      <span className="gf-system-badge gf-system-badge--ai">
        AI Service Notice
      </span>

      <h2 className="gf-system-title">{title}</h2>

      <p className="gf-system-desc">
        AI-assisted intelligence capabilities are currently in standby or temporarily degraded.
      </p>

      {reason && (
        <p className="gf-system-desc" style={{ fontStyle: 'italic' }}>
          {reason}
        </p>
      )}

      {deterministicAvailable && (
        <div className="gf-system-note">
          <strong>Deterministic Workspace Active:</strong> Core workspace features including
          task tracking, milestone reviews, documentation, and repository synchronization remain
          fully operational while AI models are offline.
        </div>
      )}

      {(action || onRetry) && (
        <div className="gf-system-actions">
          {action}
          {onRetry && (
            <Button variant="secondary" onClick={onRetry}>
              Check AI Availability
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
