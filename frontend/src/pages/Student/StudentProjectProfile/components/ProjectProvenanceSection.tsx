import type { ProjectResponse, ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface ProjectProvenanceSectionProps {
  project: ProjectResponse;
  mentorDefinition?: ProjectDefinitionCatalogItem | null;
}

export function ProjectProvenanceSection({
  project,
  mentorDefinition,
}: ProjectProvenanceSectionProps) {
  const isMentorProject = Boolean(project.project_definition_id);

  return (
    <Card
      as="section"
      className="gf-profile-section gf-profile-section--provenance"
      variant="bordered"
      aria-label="Project Provenance"
    >
      <CardHeader className="gf-profile-section__header">
        <div className="gf-profile-provenance-badge-wrap">
          <span
            className={`gf-profile-provenance-tag ${
              isMentorProject
                ? 'gf-profile-provenance-tag--mentor'
                : 'gf-profile-provenance-tag--independent'
            }`}
          >
            {isMentorProject ? 'Mentor Project' : 'Independent Project'}
          </span>
        </div>
        <CardTitle as="h2" className="gf-profile-section__title">
          Origin & Provenance
        </CardTitle>
        <p className="gf-profile-section__subtitle">
          Authoritative source attribution and instance isolation context.
        </p>
      </CardHeader>

      <CardContent className="gf-profile-section__body">
        {isMentorProject ? (
          <div className="gf-profile-provenance-card">
            <div className="gf-profile-provenance-info">
              <h3 className="gf-profile-provenance-source-title">
                {mentorDefinition?.name || 'Assigned Mentor Project Definition'}
              </h3>
              {mentorDefinition?.version_number !== null &&
                mentorDefinition?.version_number !== undefined && (
                  <p className="gf-profile-provenance-version">
                    Pinned to Version Snapshot #{mentorDefinition.version_number}
                  </p>
                )}
            </div>

            <div className="gf-profile-provenance-immutability-notice" role="note">
              <div className="gf-profile-provenance-notice-icon" aria-hidden="true">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </div>
              <div className="gf-profile-provenance-notice-text">
                <strong>Immutable Baseline & Instance Isolation:</strong> This student project is
                derived from a mentor-approved specification. Any customizations, information updates,
                and milestone executions apply exclusively to your project instance. The original
                mentor definition remains strictly immutable.
              </div>
            </div>
          </div>
        ) : (
          <div className="gf-profile-provenance-card">
            <div className="gf-profile-provenance-info">
              <h3 className="gf-profile-provenance-source-title">
                Independent Student-Initiated Project
              </h3>
              <p className="gf-profile-provenance-version">
                Self-Directed Architecture & Scope
              </p>
            </div>

            <div className="gf-profile-provenance-immutability-notice" role="note">
              <div className="gf-profile-provenance-notice-icon" aria-hidden="true">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="12" cy="12" r="10" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
              </div>
              <div className="gf-profile-provenance-notice-text">
                <strong>Autonomous Student Ownership:</strong> You initiated this project independently.
                You retain full creative and technical authority over its problem formulation,
                solution architecture, and tool selections.
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
