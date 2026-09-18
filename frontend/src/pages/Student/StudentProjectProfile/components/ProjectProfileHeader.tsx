import { Link } from 'react-router';
import type { ProjectResponse, AssessmentSessionStatus } from '@/lib/api/types';
import type { PageMode } from '../types';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { getStageNumber, getHealthDisplay } from '../utils';

interface ProjectProfileHeaderProps {
  project: ProjectResponse;
  mode: PageMode;
  onEnterEditMode: () => void;
  onCancelEditMode: () => void;
  assessmentStatus?: AssessmentSessionStatus | null;
}

export function ProjectProfileHeader({
  project,
  mode,
  onEnterEditMode,
  onCancelEditMode,
  assessmentStatus,
}: ProjectProfileHeaderProps) {
  const stageNumber = getStageNumber(project.current_phase);
  const healthMeta = getHealthDisplay(project.health);
  const isMentorDefined = Boolean(project.project_definition_id);
  const provenanceLabel = isMentorDefined ? 'Mentor Project' : 'Independent Project';

  return (
    <header className="gf-profile-header" aria-label="Project Profile Header">
      {/* Breadcrumb Navigation */}
      <nav className="gf-profile-header__nav" aria-label="Breadcrumbs">
        <Link to="/student/projects" className="gf-profile-header__breadcrumb-link">
          ← Back to Projects
        </Link>
        <span className="gf-profile-header__nav-separator" aria-hidden="true">
          /
        </span>
        <span className="gf-profile-header__nav-current" aria-current="page">
          {project.name}
        </span>
      </nav>

      {/* Main Title & Provenance Eyebrow */}
      <div className="gf-profile-header__main">
        <div className="gf-profile-header__title-area">
          <div className="gf-profile-header__eyebrow-row">
            <span
              className={`gf-profile-header__provenance-badge ${
                isMentorDefined
                  ? 'gf-profile-header__provenance-badge--mentor'
                  : 'gf-profile-header__provenance-badge--independent'
              }`}
            >
              {provenanceLabel}
            </span>
            <span className="gf-profile-header__dot-separator" aria-hidden="true">
              •
            </span>
            <span className="gf-profile-header__stage-info">
              Stage {stageNumber} of 8 ({project.current_phase})
            </span>
          </div>

          <h1 className="gf-profile-header__title">{project.name}</h1>
        </div>

        {/* Action Controls */}
        <div className="gf-profile-header__actions">
          {mode === 'VIEW' ? (
            <>
              <Button
                as="link"
                to={`/student/projects/${project.id}/assessment`}
                variant="primary"
                size="md"
                id="project-profile-assessment-cta"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="m9 11 3 3L22 4" />
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                </svg>
                {assessmentStatus?.status === 'COMPLETED'
                  ? 'View Assessment Results'
                  : assessmentStatus?.status === 'IN_PROGRESS'
                  ? 'Continue Assessment'
                  : 'Start Assessment'}
              </Button>
              <Button
                as="button"
                variant="secondary"
                size="md"
                onClick={onEnterEditMode}
                className="gf-profile-header__edit-btn"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                  <path d="m15 5 4 4" />
                </svg>
                Edit Information
              </Button>
            </>
          ) : (
            <Button
              as="button"
              variant="tertiary"
              size="md"
              onClick={onCancelEditMode}
            >
              Cancel Edit
            </Button>
          )}
        </div>
      </div>

      {/* Badges Strip */}
      <div className="gf-profile-header__badges-row">
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
    </header>
  );
}
