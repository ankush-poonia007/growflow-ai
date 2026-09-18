import { Button } from '@/components/ui/Button';

interface BlueprintPrerequisiteBlockProps {
  projectId: string;
}

export function BlueprintPrerequisiteBlock({ projectId }: BlueprintPrerequisiteBlockProps) {
  return (
    <div className="gf-blueprint-card gf-blueprint-prereq-card">
      <div className="gf-blueprint-prereq__icon-wrap">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          width="36"
          height="36"
          aria-hidden="true"
        >
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="M12 8v4M12 16h.01" />
        </svg>
      </div>

      <div className="gf-blueprint-prereq__content">
        <span className="gf-blueprint-badge-subtle">Prerequisite Required</span>
        <h2 className="gf-blueprint-card__title">Complete Stage 2 Assessment First</h2>
        <p className="gf-blueprint-card__desc">
          Stage 3 (Blueprint Generation) requires an authoritatively completed and locked Stage 2 Project Assessment.
          Your assessment results directly calibrate the architectural depth, complexity models, and technical requirements
          synthesized in your blueprint.
        </p>

        <div className="gf-blueprint-prereq__actions">
          <Button
            as="link"
            to={`/student/projects/${projectId}/assessment`}
            variant="primary"
            size="lg"
            id="go-to-assessment-btn"
          >
            Go to Project Assessment
          </Button>
          <Button
            as="link"
            to={`/student/projects/${projectId}/profile`}
            variant="secondary"
            size="lg"
          >
            Return to Project Profile
          </Button>
        </div>
      </div>
    </div>
  );
}
