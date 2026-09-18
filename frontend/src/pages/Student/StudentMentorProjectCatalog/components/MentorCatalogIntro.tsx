import { PageHeader } from '@/components/ui/PageHeader';

export function MentorCatalogIntro() {
  return (
    <div className="gf-mentor-catalog__intro">
      <PageHeader
        eyebrow="STUDENT / BUILD"
        title="Mentor Projects"
        description="Explore project ideas defined by mentors and find a direction that fits what you want to build."
      />
      <div className="gf-mentor-catalog__context-banner" role="note">
        <div className="gf-mentor-catalog__context-icon" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="18"
            height="18"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
        </div>
        <p className="gf-mentor-catalog__context-text">
          These projects are mentor-defined starting points. Choosing one will become a separate
          student project in the next step.
        </p>
      </div>
    </div>
  );
}
