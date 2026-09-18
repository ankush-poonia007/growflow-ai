import type { ProjectResponse } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { getStageNumber, getHealthDisplay, formatDateTime } from '../utils';

interface ProjectSystemStateSectionProps {
  project: ProjectResponse;
}

export function ProjectSystemStateSection({ project }: ProjectSystemStateSectionProps) {
  const stageNumber = getStageNumber(project.current_phase);
  const healthMeta = getHealthDisplay(project.health);
  const progressPercent = Math.min(100, Math.max(0, project.progress_percentage || 0));

  return (
    <Card as="section" className="gf-profile-section gf-profile-section--system" variant="bordered" aria-label="System-Controlled Lifecycle State">
      <CardHeader className="gf-profile-section__header">
        <div className="gf-profile-system-badge-wrap">
          <Badge variant="neutral">System-Controlled Lifecycle</Badge>
        </div>
        <CardTitle as="h2" className="gf-profile-section__title">
          Operational & Lifecycle State
        </CardTitle>
        <p className="gf-profile-section__subtitle">
          These fields are maintained automatically by GrowFlow lifecycle gates and cannot be directly overwritten.
        </p>
      </CardHeader>

      <CardContent className="gf-profile-section__body">
        <div className="gf-profile-system-grid">
          {/* Lifecycle Phase */}
          <div className="gf-profile-system-item">
            <span className="gf-profile-system-label">Current Phase</span>
            <div className="gf-profile-system-value-row">
              <span className="gf-profile-system-value">
                Stage {stageNumber}: {project.current_phase}
              </span>
              <Badge variant="accent">Stage {stageNumber} of 8</Badge>
            </div>
            <span className="gf-profile-system-hint">
              Transitions sequentially through subsequent build gates (Assessment → Blueprint → Implementation).
            </span>
          </div>

          {/* Operational Status */}
          <div className="gf-profile-system-item">
            <span className="gf-profile-system-label">Operational Status</span>
            <div className="gf-profile-system-value-row">
              <span className="gf-profile-system-value">{project.status || 'Active'}</span>
              <Badge variant="neutral">{project.status || 'ACTIVE'}</Badge>
            </div>
            <span className="gf-profile-system-hint">
              Active project execution status.
            </span>
          </div>

          {/* Health Indicator */}
          <div className="gf-profile-system-item">
            <span className="gf-profile-system-label">Project Health</span>
            <div className="gf-profile-system-value-row">
              <span className="gf-profile-system-value">{healthMeta.label}</span>
              <Badge variant={healthMeta.variant} dot>
                {healthMeta.label}
              </Badge>
            </div>
            <span className="gf-profile-system-hint">{healthMeta.description}</span>
          </div>

          {/* Progress Percentage */}
          <div className="gf-profile-system-item">
            <span className="gf-profile-system-label">Progress</span>
            <div className="gf-profile-system-value-row">
              <span className="gf-profile-system-value">{progressPercent}%</span>
            </div>
            <div
              role="progressbar"
              aria-valuenow={progressPercent}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Lifecycle progress percentage"
              className="gf-profile-system-progress-track"
            >
              <div
                className="gf-profile-system-progress-fill"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* Timestamps */}
          <div className="gf-profile-system-item">
            <span className="gf-profile-system-label">Created At</span>
            <span className="gf-profile-system-value gf-profile-system-value--mono">
              {formatDateTime(project.created_at)}
            </span>
          </div>

          <div className="gf-profile-system-item">
            <span className="gf-profile-system-label">Last Updated</span>
            <span className="gf-profile-system-value gf-profile-system-value--mono">
              {formatDateTime(project.updated_at)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
