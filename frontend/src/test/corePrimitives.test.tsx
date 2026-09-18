import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import {
  Card,
  CardLink,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  PageHeader,
  StatTile,
  EmptyState,
  Skeleton,
} from '@/components/ui';

describe('Core Workspace UI Primitives', () => {
  describe('Card Component', () => {
    it('renders card content with structural subcomponents and variants', () => {
      const { container } = render(
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Project Architecture</CardTitle>
            <CardDescription>Foundational build specs</CardDescription>
          </CardHeader>
          <CardContent>Main content body</CardContent>
          <CardFooter>Footer actions</CardFooter>
        </Card>,
      );

      expect(screen.getByText('Project Architecture')).toBeInTheDocument();
      expect(screen.getByText('Foundational build specs')).toBeInTheDocument();
      expect(screen.getByText('Main content body')).toBeInTheDocument();
      expect(screen.getByText('Footer actions')).toBeInTheDocument();
      expect(container.firstChild).toHaveClass('gf-card--bordered');
    });

    it('applies interactive modifier and supports CardLink', () => {
      render(
        <MemoryRouter>
          <CardLink to="/student/projects/123">
            <CardTitle>Interactive Project Card</CardTitle>
          </CardLink>
        </MemoryRouter>,
      );

      const link = screen.getByRole('link', { name: /interactive project card/i });
      expect(link).toBeInTheDocument();
      expect(link).toHaveClass('gf-card--interactive');
      expect(link).toHaveAttribute('href', '/student/projects/123');
    });
  });

  describe('PageHeader Component', () => {
    it('renders title, eyebrow, description, and breadcrumbs', () => {
      render(
        <MemoryRouter>
          <PageHeader
            title="Active Projects"
            eyebrow="Student Workspace"
            description="Manage and track your build pipeline."
            breadcrumbs={[
              { label: 'Workspace', to: '/student/dashboard' },
              { label: 'Projects' },
            ]}
            actions={<button type="button">New Project</button>}
          />
        </MemoryRouter>,
      );

      expect(screen.getByRole('heading', { level: 1, name: 'Active Projects' })).toBeInTheDocument();
      expect(screen.getByText('Student Workspace')).toBeInTheDocument();
      expect(screen.getByText('Manage and track your build pipeline.')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'Workspace' })).toHaveAttribute('href', '/student/dashboard');
      expect(screen.getByText('Projects')).toHaveAttribute('aria-current', 'page');
      expect(screen.getByRole('button', { name: 'New Project' })).toBeInTheDocument();
    });
  });

  describe('StatTile Component', () => {
    it('renders label, value, subtext, and applies tone classes', () => {
      const { container } = render(
        <StatTile
          label="Project Health"
          value="HEALTHY"
          subtext="No active blockers detected"
          tone="success"
        />,
      );

      expect(screen.getByText('Project Health')).toBeInTheDocument();
      expect(screen.getByText('HEALTHY')).toBeInTheDocument();
      expect(screen.getByText('No active blockers detected')).toBeInTheDocument();
      expect(container.firstChild).toHaveClass('gf-stat-tile--tone-success');
    });
  });

  describe('EmptyState Component', () => {
    it('renders title, description, and action button', () => {
      render(
        <EmptyState
          title="No Active Projects"
          description="Create your first project to get started with the build roadmap."
          action={<button type="button">Create Project</button>}
        />,
      );

      expect(screen.getByRole('heading', { level: 3, name: 'No Active Projects' })).toBeInTheDocument();
      expect(screen.getByText(/create your first project/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Create Project' })).toBeInTheDocument();
    });
  });

  describe('Skeleton Component', () => {
    it('renders with accessible loading attributes and supports variants', () => {
      render(
        <div>
          <Skeleton variant="text" width={200} height={20} />
          <Skeleton variant="circle" width={40} height={40} />
        </div>,
      );

      const statusElements = screen.getAllByRole('status');
      expect(statusElements).toHaveLength(2);
      expect(statusElements[0]).toHaveAttribute('aria-busy', 'true');
      expect(statusElements[0]).toHaveClass('gf-skeleton--text');
      expect(statusElements[1]).toHaveClass('gf-skeleton--circle');
    });
  });
});
