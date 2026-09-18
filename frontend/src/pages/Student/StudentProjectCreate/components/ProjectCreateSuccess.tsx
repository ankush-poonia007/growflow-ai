import type { ProjectResponse } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface ProjectCreateSuccessProps {
  project: ProjectResponse;
}

export function ProjectCreateSuccess({ project }: ProjectCreateSuccessProps) {
  return (
    <Card
      as="section"
      className="gf-project-create-success"
      variant="bordered"
      aria-label="Project Creation Success"
    >
      <CardHeader className="gf-project-create-success__header">
        <div className="gf-project-create-success__icon-wrap" aria-hidden="true">
          <svg
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </div>

        <div className="gf-project-create-success__title-wrap">
          <span className="gf-project-create-success__eyebrow">STAGE 1: IDEA INITIALIZED</span>
          <CardTitle as="h2" className="gf-project-create-success__title">
            Your project has been created.
          </CardTitle>
          <p className="gf-project-create-success__subtitle">
            <strong>{project.name}</strong> is now registered as an independent Student Project Instance.
          </p>
        </div>

        <div className="gf-project-create-success__badges">
          {project.complexity && <Badge variant="accent">{project.complexity}</Badge>}
          {project.status && <Badge variant="neutral">{project.status}</Badge>}
          <Badge variant="success" dot>Stage 1: {project.current_phase}</Badge>
        </div>
      </CardHeader>

      <CardContent className="gf-project-create-success__body">
        {/* Next Stage Guidance */}
        <div className="gf-project-create-success__guidance">
          <span className="gf-project-create-success__guidance-eyebrow">NEXT BUILD STAGE</span>
          <h3 className="gf-project-create-success__guidance-title">
            The next stage is Assessment.
          </h3>
          <p className="gf-project-create-success__guidance-text">
            Your project definition establishes the baseline for evaluation. In subsequent build gates,
            you will review technical requirements, complexity scope, and prerequisite dependencies
            prior to architectural blueprint generation.
          </p>
        </div>
      </CardContent>

      <CardFooter className="gf-project-create-success__footer">
        <Button as="link" to={`/student/projects/${project.id}`} variant="primary">
          View Project Profile
        </Button>
        <Button as="link" to="/student/projects" variant="secondary">
          View in Projects Collection
        </Button>
        <Button as="link" to="/student/dashboard" variant="tertiary">
          Go to Student Dashboard
        </Button>
      </CardFooter>
    </Card>
  );
}
