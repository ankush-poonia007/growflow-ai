import type { ProjectResponse } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { getStageNumber, getHealthDisplay } from '../utils';

interface SecondaryProjectsProps {
  projects: ProjectResponse[];
  selectedProjectId: string;
  onSelectProject: (projectId: string) => void;
}

export function SecondaryProjects({
  projects,
  selectedProjectId,
  onSelectProject,
}: SecondaryProjectsProps) {
  if (projects.length <= 1) return null;

  return (
    <Card as="section" className="gf-dashboard__secondary-projects" variant="bordered">
      <CardHeader className="gf-dashboard__secondary-header">
        <div>
          <span className="gf-dashboard__section-eyebrow">PORTFOLIO OVERVIEW</span>
          <CardTitle as="h3" className="gf-dashboard__section-title">
            All Student Projects ({projects.length})
          </CardTitle>
        </div>
        <Button as="link" to="/student/projects" variant="secondary">
          Manage Projects →
        </Button>
      </CardHeader>

      <CardContent>
        <div className="gf-dashboard__projects-list" role="list">
          {projects.map((proj) => {
            const isCurrent = proj.id === selectedProjectId;
            const healthMeta = getHealthDisplay(proj.health);
            const stageNum = getStageNumber(proj.current_phase);

            return (
              <div
                key={proj.id}
                role="listitem"
                className={`gf-dashboard__project-row ${
                  isCurrent ? 'gf-dashboard__project-row--active' : ''
                }`}
              >
                <div className="gf-dashboard__project-row-main">
                  <div className="gf-dashboard__project-row-title-row">
                    <span className="gf-dashboard__project-row-name">{proj.name}</span>
                    {isCurrent && (
                      <span className="gf-dashboard__project-row-current-tag">Active Context</span>
                    )}
                  </div>
                  <div className="gf-dashboard__project-row-meta">
                    <span className="gf-dashboard__project-row-stage">
                      Stage {stageNum} of 8 ({proj.current_phase})
                    </span>
                    <span className="gf-dashboard__separator" aria-hidden="true">•</span>
                    <Badge variant={healthMeta.variant} dot>
                      {healthMeta.label}
                    </Badge>
                    <span className="gf-dashboard__separator" aria-hidden="true">•</span>
                    <span className="gf-dashboard__project-row-progress">
                      {proj.progress_percentage}% Complete
                    </span>
                  </div>
                </div>

                <div className="gf-dashboard__project-row-actions">
                  {!isCurrent ? (
                    <Button
                      as="button"
                      variant="tertiary"
                      onClick={() => onSelectProject(proj.id)}
                      aria-label={`View ${proj.name} overview in dashboard`}
                    >
                      Focus in Dashboard
                    </Button>
                  ) : (
                    <Button as="link" to="/student/projects" variant="tertiary">
                      Open Project
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
