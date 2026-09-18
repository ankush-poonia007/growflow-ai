import { EmptyState } from '@/components/ui/EmptyState';
import { Button } from '@/components/ui/Button';

export function DashboardEmptyState() {
  return (
    <div className="gf-dashboard__empty-container">
      <EmptyState
        title="You have no projects yet."
        description="Start with an idea and turn it into something you can build."
        icon={
          <svg
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M2 7a2 2 0 0 1 2-2h4l2 2h10a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2Z" />
            <path d="M12 11v6" />
            <path d="M9 14h6" />
          </svg>
        }
        action={
          <Button as="link" to="/student/projects/new" variant="primary">
            Create your first project
          </Button>
        }
      />
    </div>
  );
}
