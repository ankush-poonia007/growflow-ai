import type { ProjectResponse, ProjectOverviewResponse } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { getStageNumber, getHealthDisplay, formatDate } from '../utils';

interface CurrentWorkProps {
  project: ProjectResponse;
  overview?: ProjectOverviewResponse | null;
}

export function CurrentWork({ project, overview }: CurrentWorkProps) {
  const stageNumber = getStageNumber(project.current_phase);
  const healthMeta = getHealthDisplay(project.health);
  const progressPercent = Math.min(100, Math.max(0, project.progress_percentage || 0));

  // Determine days remaining display using backend-canonical days_remaining
  const daysRemaining = overview?.days_remaining;
  let deadlineSubtext: string | null = null;
  if (project.deadline) {
    if (daysRemaining !== null && daysRemaining !== undefined) {
      if (daysRemaining === 0) {
        deadlineSubtext = 'Deadline is today';
      } else if (daysRemaining === 1) {
        deadlineSubtext = '1 day remaining';
      } else {
        deadlineSubtext = `${daysRemaining} days remaining`;
      }
    }
  }

  // Extract real profile objective if present
  const objectiveText =
    overview?.profile?.objective?.trim() ||
    project.problem?.trim() ||
    null;

  // Real technologies from overview
  const technologies = overview?.technologies || [];

  return (
    <Card as="article" className="gf-dashboard__current-work" variant="bordered">
      <CardHeader className="gf-dashboard__current-work-header">
        <div className="gf-dashboard__current-work-title-area">
          <div className="gf-dashboard__current-work-eyebrow">
            <span>Stage {stageNumber} of 8</span>
            <span className="gf-dashboard__separator" aria-hidden="true">•</span>
            <span className="gf-dashboard__phase-pill">{project.current_phase}</span>
          </div>
          <CardTitle as="h2" className="gf-dashboard__project-name">
            {project.name}
          </CardTitle>
        </div>

        <div className="gf-dashboard__badges-row">
          {project.complexity && (
            <Badge variant="accent">
              {project.complexity}
            </Badge>
          )}
          {project.status && (
            <Badge variant="neutral">
              {project.status}
            </Badge>
          )}
          <Badge variant={healthMeta.variant} dot>
            {healthMeta.label}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="gf-dashboard__current-work-body">
        {/* Progress Section */}
        <div className="gf-dashboard__progress-section">
          <div className="gf-dashboard__progress-label-row">
            <span className="gf-dashboard__progress-label">Lifecycle Progress</span>
            <span className="gf-dashboard__progress-value">{progressPercent}%</span>
          </div>
          <div
            role="progressbar"
            aria-valuenow={progressPercent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Project progress"
            className="gf-dashboard__progress-track"
          >
            <div
              className="gf-dashboard__progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Primary Meta Grid */}
        <div className="gf-dashboard__meta-grid">
          <div className="gf-dashboard__meta-item">
            <span className="gf-dashboard__meta-label">Target Deadline</span>
            <span className="gf-dashboard__meta-value">
              {formatDate(project.deadline)}
            </span>
            {deadlineSubtext && (
              <span className="gf-dashboard__meta-hint">{deadlineSubtext}</span>
            )}
          </div>

          <div className="gf-dashboard__meta-item">
            <span className="gf-dashboard__meta-label">Project Health</span>
            <span className="gf-dashboard__meta-value gf-dashboard__meta-health">
              {healthMeta.label}
            </span>
            <span className="gf-dashboard__meta-hint">{healthMeta.description}</span>
          </div>
        </div>

        {/* Real Profile Objective / Scope Snippet if populated */}
        {objectiveText && (
          <div className="gf-dashboard__objective-callout">
            <span className="gf-dashboard__objective-label">Project Objective</span>
            <p className="gf-dashboard__objective-text">{objectiveText}</p>
          </div>
        )}

        {/* Real Technologies if populated */}
        {technologies.length > 0 && (
          <div className="gf-dashboard__tech-stack">
            <span className="gf-dashboard__tech-label">Technologies</span>
            <div className="gf-dashboard__tech-pills">
              {technologies.map((t) => (
                <span key={t.id} className="gf-dashboard__tech-tag">
                  {t.technology_id}
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="gf-dashboard__current-work-footer">
        <Button as="link" to={`/student/projects/${project.id}`} variant="primary">
          View Project Profile →
        </Button>
        <Button as="link" to="/student/projects" variant="secondary">
          Open in Project Workspace →
        </Button>
      </CardFooter>
    </Card>
  );
}
