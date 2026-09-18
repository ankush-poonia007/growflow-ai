import { useAuth } from '@/auth/useAuth';
import { Button } from '@/components/ui/Button';
import { getStudentGreeting } from '../utils';

interface DashboardWelcomeProps {
  projectCount?: number;
}

export function DashboardWelcome({ projectCount = 0 }: DashboardWelcomeProps) {
  const { user } = useAuth();
  const greeting = getStudentGreeting(user?.fullName, user?.email);

  return (
    <section className="gf-dashboard__welcome" aria-labelledby="dashboard-heading">
      <div className="gf-dashboard__welcome-header">
        <div className="gf-dashboard__welcome-text">
          <span className="gf-dashboard__eyebrow">BUILD / STUDENT</span>
          <h1 id="dashboard-heading" className="gf-dashboard__heading">
            {greeting}
          </h1>
          <p className="gf-dashboard__subheading">
            Your primary build control surface — monitor project lifecycle progression, verify health
            indicators, and follow deterministic next actions.
          </p>
        </div>

        {projectCount > 0 && (
          <div className="gf-dashboard__welcome-actions">
            <Button as="link" to="/student/projects" variant="secondary">
              View All Projects
            </Button>
            <Button as="link" to="/student/projects/new" variant="primary">
              Create Project
            </Button>
          </div>
        )}
      </div>
    </section>
  );
}
