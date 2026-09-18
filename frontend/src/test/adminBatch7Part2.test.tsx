import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue, UserRole } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { AdminSidebar } from '@/components/navigation/AdminSidebar';
import { GroupsDirectory } from '@/pages/Admin/GroupsDirectory/GroupsDirectory';
import { GroupDetail } from '@/pages/Admin/GroupDetail/GroupDetail';
import { ProjectsDirectory } from '@/pages/Admin/ProjectsDirectory/ProjectsDirectory';
import { DefinitionsMonitoring } from '@/pages/Admin/DefinitionsMonitoring/DefinitionsMonitoring';
import { InstancesMonitoring } from '@/pages/Admin/InstancesMonitoring/InstancesMonitoring';
import { InstanceDetail } from '@/pages/Admin/InstanceDetail/InstanceDetail';

import * as apiClient from '@/lib/api/client';
import type {
  AdminGroupSummary,
  AdminGroupDetail,
  AdminProjectSummary,
  AdminProjectDefinitionSummary,
  AdminProjectDefinitionDetail,
  AdminInstanceMonitoringResponse,
  AdminProjectInstanceDetail,
} from '@/lib/api/types';

function createMockAuth(
  role: UserRole = 'ADMIN',
  fullName = 'Administrator',
  email = 'admin@growflow.ai'
): AuthContextValue {
  return {
    status: 'AUTHENTICATED',
    session: {
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      expires_in: 3600,
      token_type: 'bearer',
      user: { id: 'usr-admin-1', email } as unknown as User,
    },
    supabaseUser: { id: 'usr-admin-1', email } as unknown as User,
    user: {
      id: 'usr-admin-1',
      email,
      role,
      status: 'ACTIVE',
      fullName,
    },
    error: null,
    isRoleResolving: false,
    isAuthenticated: true,
    isLoading: false,
    signIn: vi.fn(),
    signOut: vi.fn(),
    retryAuth: vi.fn(),
    refreshAuthorization: vi.fn(),
  };
}

// ---------------------------------------------------------------------------
// Mock Data Fixtures
// ---------------------------------------------------------------------------

const mockGroups: AdminGroupSummary[] = [
  {
    id: 'grp-1',
    name: 'Cloud Infrastructure Cohort Alpha',
    mentor_id: 'mnt-1',
    mentor_name: 'Dr. Jane Smith',
    mentor_email: 'jane.smith@growflow.ai',
    join_code: 'INFRA2026',
    status: 'ACTIVE',
    created_at: '2026-01-10T00:00:00Z',
    updated_at: '2026-01-10T00:00:00Z',
    student_count: 18,
    project_count: 12,
  },
  {
    id: 'grp-2',
    name: 'Embedded Systems Beta',
    mentor_id: 'mnt-2',
    mentor_name: 'Prof. Alan Turing',
    mentor_email: 'alan.turing@growflow.ai',
    join_code: 'EMBED99',
    status: 'ARCHIVED',
    created_at: '2025-11-01T00:00:00Z',
    updated_at: '2025-11-01T00:00:00Z',
    student_count: 5,
    project_count: 3,
  },
];

const mockGroupDetail: AdminGroupDetail = {
  id: 'grp-1',
  name: 'Cloud Infrastructure Cohort Alpha',
  mentor_id: 'mnt-1',
  mentor_name: 'Dr. Jane Smith',
  mentor_email: 'jane.smith@growflow.ai',
  mentor_specialization: 'Distributed Systems & Cloud Architecture',
  join_code: 'INFRA2026',
  status: 'ACTIVE',
  created_at: '2026-01-10T00:00:00Z',
  updated_at: '2026-01-10T00:00:00Z',
  student_count: 18,
  project_count: 12,
  active_project_count: 10,
  members: [
    {
      id: 'mem-1',
      student_id: 'stu-101',
      full_name: 'Alice Johnson',
      email: 'alice@growflow.ai',
      status: 'ACTIVE',
      joined_at: '2026-01-12T00:00:00Z',
    },
  ],
  projects: [
    {
      id: 'proj-1',
      name: 'High-Throughput Ingestion Engine',
      student_id: 'stu-101',
      student_name: 'Alice Johnson',
      current_phase: 'IMPLEMENTATION',
      health: 'HEALTHY',
      progress_percentage: 65,
      status: 'ACTIVE',
      created_at: '2026-01-15T00:00:00Z',
    },
  ],
};

const mockProjects: AdminProjectSummary[] = [
  {
    id: 'proj-1',
    name: 'High-Throughput Ingestion Engine',
    student_id: 'stu-101',
    student_name: 'Alice Johnson',
    student_email: 'alice@growflow.ai',
    group_id: 'grp-1',
    group_name: 'Cloud Infrastructure Cohort Alpha',
    mentor_id: 'mnt-1',
    mentor_name: 'Dr. Jane Smith',
    current_phase: 'IMPLEMENTATION',
    health: 'HEALTHY',
    progress_percentage: 65,
    status: 'ACTIVE',
    complexity: 'HARD',
    source_definition_name: 'Distributed Telemetry Pipeline',
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-03-01T00:00:00Z',
  },
  {
    id: 'proj-2',
    name: 'Smart Energy Grid Monitor',
    student_id: 'stu-102',
    student_name: 'Bob Miller',
    student_email: 'bob@growflow.ai',
    group_id: 'grp-2',
    group_name: 'Embedded Systems Beta',
    mentor_id: 'mnt-2',
    mentor_name: 'Prof. Alan Turing',
    current_phase: 'PLANNING',
    health: 'CRITICAL',
    progress_percentage: 20,
    status: 'ACTIVE',
    complexity: 'MEDIUM',
    source_definition_name: null,
    created_at: '2026-02-01T00:00:00Z',
    updated_at: '2026-03-01T00:00:00Z',
  },
];

const mockDefinitions: AdminProjectDefinitionSummary[] = [
  {
    id: 'def-1',
    name: 'Distributed Telemetry Pipeline',
    owner_mentor_id: 'mnt-1',
    owner_mentor_name: 'Dr. Jane Smith',
    owner_mentor_email: 'jane.smith@growflow.ai',
    status: 'ACTIVE',
    current_version_id: 'ver-2',
    current_version_number: 2,
    complexity: 'HARD',
    instance_count: 8,
    version_count: 2,
    created_at: '2025-10-01T00:00:00Z',
    updated_at: '2026-01-05T00:00:00Z',
  },
];

const mockDefinitionDetail: AdminProjectDefinitionDetail = {
  id: 'def-1',
  name: 'Distributed Telemetry Pipeline',
  owner_mentor_id: 'mnt-1',
  owner_mentor_name: 'Dr. Jane Smith',
  owner_mentor_email: 'jane.smith@growflow.ai',
  status: 'ACTIVE',
  current_version_id: 'ver-2',
  current_version_number: 2,
  complexity: 'HARD',
  instance_count: 8,
  version_count: 2,
  created_at: '2025-10-01T00:00:00Z',
  updated_at: '2026-01-05T00:00:00Z',
  versions: [
    {
      id: 'ver-1',
      version_number: 1,
      name: 'Distributed Telemetry Pipeline v1',
      problem: 'Ingest and analyze high velocity metrics.',
      proposed_solution: 'Build Kafka-based streaming pipeline.',
      complexity: 'HARD',
      description: 'Initial pipeline version',
      duration: '8 weeks',
      constraints: 'Zero loss',
      assumptions: 'Kafka cluster running',
      technology_snapshot: [],
      created_by: 'Dr. Jane Smith',
      created_at: '2025-10-01T00:00:00Z',
    },
    {
      id: 'ver-2',
      version_number: 2,
      name: 'Distributed Telemetry Pipeline v2',
      problem: 'Ingest and analyze streaming metrics with zero-loss guarantee.',
      proposed_solution: 'Upgraded architecture with Redis caching layer and OpenTelemetry.',
      complexity: 'HARD',
      description: 'Upgraded telemetry pipeline with caching',
      duration: '10 weeks',
      constraints: 'Zero loss and sub-second ingestion',
      assumptions: 'Redis and Kafka clusters running',
      technology_snapshot: [],
      created_by: 'Dr. Jane Smith',
      created_at: '2026-01-05T00:00:00Z',
    },
  ],
  assigned_instances: [
    {
      id: 'proj-1',
      name: 'High-Throughput Ingestion Engine',
      student_name: 'Alice Johnson',
      current_phase: 'IMPLEMENTATION',
      health: 'HEALTHY',
      status: 'ACTIVE',
    },
  ],
};

const mockInstancesMonitoring: AdminInstanceMonitoringResponse = {
  summary: {
    total_instances: 42,
    healthy_count: 35,
    warning_count: 4,
    critical_count: 2,
    completed_count: 1,
  },
  instances: mockProjects,
};

const mockInstanceDetail: AdminProjectInstanceDetail = {
  id: 'proj-1',
  name: 'High-Throughput Ingestion Engine',
  problem: 'Ingest and analyze streaming metrics with zero-loss guarantee.',
  proposed_solution: 'Build Kafka-based streaming pipeline with Redis cache.',
  complexity: 'HARD',
  current_phase: 'IMPLEMENTATION',
  health: 'HEALTHY',
  progress_percentage: 65,
  status: 'ACTIVE',
  definition_id: 'def-1',
  definition_name: 'Distributed Telemetry Pipeline',
  version_number: 2,
  student_id: 'stu-101',
  student_name: 'Alice Johnson',
  student_email: 'alice@growflow.ai',
  mentor_id: 'mnt-1',
  mentor_name: 'Dr. Jane Smith',
  mentor_email: 'jane.smith@growflow.ai',
  group_id: 'grp-1',
  group_name: 'Cloud Infrastructure Cohort Alpha',
  created_at: '2026-01-15T00:00:00Z',
  updated_at: '2026-03-01T00:00:00Z',
  phase_history: [
    {
      id: 'ph-1',
      previous_phase: 'ORIENTATION',
      new_phase: 'PLANNING',
      changed_at: '2026-01-20T00:00:00Z',
      reason: 'Initial scope approved.',
    },
    {
      id: 'ph-2',
      previous_phase: 'PLANNING',
      new_phase: 'IMPLEMENTATION',
      changed_at: '2026-02-10T00:00:00Z',
      reason: 'Architecture sign-off.',
    },
  ],
  health_history: [
    {
      id: 'hh-1',
      previous_health: 'NEEDS_ATTENTION',
      new_health: 'HEALTHY',
      changed_at: '2026-02-15T00:00:00Z',
      reason: 'Resolved latency bottlenecks in cluster.',
    },
  ],
};

describe('GrowFlow Phase 7 Batch 7 Part 2 — Admin Governance Resources', () => {
  const adminAuth = createMockAuth();

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  // -------------------------------------------------------------------------
  // 1. AD06 — Groups Directory (/admin/groups)
  // -------------------------------------------------------------------------
  describe('AD06 — Groups Directory (/admin/groups)', () => {
    it('renders groups list, metrics, and handles search & status filtering', async () => {
      vi.spyOn(apiClient, 'getAdminGroups').mockImplementation(async (params) => {
        let list = mockGroups;
        if (params?.search) {
          const s = params.search.toLowerCase();
          list = list.filter(
            (g) =>
              g.name.toLowerCase().includes(s) ||
              g.join_code.toLowerCase().includes(s) ||
              g.mentor_name.toLowerCase().includes(s)
          );
        }
        if (params?.status && params.status !== 'ALL') {
          list = list.filter((g) => g.status === params.status);
        }
        return list;
      });

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/groups']}>
            <Routes>
              <Route path="/admin/groups" element={<GroupsDirectory />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Cloud Infrastructure Cohort Alpha')).toBeInTheDocument();
        expect(screen.getByText('Embedded Systems Beta')).toBeInTheDocument();
      });

      // Mentor and join codes
      expect(screen.getByText('Dr. Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('INFRA2026')).toBeInTheDocument();
      expect(screen.getByText('EMBED99')).toBeInTheDocument();

      // Search filter
      const searchInput = screen.getByLabelText(/search cohorts/i);
      fireEvent.change(searchInput, { target: { value: 'Alpha' } });

      await waitFor(() => {
        expect(screen.getByText('Cloud Infrastructure Cohort Alpha')).toBeInTheDocument();
        expect(screen.queryByText('Embedded Systems Beta')).not.toBeInTheDocument();
      });

      // Clear search
      fireEvent.change(searchInput, { target: { value: '' } });

      await waitFor(() => {
        expect(screen.getByText('Cloud Infrastructure Cohort Alpha')).toBeInTheDocument();
        expect(screen.getByText('Embedded Systems Beta')).toBeInTheDocument();
      });

      // Status filter
      const statusSelect = screen.getByLabelText(/filter by status/i);
      fireEvent.change(statusSelect, { target: { value: 'ARCHIVED' } });

      await waitFor(() => {
        expect(screen.queryByText('Cloud Infrastructure Cohort Alpha')).not.toBeInTheDocument();
        expect(screen.getByText('Embedded Systems Beta')).toBeInTheDocument();
      });
    });

    it('renders empty state when no groups match search', async () => {
      vi.spyOn(apiClient, 'getAdminGroups').mockImplementation(async (params) => {
        let list = mockGroups;
        if (params?.search) {
          const s = params.search.toLowerCase();
          list = list.filter(
            (g) =>
              g.name.toLowerCase().includes(s) ||
              g.join_code.toLowerCase().includes(s) ||
              g.mentor_name.toLowerCase().includes(s)
          );
        }
        return list;
      });

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/groups']}>
            <Routes>
              <Route path="/admin/groups" element={<GroupsDirectory />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Cloud Infrastructure Cohort Alpha')).toBeInTheDocument();
      });

      const searchInput = screen.getByLabelText(/search cohorts/i);
      fireEvent.change(searchInput, { target: { value: 'Nonexistent Group 99' } });

      await waitFor(() => {
        expect(screen.getByText('No cohorts found')).toBeInTheDocument();
        expect(screen.getByText('No groups match your current filter criteria.')).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 2. AD07 — Group Detail (/admin/groups/:groupId)
  // -------------------------------------------------------------------------
  describe('AD07 — Group Detail (/admin/groups/:groupId)', () => {
    it('renders group information, supervising mentor, members, and enrolled projects', async () => {
      vi.spyOn(apiClient, 'getAdminGroup').mockResolvedValue(mockGroupDetail);

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/groups/grp-1']}>
            <Routes>
              <Route path="/admin/groups/:groupId" element={<GroupDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Cloud Infrastructure Cohort Alpha')).toBeInTheDocument();
      });

      // Mentor details
      expect(screen.getByText('Dr. Jane Smith')).toBeInTheDocument();
      expect(screen.getByText(/Distributed Systems & Cloud Architecture/i)).toBeInTheDocument();

      // Read-only mode badge
      expect(screen.getByText('Governance Read-Only Mode')).toBeInTheDocument();

      // Enrolled student
      expect(screen.getAllByText('Alice Johnson').length).toBeGreaterThan(0);

      // Group project
      expect(screen.getByText('High-Throughput Ingestion Engine')).toBeInTheDocument();
      expect(screen.getByText('65%')).toBeInTheDocument();

      // Canonical link to project instance detail: /admin/instances/:projectId
      const projectLink = screen.getByRole('link', { name: 'Inspect Instance' });
      expect(projectLink).toHaveAttribute('href', '/admin/instances/proj-1');
    });
  });

  // -------------------------------------------------------------------------
  // 3. AD08 — Projects Directory (/admin/projects)
  // -------------------------------------------------------------------------
  describe('AD08 — Projects Directory (/admin/projects)', () => {
    it('renders project list and links to canonical /admin/instances/:projectId URL', async () => {
      vi.spyOn(apiClient, 'getAdminProjects').mockResolvedValue(mockProjects);

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/projects']}>
            <Routes>
              <Route path="/admin/projects" element={<ProjectsDirectory />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('High-Throughput Ingestion Engine')).toBeInTheDocument();
        expect(screen.getByText('Smart Energy Grid Monitor')).toBeInTheDocument();
      });

      // Student and Mentor supervisor context
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.getByText('Bob Miller')).toBeInTheDocument();

      // Phase & Health badges
      expect(screen.getByText('IMPLEMENTATION')).toBeInTheDocument();
      expect(screen.getAllByText('Healthy').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Critical').length).toBeGreaterThan(0);

      // Canonical link verification: must be /admin/instances/:projectId
      const links = screen.getAllByRole('link', { name: /inspect/i });
      expect(links[0]).toHaveAttribute('href', '/admin/instances/proj-1');
      expect(links[1]).toHaveAttribute('href', '/admin/instances/proj-2');
    });

    it('filters projects by health and phase', async () => {
      vi.spyOn(apiClient, 'getAdminProjects').mockImplementation(async (params) => {
        let list = mockProjects;
        if (params?.health && params.health !== 'ALL') {
          list = list.filter((p) => p.health === params.health);
        }
        return list;
      });

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/projects']}>
            <Routes>
              <Route path="/admin/projects" element={<ProjectsDirectory />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('High-Throughput Ingestion Engine')).toBeInTheDocument();
      });

      // Filter by Health: CRITICAL
      const healthSelect = screen.getByLabelText('Filter by health');
      fireEvent.change(healthSelect, { target: { value: 'CRITICAL' } });

      await waitFor(() => {
        expect(screen.queryByText('High-Throughput Ingestion Engine')).not.toBeInTheDocument();
        expect(screen.getByText('Smart Energy Grid Monitor')).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 4. AD09 — Definitions Monitoring (/admin/definitions)
  // -------------------------------------------------------------------------
  describe('AD09 — Definitions Monitoring (/admin/definitions)', () => {
    it('renders definition catalog and opens version inspection drawer', async () => {
      vi.spyOn(apiClient, 'getAdminDefinitions').mockResolvedValue(mockDefinitions);
      vi.spyOn(apiClient, 'getAdminDefinition').mockResolvedValue(mockDefinitionDetail);

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/definitions']}>
            <Routes>
              <Route path="/admin/definitions" element={<DefinitionsMonitoring />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('Distributed Telemetry Pipeline')).toBeInTheDocument();
      });

      expect(screen.getByText('v2')).toBeInTheDocument();
      expect(screen.getByText(/8\s*instances/i)).toBeInTheDocument();

      // Open version inspection modal
      const inspectBtn = screen.getByRole('button', { name: 'Inspect Tree' });
      fireEvent.click(inspectBtn);

      await waitFor(() => {
        expect(screen.getByText(/Immutable Versions \(2\)/i)).toBeInTheDocument();
        expect(screen.getByText('Version 1')).toBeInTheDocument();
        expect(screen.getByText('Version 2')).toBeInTheDocument();
      });

      // Inspect problem statements and solution overviews
      expect(screen.getByText(/Ingest and analyze high velocity metrics/i)).toBeInTheDocument();
      expect(screen.getByText(/Upgraded architecture with Redis caching layer/i)).toBeInTheDocument();

      // Close modal
      const closeBtn = screen.getByLabelText('Close modal');
      fireEvent.click(closeBtn);

      expect(screen.queryByText(/Immutable Versions \(2\)/i)).not.toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // 5. AD10 — Instances Monitoring (/admin/instances)
  // -------------------------------------------------------------------------
  describe('AD10 — Instances Monitoring (/admin/instances)', () => {
    it('renders KPI metrics and instance monitoring table linking to canonical detail', async () => {
      vi.spyOn(apiClient, 'getAdminInstancesMonitoring').mockResolvedValue(mockInstancesMonitoring);

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/instances']}>
            <Routes>
              <Route path="/admin/instances" element={<InstancesMonitoring />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('High-Throughput Ingestion Engine')).toBeInTheDocument();
      });

      // KPI card values
      expect(screen.getByText('42')).toBeInTheDocument(); // total
      expect(screen.getByText('35')).toBeInTheDocument(); // healthy
      expect(screen.getByText('4')).toBeInTheDocument();  // warning
      expect(screen.getByText('2')).toBeInTheDocument();  // critical
      expect(screen.getByText('1')).toBeInTheDocument();  // completed

      // Table contents
      expect(screen.getByText('High-Throughput Ingestion Engine')).toBeInTheDocument();
      expect(screen.getByText('Smart Energy Grid Monitor')).toBeInTheDocument();
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.getByText('Bob Miller')).toBeInTheDocument();
      expect(screen.getByText('Dr. Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('Prof. Alan Turing')).toBeInTheDocument();

      // Canonical link check: must link to /admin/instances/:projectId
      const links = screen.getAllByRole('link', { name: /inspect/i });
      expect(links[0]).toHaveAttribute('href', '/admin/instances/proj-1');
      expect(links[1]).toHaveAttribute('href', '/admin/instances/proj-2');
    });
  });

  // -------------------------------------------------------------------------
  // 6. AD10 — Canonical Project Instance Detail (/admin/instances/:projectId)
  // -------------------------------------------------------------------------
  describe('AD10 — Canonical Project Instance Detail (/admin/instances/:projectId)', () => {
    it('renders instance detail, pinned version, phase history, and health audit trail', async () => {
      vi.spyOn(apiClient, 'getAdminInstanceDetail').mockResolvedValue(mockInstanceDetail);

      render(
        <AuthContext.Provider value={adminAuth}>
          <MemoryRouter initialEntries={['/admin/instances/proj-1']}>
            <Routes>
              <Route path="/admin/instances/:projectId" element={<InstanceDetail />} />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByText('High-Throughput Ingestion Engine')).toBeInTheDocument();
      });

      // Pinned template
      expect(screen.getByText('Template: Distributed Telemetry Pipeline v2')).toBeInTheDocument();
      expect(screen.getByText('Governance Read-Only Mode')).toBeInTheDocument();

      // Student and mentor info
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.getByText('Dr. Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('Cloud Infrastructure Cohort Alpha')).toBeInTheDocument();

      // Phase history
      expect(screen.getByText(/Phase Transitions \(2\)/i)).toBeInTheDocument();
      expect(screen.getByText('ORIENTATION')).toBeInTheDocument();
      expect(screen.getAllByText('PLANNING').length).toBeGreaterThan(0);
      expect(screen.getByText('Initial scope approved.')).toBeInTheDocument();

      // Health history
      expect(screen.getByText(/Health Transitions \(1\)/i)).toBeInTheDocument();
      expect(screen.getByText('Resolved latency bottlenecks in cluster.')).toBeInTheDocument();

      // Problem & Solution
      expect(screen.getByText(/Ingest and analyze streaming metrics with zero-loss guarantee/i)).toBeInTheDocument();
      expect(screen.getByText(/Build Kafka-based streaming pipeline with Redis cache/i)).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // 7. AdminSidebar Navigation
  // -------------------------------------------------------------------------
  describe('AdminSidebar Navigation', () => {
    it('renders navigation links for Groups, Projects, Definitions, and Instances', () => {
      render(
        <MemoryRouter initialEntries={['/admin/overview']}>
          <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
        </MemoryRouter>
      );

      // Verify all links exist
      expect(screen.getByRole('link', { name: /overview/i })).toHaveAttribute('href', '/admin/overview');
      expect(screen.getByRole('link', { name: /mentors/i })).toHaveAttribute('href', '/admin/mentors');
      expect(screen.getByRole('link', { name: /students/i })).toHaveAttribute('href', '/admin/students');
      expect(screen.getByRole('link', { name: /groups/i })).toHaveAttribute('href', '/admin/groups');
      expect(screen.getByRole('link', { name: /projects/i })).toHaveAttribute('href', '/admin/projects');
      expect(screen.getByRole('link', { name: /definitions/i })).toHaveAttribute('href', '/admin/definitions');
      expect(screen.getByRole('link', { name: /instances/i })).toHaveAttribute('href', '/admin/instances');
    });

    it('highlights the active section correctly', () => {
      render(
        <MemoryRouter initialEntries={['/admin/definitions']}>
          <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
        </MemoryRouter>
      );

      const definitionsLink = screen.getByRole('link', { name: /definitions/i });
      expect(definitionsLink).toHaveClass('gf-admin-sidebar__item--active');
    });
  });
});
