import { Link } from 'react-router';
import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { Badge } from '@/components/ui/Badge';

interface MentorProjectDetailHeaderProps {
  definition: ProjectDefinitionCatalogItem;
}

export function MentorProjectDetailHeader({ definition }: MentorProjectDetailHeaderProps) {
  return (
    <header className="gf-detail-header">
      {/* Top Navigation Row: Back Link & Breadcrumb */}
      <div className="gf-detail-header__nav-bar">
        <Link
          to="/student/projects/mentor-catalog"
          className="gf-detail-header__back-link"
          aria-label="Back to Mentor Projects"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="16"
            height="16"
            aria-hidden="true"
          >
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          <span>Back to Mentor Projects</span>
        </Link>

        <nav aria-label="Breadcrumb" className="gf-detail-header__breadcrumb">
          <ol className="gf-detail-header__breadcrumb-list">
            <li className="gf-detail-header__breadcrumb-item">
              <Link to="/student/projects/mentor-catalog">Mentor Projects</Link>
            </li>
            <li className="gf-detail-header__breadcrumb-separator" aria-hidden="true">
              /
            </li>
            <li className="gf-detail-header__breadcrumb-item gf-detail-header__breadcrumb-item--current" aria-current="page">
              Project Detail
            </li>
          </ol>
        </nav>
      </div>

      {/* Provenance & Badges */}
      <div className="gf-detail-header__badge-row">
        <Badge variant="info" className="gf-detail-header__provenance-badge">
          MENTOR PROJECT
        </Badge>
        {definition.complexity && (
          <Badge variant="accent" className="gf-detail-header__complexity-badge">
            {definition.complexity}
          </Badge>
        )}
        {definition.duration && (
          <span className="gf-detail-header__duration-pill">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="14"
              height="14"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            <span>{definition.duration}</span>
          </span>
        )}
      </div>

      {/* Project Title */}
      <h1 className="gf-detail-header__title">{definition.name}</h1>

      {/* Contextual Subtitle */}
      <p className="gf-detail-header__subtitle">
        Mentor-authored project definition available for student selection and implementation.
      </p>
    </header>
  );
}
