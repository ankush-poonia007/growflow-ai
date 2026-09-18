import type { ProjectResponse, ProjectOverviewResponse } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { formatDate } from '../utils';

interface ProjectIdentitySectionProps {
  project: ProjectResponse;
  overview?: ProjectOverviewResponse | null;
}

export function ProjectIdentitySection({
  project,
  overview,
}: ProjectIdentitySectionProps) {
  const daysRemaining = overview?.days_remaining;

  return (
    <Card as="section" className="gf-profile-section" variant="bordered" aria-label="Project Identity">
      <CardHeader className="gf-profile-section__header">
        <CardTitle as="h2" className="gf-profile-section__title">
          Project Identity & Scope
        </CardTitle>
        <p className="gf-profile-section__subtitle">
          Core definition and problem formulation established for this project instance.
        </p>
      </CardHeader>

      <CardContent className="gf-profile-section__body">
        <div className="gf-profile-identity-grid">
          {/* Problem Statement */}
          <div className="gf-profile-field-card gf-profile-field-card--full">
            <h3 className="gf-profile-field-label">Problem Statement</h3>
            <p className="gf-profile-field-value gf-profile-field-value--prose">
              {project.problem?.trim() || (
                <span className="gf-profile-field-empty">No problem statement defined yet.</span>
              )}
            </p>
          </div>

          {/* Proposed Solution */}
          <div className="gf-profile-field-card gf-profile-field-card--full">
            <h3 className="gf-profile-field-label">Proposed Solution</h3>
            <p className="gf-profile-field-value gf-profile-field-value--prose">
              {project.proposed_solution?.trim() || (
                <span className="gf-profile-field-empty">No proposed solution formulated yet.</span>
              )}
            </p>
          </div>

          {/* Complexity Tier */}
          <div className="gf-profile-field-card">
            <h3 className="gf-profile-field-label">Target Complexity</h3>
            <p className="gf-profile-field-value gf-profile-field-value--highlight">
              {project.complexity || 'Intermediate'}
            </p>
            <span className="gf-profile-field-hint">
              {project.complexity === 'BEGINNER' && 'Focused scope with established patterns.'}
              {project.complexity === 'INTERMEDIATE' && 'Full-stack application with service integrations.'}
              {project.complexity === 'ADVANCED' && 'Distributed architecture or specialized algorithms.'}
              {!project.complexity && 'Standard project implementation scope.'}
            </span>
          </div>

          {/* Deadline & Days Remaining */}
          <div className="gf-profile-field-card">
            <h3 className="gf-profile-field-label">Target Deadline</h3>
            <p className="gf-profile-field-value gf-profile-field-value--date">
              {formatDate(project.deadline)}
            </p>
            {daysRemaining !== null && daysRemaining !== undefined && project.deadline && (
              <span className="gf-profile-field-hint">
                {daysRemaining === 0
                  ? 'Target completion date is today'
                  : daysRemaining === 1
                  ? '1 day remaining'
                  : `${daysRemaining} days remaining`}
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
