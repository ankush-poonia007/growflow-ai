import { Link } from 'react-router';
import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

interface MentorProjectCardProps {
  definition: ProjectDefinitionCatalogItem;
}

export function MentorProjectCard({ definition }: MentorProjectCardProps) {
  // Prefer description, fall back to problem
  const primaryText = definition.description || definition.problem;
  const showSecondaryProblem =
    Boolean(definition.description && definition.problem && definition.description !== definition.problem);

  return (
    <Card as="article" className="gf-mentor-card" variant="bordered">
      <CardHeader className="gf-mentor-card__header">
        <div className="gf-mentor-card__eyebrow-row">
          <Badge variant="info" className="gf-mentor-card__provenance-badge">
            MENTOR PROJECT
          </Badge>
          <div className="gf-mentor-card__badges-group">
            {definition.complexity && (
              <Badge variant="accent" className="gf-mentor-card__complexity-badge">
                {definition.complexity}
              </Badge>
            )}
            {definition.duration && (
              <span className="gf-mentor-card__duration-pill">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  width="13"
                  height="13"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="10" />
                  <polyline points="12 6 12 12 16 14" />
                </svg>
                <span>{definition.duration}</span>
              </span>
            )}
          </div>
        </div>

        <CardTitle as="h3" className="gf-mentor-card__title">
          <Link
            to={`/student/projects/mentor-catalog/${definition.id}`}
            className="gf-mentor-card__title-link"
          >
            {definition.name}
          </Link>
        </CardTitle>
      </CardHeader>

      <CardContent className="gf-mentor-card__content">
        {primaryText && (
          <p className="gf-mentor-card__description">{primaryText}</p>
        )}

        {showSecondaryProblem && definition.problem && (
          <div className="gf-mentor-card__section">
            <span className="gf-mentor-card__section-label">Core Problem</span>
            <p className="gf-mentor-card__section-text">{definition.problem}</p>
          </div>
        )}

        {definition.proposed_solution && (
          <div className="gf-mentor-card__section">
            <span className="gf-mentor-card__section-label">Proposed Direction</span>
            <p className="gf-mentor-card__section-text">{definition.proposed_solution}</p>
          </div>
        )}

        {/* Technologies Pills */}
        {definition.technology_snapshot && definition.technology_snapshot.length > 0 && (
          <div className="gf-mentor-card__tech-row" aria-label="Technologies used">
            {definition.technology_snapshot.map((tech, idx) => {
              const label = typeof tech === 'string' ? tech : String(tech?.name || tech?.title || '');
              if (!label) return null;
              return (
                <span key={`${label}-${idx}`} className="gf-mentor-card__tech-pill">
                  {label}
                </span>
              );
            })}
          </div>
        )}

        {/* Counts / indicators for constraints & assumptions */}
        {(Boolean(definition.constraints) || Boolean(definition.assumptions)) && (
          <div className="gf-mentor-card__meta-counts">
            {definition.constraints && (
              <span className="gf-mentor-card__meta-pill">
                Has constraints specified
              </span>
            )}
            {definition.assumptions && (
              <span className="gf-mentor-card__meta-pill">
                Has assumptions noted
              </span>
            )}
          </div>
        )}
      </CardContent>

      <CardFooter className="gf-mentor-card__footer">
        <Link
          to={`/student/projects/mentor-catalog/${definition.id}`}
          className="gf-mentor-card__view-link"
          aria-label={`View details and select ${definition.name}`}
        >
          <span>View Details &amp; Select</span>
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
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </Link>
      </CardFooter>
    </Card>
  );
}
