import type { ProjectProfileData } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface ProjectObjectiveSectionProps {
  profile?: ProjectProfileData | null;
}

export function ProjectObjectiveSection({ profile }: ProjectObjectiveSectionProps) {
  if (!profile) return null;

  const hasContent = Boolean(
    profile.objective?.trim() ||
      profile.scope?.trim() ||
      profile.target_users?.trim() ||
      profile.expected_outcome?.trim() ||
      profile.constraints?.trim() ||
      profile.assumptions?.trim()
  );

  if (!hasContent) return null;

  return (
    <Card as="section" className="gf-profile-section" variant="bordered" aria-label="Project Objectives & Scope">
      <CardHeader className="gf-profile-section__header">
        <CardTitle as="h2" className="gf-profile-section__title">
          Objectives, Requirements & Boundaries
        </CardTitle>
        <p className="gf-profile-section__subtitle">
          Authoritative profile objectives and constraints registered on this project instance.
        </p>
      </CardHeader>

      <CardContent className="gf-profile-section__body">
        <div className="gf-profile-objectives-grid">
          {profile.objective?.trim() && (
            <div className="gf-profile-field-card gf-profile-field-card--full">
              <h3 className="gf-profile-field-label">Core Objective</h3>
              <p className="gf-profile-field-value gf-profile-field-value--prose">
                {profile.objective}
              </p>
            </div>
          )}

          {profile.scope?.trim() && (
            <div className="gf-profile-field-card gf-profile-field-card--full">
              <h3 className="gf-profile-field-label">Defined Scope</h3>
              <p className="gf-profile-field-value gf-profile-field-value--prose">
                {profile.scope}
              </p>
            </div>
          )}

          {profile.expected_outcome?.trim() && (
            <div className="gf-profile-field-card gf-profile-field-card--full">
              <h3 className="gf-profile-field-label">Expected Outcome</h3>
              <p className="gf-profile-field-value gf-profile-field-value--prose">
                {profile.expected_outcome}
              </p>
            </div>
          )}

          {profile.target_users?.trim() && (
            <div className="gf-profile-field-card">
              <h3 className="gf-profile-field-label">Target Users</h3>
              <p className="gf-profile-field-value">
                {profile.target_users}
              </p>
            </div>
          )}

          {profile.constraints?.trim() && (
            <div className="gf-profile-field-card">
              <h3 className="gf-profile-field-label">Project Constraints</h3>
              <p className="gf-profile-field-value gf-profile-field-value--prose">
                {profile.constraints}
              </p>
            </div>
          )}

          {profile.assumptions?.trim() && (
            <div className="gf-profile-field-card">
              <h3 className="gf-profile-field-label">Assumptions</h3>
              <p className="gf-profile-field-value gf-profile-field-value--prose">
                {profile.assumptions}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
