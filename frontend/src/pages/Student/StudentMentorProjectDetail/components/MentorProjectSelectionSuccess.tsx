import { Link } from 'react-router';
import type { ProjectResponse } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

interface MentorProjectSelectionSuccessProps {
  project: ProjectResponse;
}

export function MentorProjectSelectionSuccess({ project }: MentorProjectSelectionSuccessProps) {
  return (
    <div className="gf-detail-success-container">
      <Card as="article" className="gf-detail-success-card" variant="bordered" aria-live="polite">
        <CardHeader className="gf-detail-success-card__header">
          <div className="gf-detail-success-card__icon-wrap" aria-hidden="true">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="28"
              height="28"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <CardTitle as="h2" className="gf-detail-success-card__title">
            Project Created Successfully!
          </CardTitle>
          <p className="gf-detail-success-card__subtitle">
            This mentor project has been added to your active student portfolio.
          </p>
        </CardHeader>

        <CardContent className="gf-detail-success-card__content">
          <div className="gf-detail-success-card__details-panel">
            <h3 className="gf-detail-success-card__details-heading">Created Project Summary</h3>
            <dl className="gf-detail-success-card__dl">
              <div className="gf-detail-success-card__row">
                <dt className="gf-detail-success-card__dt">Project Name</dt>
                <dd className="gf-detail-success-card__dd gf-detail-success-card__dd--highlight">
                  {project.name}
                </dd>
              </div>

              <div className="gf-detail-success-card__row">
                <dt className="gf-detail-success-card__dt">Project ID</dt>
                <dd className="gf-detail-success-card__dd gf-detail-success-card__dd--mono">
                  {project.id}
                </dd>
              </div>

              <div className="gf-detail-success-card__row">
                <dt className="gf-detail-success-card__dt">Current Phase</dt>
                <dd className="gf-detail-success-card__dd">
                  <Badge variant="info">{project.current_phase}</Badge>
                </dd>
              </div>

              <div className="gf-detail-success-card__row">
                <dt className="gf-detail-success-card__dt">Initial Health</dt>
                <dd className="gf-detail-success-card__dd">
                  <Badge variant="success">{project.health}</Badge>
                </dd>
              </div>

              <div className="gf-detail-success-card__row">
                <dt className="gf-detail-success-card__dt">Initial Progress</dt>
                <dd className="gf-detail-success-card__dd">
                  <span className="gf-detail-success-card__progress-pill">
                    {project.progress_percentage}%
                  </span>
                </dd>
              </div>

              {project.status && (
                <div className="gf-detail-success-card__row">
                  <dt className="gf-detail-success-card__dt">Instance Status</dt>
                  <dd className="gf-detail-success-card__dd">
                    <Badge variant="neutral">{project.status}</Badge>
                  </dd>
                </div>
              )}
            </dl>
          </div>

          <div className="gf-detail-success-card__scope-note" role="note">
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
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
            <p>
              Your project instance is initialized and added to your portfolio.
            </p>
          </div>
        </CardContent>

        <CardFooter className="gf-detail-success-card__footer">
          <Link
            to={`/student/projects/${project.id}`}
            className="gf-btn gf-btn--primary gf-detail-success-card__action"
          >
            View Project Profile
          </Link>
          <Link
            to="/student/projects"
            className="gf-btn gf-btn--secondary gf-detail-success-card__action"
          >
            View in My Projects
          </Link>
          <Link
            to="/student/projects/mentor-catalog"
            className="gf-btn gf-btn--outline gf-detail-success-card__action"
          >
            Browse More Mentor Projects
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
