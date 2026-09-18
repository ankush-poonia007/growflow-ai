import type { ProjectFormData } from '../types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CANONICAL_LIFECYCLE_STAGES } from '@/pages/Student/StudentDashboard/utils';

interface ProjectSnapshotProps {
  formData: ProjectFormData;
}

export function ProjectSnapshot({ formData }: ProjectSnapshotProps) {
  const hasContent = Boolean(
    formData.name.trim() ||
      formData.problem.trim() ||
      formData.proposedSolution.trim(),
  );

  const techList = formData.technologies
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean);

  return (
    <Card as="section" className="gf-project-snapshot" variant="bordered">
      <CardHeader className="gf-project-snapshot__header">
        <span className="gf-project-snapshot__eyebrow">PROJECT SNAPSHOT</span>
        <div className="gf-project-snapshot__title-row">
          <CardTitle as="h3" className="gf-project-snapshot__title">
            {formData.name.trim() || 'Untitled Project Idea'}
          </CardTitle>
          <Badge variant="accent">{formData.complexity}</Badge>
        </div>

        {!hasContent && (
          <p className="gf-project-snapshot__placeholder-hint">
            Your project snapshot will take shape as you define the idea.
          </p>
        )}
      </CardHeader>

      <CardContent className="gf-project-snapshot__body">
        {/* Problem Statement Preview */}
        <div className="gf-project-snapshot__section">
          <span className="gf-project-snapshot__label">Problem Statement</span>
          {formData.problem.trim() ? (
            <p className="gf-project-snapshot__text">{formData.problem.trim()}</p>
          ) : (
            <span className="gf-project-snapshot__muted">
              Explain the problem and who experiences it in the form.
            </span>
          )}
        </div>

        {/* Proposed Solution Preview */}
        <div className="gf-project-snapshot__section">
          <span className="gf-project-snapshot__label">Proposed Solution</span>
          {formData.proposedSolution.trim() ? (
            <p className="gf-project-snapshot__text">{formData.proposedSolution.trim()}</p>
          ) : (
            <span className="gf-project-snapshot__muted">
              Outline the technical approach you want to explore.
            </span>
          )}
        </div>

        {/* Technologies if specified */}
        {techList.length > 0 && (
          <div className="gf-project-snapshot__section">
            <span className="gf-project-snapshot__label">Technical Stack Direction</span>
            <div className="gf-project-snapshot__pills">
              {techList.map((tech) => (
                <span key={tech} className="gf-project-snapshot__tech-pill">
                  {tech}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Target Deadline if specified */}
        {formData.deadline && (
          <div className="gf-project-snapshot__section">
            <span className="gf-project-snapshot__label">Target Deadline</span>
            <span className="gf-project-snapshot__meta-val">{formData.deadline}</span>
          </div>
        )}

        {/* Informational Lifecycle Preview */}
        <div className="gf-project-snapshot__lifecycle">
          <span className="gf-project-snapshot__label">Build Lifecycle Path</span>
          <ol className="gf-project-snapshot__stages" aria-label="Planned lifecycle progression">
            {CANONICAL_LIFECYCLE_STAGES.map((s) => {
              const isInitial = s.phase === 'IDEA';
              const isNext = s.phase === 'ASSESSMENT';

              return (
                <li
                  key={s.phase}
                  className={`gf-project-snapshot__stage-node ${
                    isInitial
                      ? 'gf-project-snapshot__stage-node--current'
                      : isNext
                      ? 'gf-project-snapshot__stage-node--next'
                      : ''
                  }`}
                >
                  <span className="gf-project-snapshot__stage-num">{s.stage}</span>
                  <span className="gf-project-snapshot__stage-name">{s.label}</span>
                  {isInitial && <span className="gf-project-snapshot__stage-badge">Current</span>}
                  {isNext && <span className="gf-project-snapshot__stage-badge gf-project-snapshot__stage-badge--next">Next</span>}
                </li>
              );
            })}
          </ol>
          <p className="gf-project-snapshot__lifecycle-disclaimer">
            Informational roadmap cue. Build stages activate sequentially upon successful project creation.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
