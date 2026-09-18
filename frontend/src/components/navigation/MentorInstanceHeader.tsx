import React from 'react';
import { Link, useLocation } from 'react-router';
import { Badge } from '@/components/ui/Badge';
import type { MentorProjectInstanceDetail, MentorProjectInstanceSummary } from '@/lib/api/types';
import './MentorInstanceHeader.css';

interface MentorInstanceHeaderProps {
  project: MentorProjectInstanceDetail | MentorProjectInstanceSummary;
  activeTab?: 'overview' | 'blueprint' | 'tasks' | 'milestones' | 'risks' | 'documents' | 'github' | 'activity' | 'notes';
}

export const MentorInstanceHeader: React.FC<MentorInstanceHeaderProps> = ({
  project,
  activeTab,
}) => {
  const location = useLocation();

  // Determine current tab from activeTab prop or current pathname
  const currentTab =
    activeTab ||
    (() => {
      const path = location.pathname;
      if (path.endsWith('/blueprint')) return 'blueprint';
      if (path.endsWith('/tasks')) return 'tasks';
      if (path.endsWith('/milestones')) return 'milestones';
      if (path.endsWith('/risks')) return 'risks';
      if (path.endsWith('/documents')) return 'documents';
      if (path.endsWith('/github')) return 'github';
      if (path.endsWith('/activity')) return 'activity';
      if (path.endsWith('/notes')) return 'notes';
      return 'overview';
    })();

  const getHealthBadge = (health: string) => {
    switch (health) {
      case 'CRITICAL':
        return <Badge variant="danger">CRITICAL</Badge>;
      case 'WARNING':
        return <Badge variant="warning">WARNING</Badge>;
      case 'HEALTHY':
      default:
        return <Badge variant="success">HEALTHY</Badge>;
    }
  };

  const navItems = [
    { id: 'overview', label: 'Overview', to: `/mentor/project-instances/${project.id}` },
    { id: 'blueprint', label: 'Blueprint', to: `/mentor/project-instances/${project.id}/blueprint` },
    { id: 'tasks', label: 'Tasks', to: `/mentor/project-instances/${project.id}/tasks` },
    { id: 'milestones', label: 'Milestones', to: `/mentor/project-instances/${project.id}/milestones` },
    { id: 'risks', label: 'Risks', to: `/mentor/project-instances/${project.id}/risks` },
    { id: 'documents', label: 'Documents', to: `/mentor/project-instances/${project.id}/documents` },
    { id: 'github', label: 'GitHub', to: `/mentor/project-instances/${project.id}/github` },
    { id: 'activity', label: 'Activity', to: `/mentor/project-instances/${project.id}/activity` },
    { id: 'notes', label: 'Notes', to: `/mentor/project-instances/${project.id}/notes` },
  ];

  return (
    <header className="gf-mentor-instance-header" id="mentor-instance-header">
      <div className="gf-mentor-instance-header__top">
        <nav aria-label="Breadcrumb" className="gf-mentor-instance-header__breadcrumb">
          <Link to="/mentor/project-instances" className="gf-mentor-instance-header__back-link">
            ← All Project Instances
          </Link>
          <span className="gf-mentor-instance-header__breadcrumb-divider">/</span>
          <span className="gf-mentor-instance-header__breadcrumb-current">{project.name}</span>
        </nav>

        <div className="gf-mentor-instance-header__supervision-tag">
          <span className="gf-mentor-instance-header__tag-dot" />
          SUPERVISE • READ-ONLY
        </div>
      </div>

      <div className="gf-mentor-instance-header__hero">
        <div className="gf-mentor-instance-header__title-section">
          <h1 className="gf-mentor-instance-header__title" id="mentor-instance-title">
            {project.name}
          </h1>
          <div className="gf-mentor-instance-header__meta-row">
            <span className="gf-mentor-instance-header__student-pill">
              Student: <strong>{project.student_name}</strong> ({project.student_email})
            </span>
            <span className="gf-mentor-instance-header__meta-divider">•</span>
            <span className="gf-mentor-instance-header__group-pill">
              Cohort: <strong>{project.group_name || 'Individual'}</strong>
            </span>
            {project.source_definition_name && (
              <>
                <span className="gf-mentor-instance-header__meta-divider">•</span>
                <span className="gf-mentor-instance-header__version-pill" id="pinned-version-badge">
                  {project.source_definition_name} •{' '}
                  <strong className="gf-mentor-instance-header__version-highlight">
                    Pinned v{project.source_definition_version_number ?? 1}
                  </strong>
                </span>
              </>
            )}
          </div>
        </div>

        <div className="gf-mentor-instance-header__badges">
          <div className="gf-mentor-instance-header__badge-item">
            <span className="gf-mentor-instance-header__badge-label">Phase</span>
            <Badge variant="neutral">{project.current_phase}</Badge>
          </div>
          <div className="gf-mentor-instance-header__badge-item">
            <span className="gf-mentor-instance-header__badge-label">Health</span>
            {getHealthBadge(project.health)}
          </div>
          <div className="gf-mentor-instance-header__badge-item">
            <span className="gf-mentor-instance-header__badge-label">Status</span>
            <Badge variant={project.status === 'ACTIVE' ? 'info' : 'neutral'}>
              {project.status}
            </Badge>
          </div>
        </div>
      </div>

      <nav className="gf-mentor-instance-header__nav-tabs" aria-label="Inspection Tabs">
        {navItems.map((item) => (
          <Link
            key={item.id}
            to={item.to}
            id={`mentor-nav-${item.id}`}
            className={`gf-mentor-instance-header__nav-tab ${
              currentTab === item.id ? 'gf-mentor-instance-header__nav-tab--active' : ''
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
};
