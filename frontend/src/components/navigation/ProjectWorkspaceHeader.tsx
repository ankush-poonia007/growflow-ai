import { NavLink } from 'react-router';
import { Badge } from '@/components/ui/Badge';
import { getStageNumber, getHealthDisplay } from '@/pages/Student/StudentDashboard/utils';
import './ProjectWorkspaceHeader.css';

interface ProjectWorkspaceHeaderProps {
  projectId: string;
  projectName: string;
  currentPhase: string;
  health: string;
  isMentorProject?: boolean;
}

export function ProjectWorkspaceHeader({
  projectId,
  projectName,
  currentPhase,
  health,
  isMentorProject = false,
}: ProjectWorkspaceHeaderProps) {
  const stageNumber = getStageNumber(currentPhase);
  const healthMeta = getHealthDisplay(health);
  const provenanceLabel = isMentorProject ? 'Mentor Project' : 'Independent Project';

  return (
    <header className="gf-workspace-header" aria-label={`Project workspace header for ${projectName}`}>
      <div className="gf-workspace-header__top-row">
        <NavLink
          to="/student/projects"
          className="gf-workspace-header__back-link"
          id="workspace-back-projects-btn"
        >
          <span aria-hidden="true">←</span> All Projects
        </NavLink>

        <div className="gf-workspace-header__badges">
          <Badge variant="neutral">
            {provenanceLabel}
          </Badge>
          <Badge variant="accent">
            Stage {stageNumber} of 8 • {currentPhase}
          </Badge>
          <Badge variant={healthMeta.variant} dot>
            {healthMeta.label}
          </Badge>
        </div>
      </div>

      <div className="gf-workspace-header__title-row">
        <h1 className="gf-workspace-header__title" id="workspace-project-title">
          {projectName}
        </h1>
      </div>

      <nav className="gf-workspace-header__nav" aria-label="Project Workspace Navigation">
        <ul className="gf-workspace-header__tabs" role="tablist">
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/overview`}
              role="tab"
              id="ws-nav-overview"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Overview
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/tasks`}
              role="tab"
              id="ws-nav-tasks"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Tasks
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/milestones`}
              role="tab"
              id="ws-nav-milestones"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Milestones
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/risks`}
              role="tab"
              id="ws-nav-risks"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Risks
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/roadmap`}
              role="tab"
              id="ws-nav-roadmap"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Roadmap
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/documents`}
              role="tab"
              id="ws-nav-documents"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Documents
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/github`}
              role="tab"
              id="ws-nav-github"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              GitHub
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/activity`}
              role="tab"
              id="ws-nav-activity"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Activity
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/ai-mentor`}
              role="tab"
              id="ws-nav-ai-mentor"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              AI Mentor
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/help-requests`}
              role="tab"
              id="ws-nav-help-requests"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Help Requests
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/mentor-feedback`}
              role="tab"
              id="ws-nav-mentor-feedback"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Mentor Feedback
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/changes`}
              role="tab"
              id="ws-nav-changes"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Changes
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/blueprint/workspace`}
              role="tab"
              id="ws-nav-blueprint"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Blueprint Workspace
            </NavLink>
          </li>
          <li role="presentation">
            <NavLink
              to={`/student/projects/${projectId}/profile`}
              role="tab"
              id="ws-nav-profile"
              className={({ isActive }) =>
                `gf-workspace-header__tab ${isActive ? 'gf-workspace-header__tab--active' : ''}`
              }
            >
              Project Profile
            </NavLink>
          </li>
        </ul>
      </nav>
    </header>
  );
}
