import type { ProjectResponse } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { getStageNumber, getHealthDisplay, formatDate } from '@/pages/Student/StudentDashboard/utils';

interface ProjectCardProps {
  project: ProjectResponse;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const stageNumber = getStageNumber(project.current_phase);
  const healthMeta = getHealthDisplay(project.health);
  const progressPercent = Math.min(100, Math.max(0, project.progress_percentage || 0));

  const isMentorDefined = Boolean(project.project_definition_id);
  const sourceLabel = isMentorDefined ? 'Mentor Project' : 'Independent Project';

  return (
    <Card as="article" className="gf-project-card" variant="bordered">
      <CardHeader className="gf-project-card__header">
        <div className="gf-project-card__title-area">
          <div className="gf-project-card__eyebrow-row">
            <span className="gf-project-card__source-tag">{sourceLabel}</span>
            <span className="gf-project-card__separator" aria-hidden="true">•</span>
            <span className="gf-project-card__stage-text">
              Stage {stageNumber} of 8 ({project.current_phase})
            </span>
          </div>

          <CardTitle as="h2" className="gf-project-card__title">
            {project.name}
          </CardTitle>
        </div>

        <div className="gf-project-card__badges-group">
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

      <CardContent className="gf-project-card__content">
        {/* Progress Section */}
        <div className="gf-project-card__progress-wrap">
          <div className="gf-project-card__progress-label-row">
            <span className="gf-project-card__progress-label">Lifecycle Progress</span>
            <span className="gf-project-card__progress-pct">{progressPercent}%</span>
          </div>
          <div
            role="progressbar"
            aria-valuenow={progressPercent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Project progress for ${project.name}`}
            className="gf-project-card__progress-track"
          >
            <div
              className="gf-project-card__progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Problem / Objective Snippet */}
        {(project.problem || project.proposed_solution) && (
          <p className="gf-project-card__snippet">
            {project.problem || project.proposed_solution}
          </p>
        )}

        {/* Meta Row: Deadline & Group context */}
        <div className="gf-project-card__meta-row">
          <div className="gf-project-card__meta-item">
            <span className="gf-project-card__meta-label">Deadline</span>
            <span className="gf-project-card__meta-val">
              {formatDate(project.deadline)}
            </span>
          </div>

          {project.group_id && (
            <div className="gf-project-card__meta-item">
              <span className="gf-project-card__meta-label">Team Context</span>
              <span className="gf-project-card__meta-val">Collaborative</span>
            </div>
          )}

          <div className="gf-project-card__meta-item">
            <span className="gf-project-card__meta-label">Health</span>
            <span className="gf-project-card__meta-val gf-project-card__meta-val--health">
              {healthMeta.label}
            </span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="gf-project-card__footer">
        <span className="gf-project-card__workspace-note">
          Stage {stageNumber} of 8 • {project.current_phase}
        </span>
        <div className="gf-project-card__footer-actions" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <Button as="link" to={`/student/projects/${project.id}/profile`} variant="secondary" size="sm">
            View Project Profile
          </Button>
          <Button as="link" to={`/student/projects/${project.id}/overview`} variant="primary" size="sm">
            Open Workspace →
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
