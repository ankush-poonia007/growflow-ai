import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue, UserRole } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { AdminSidebar } from '@/components/navigation/AdminSidebar';
import { DocumentsRAG } from '@/pages/Admin/DocumentsRAG/DocumentsRAG';
import { RAGMonitoring } from '@/pages/Admin/RAGMonitoring/RAGMonitoring';
import { DocumentGeneration } from '@/pages/Admin/DocumentGeneration/DocumentGeneration';
import { PlatformAnalytics } from '@/pages/Admin/PlatformAnalytics/PlatformAnalytics';
import { AnalyticsDetail } from '@/pages/Admin/AnalyticsDetail/AnalyticsDetail';
import * as apiClient from '@/lib/api/client';
import type {
  AdminDocumentsResponse,
  AdminRAGDiagnostics,
  AdminGenerationJobsResponse,
  AdminPlatformAnalyticsResponse,
  AdminAnalyticsDimensionDetail,
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

const mockDocumentsData: AdminDocumentsResponse = {
  total: 2,
  limit: 25,
  offset: 0,
  doc_type_counts: {
    BLUEPRINT: 1,
    SPECIFICATION: 1,
    README: 0,
  },
  documents: [
    {
      id: 'doc-1',
      project_instance_id: 'proj-1',
      project_name: 'Smart Energy Grid',
      document_key: 'system_blueprint_v1',
      title: 'Smart Energy System Blueprint',
      doc_type: 'BLUEPRINT',
      format: 'markdown',
      version: '1.0',
      status: 'ACTIVE',
      source: 'BLUEPRINT_INIT',
      size_bytes: 4096,
      created_at: new Date('2026-03-01T10:00:00Z').toISOString(),
      updated_at: new Date('2026-03-01T10:00:00Z').toISOString(),
    },
    {
      id: 'doc-2',
      project_instance_id: 'proj-1',
      project_name: 'Smart Energy Grid',
      document_key: 'api_spec_v1',
      title: 'API Specification',
      doc_type: 'SPECIFICATION',
      format: 'markdown',
      version: '1.0',
      status: 'ACTIVE',
      source: 'BLUEPRINT_INIT',
      size_bytes: 2048,
      created_at: new Date('2026-03-02T10:00:00Z').toISOString(),
      updated_at: new Date('2026-03-02T10:00:00Z').toISOString(),
    },
  ],
};

const mockRAGData: AdminRAGDiagnostics = {
  status: 'DEFERRED_INTEGRATION',
  posture_description:
    'Vector storage and retrieval infrastructure is currently deferred in this deployment.',
  vector_store_type: 'NONE_CONFIGURED',
  embedding_model: 'text-embedding-3-small',
  target_chunk_size: 800,
  target_chunk_overlap: 100,
  target_top_k: 5,
  index_generated_documents: true,
  eligible_documents_count: 24,
  recent_events: [
    {
      id: 'evt-1',
      event_type: 'DOCUMENT_CREATED',
      title: 'Blueprint Published',
      description: 'System blueprint created for Project 1',
      occurred_at: new Date('2026-03-01T12:00:00Z').toISOString(),
      status: 'PUBLISHED',
    },
  ],
};

const mockGenerationJobsData: AdminGenerationJobsResponse = {
  total: 2,
  limit: 25,
  offset: 0,
  summary: {
    total_jobs: 2,
    completed_jobs: 1,
    running_jobs: 0,
    failed_jobs: 1,
    pending_jobs: 0,
    average_duration_seconds: 14.5,
  },
  jobs: [
    {
      id: 'job-1111-2222',
      blueprint_id: 'bp-1',
      project_instance_id: 'proj-1',
      project_name: 'Smart Energy Grid',
      job_type: 'FULL_BLUEPRINT',
      target_output: 'blueprint.md',
      status: 'COMPLETED',
      current_step: 'complete',
      progress_percent: 100,
      error: null,
      started_at: new Date('2026-03-01T10:00:00Z').toISOString(),
      completed_at: new Date('2026-03-01T10:00:14Z').toISOString(),
      created_at: new Date('2026-03-01T10:00:00Z').toISOString(),
      duration_seconds: 14.5,
    },
    {
      id: 'job-3333-4444',
      blueprint_id: 'bp-2',
      project_instance_id: 'proj-2',
      project_name: 'AI Crop Diagnostics',
      job_type: 'SYSTEM_ARCHITECTURE',
      target_output: 'architecture.md',
      status: 'FAILED',
      current_step: 'synthesis',
      progress_percent: 45,
      error: 'Upstream model timeout after 30s',
      started_at: new Date('2026-03-02T11:00:00Z').toISOString(),
      completed_at: null,
      created_at: new Date('2026-03-02T11:00:00Z').toISOString(),
      duration_seconds: null,
    },
  ],
};

const mockAnalyticsData: AdminPlatformAnalyticsResponse = {
  overview: {
    total_users: 150,
    total_students: 120,
    total_mentors: 25,
    total_groups: 10,
    total_projects: 30,
    active_projects: 18,
    completed_projects: 8,
    at_risk_projects: 4,
    total_documents: 65,
    total_generation_jobs: 40,
    total_domain_events: 512,
  },
  project_phase_distribution: {
    INCEPTION: 5,
    BLUEPRINT: 10,
    EXECUTION: 12,
    REVIEW: 3,
  },
  project_health_distribution: {
    HEALTHY: 20,
    NEEDS_ATTENTION: 6,
    AT_RISK: 4,
  },
  task_status_distribution: {
    TODO: 40,
    IN_PROGRESS: 25,
    COMPLETED: 85,
  },
  user_status_distribution: {
    ACTIVE: 140,
    INVITED: 10,
  },
  generation_job_distribution: {
    COMPLETED: 32,
    FAILED: 5,
    RUNNING: 3,
  },
  document_type_distribution: {
    BLUEPRINT: 20,
    SPECIFICATION: 25,
    README: 20,
  },
  event_type_distribution: {
    TASK_COMPLETED: 120,
    DOCUMENT_CREATED: 65,
  },
  help_request_distribution: {
    OPEN: 6,
    RESOLVED: 18,
  },
};

const mockProjectsDimensionDetail: AdminAnalyticsDimensionDetail = {
  dimension: 'projects',
  title: 'Project Telemetry & Execution Analytics',
  description: 'Authoritative portfolio progress and health distributions.',
  total_records: 30,
  generated_at: new Date().toISOString(),
  data: {
    summary: {
      total_projects: 30,
      active_projects: 18,
      completed_projects: 8,
      at_risk_projects: 4,
      avg_progress: 68.4,
    },
    phases: {
      INCEPTION: 5,
      BLUEPRINT: 10,
      EXECUTION: 12,
    },
    health: {
      HEALTHY: 20,
      NEEDS_ATTENTION: 6,
      AT_RISK: 4,
    },
    tasks: {
      total_tasks: 150,
      completed_tasks: 85,
      completion_rate_percent: 56.7,
    },
  },
};

describe('Admin Batch 9 — Documents, RAG & Platform Analytics', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  // ============================================================
  // AdminSidebar Navigation Tests
  // ============================================================
  describe('AdminSidebar Navigation', () => {
    it('renders Documents & RAG and Platform Analytics navigation items', () => {
      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/admin/overview']}>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByRole('link', { name: /Documents & RAG/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Platform Analytics/i })).toBeInTheDocument();
    });

    it('marks Documents & RAG active on /admin/documents', () => {
      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/admin/documents']}>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const link = screen.getByRole('link', { name: /Documents & RAG/i });
      expect(link.className).toContain('gf-admin-sidebar__item--active');
      expect(link).toHaveAttribute('aria-current', 'page');
    });

    it('marks Platform Analytics active on /admin/analytics', () => {
      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/admin/analytics']}>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const link = screen.getByRole('link', { name: /Platform Analytics/i });
      expect(link.className).toContain('gf-admin-sidebar__item--active');
      expect(link).toHaveAttribute('aria-current', 'page');
    });
  });

  // ============================================================
  // AD21: Documents & Knowledge Tests
  // ============================================================
  describe('AD21 — Documents & Knowledge (/admin/documents)', () => {
    it('renders header, stat tiles, and documents table', async () => {
      vi.spyOn(apiClient, 'getAdminDocuments').mockResolvedValue(mockDocumentsData);

      render(
        <MemoryRouter>
          <DocumentsRAG />
        </MemoryRouter>
      );

      expect(screen.getByText('DELIVERABLE GOVERNANCE')).toBeInTheDocument();
      expect(screen.getByText('Documents & Knowledge')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('Smart Energy System Blueprint')).toBeInTheDocument();
        expect(screen.getByText('system_blueprint_v1')).toBeInTheDocument();
        expect(screen.getByText('API Specification')).toBeInTheDocument();
      });

      expect(screen.getByText('Total Documents')).toBeInTheDocument();
      expect(screen.getByText('Blueprints')).toBeInTheDocument();
    });

    it('handles search and filter inputs correctly', async () => {
      const getDocsSpy = vi
        .spyOn(apiClient, 'getAdminDocuments')
        .mockResolvedValue(mockDocumentsData);

      render(
        <MemoryRouter>
          <DocumentsRAG />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Search by title/i)).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/Search by title/i);
      fireEvent.change(searchInput, { target: { value: 'Blueprint' } });

      await waitFor(() => {
        expect(getDocsSpy).toHaveBeenCalledWith(
          expect.objectContaining({ search: 'Blueprint' })
        );
      });
    });

    it('renders empty state when no documents are returned', async () => {
      vi.spyOn(apiClient, 'getAdminDocuments').mockResolvedValue({
        total: 0,
        limit: 25,
        offset: 0,
        doc_type_counts: {},
        documents: [],
      });

      render(
        <MemoryRouter>
          <DocumentsRAG />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('No Documents Found')).toBeInTheDocument();
      });
    });

    it('renders error alert when API call fails', async () => {
      vi.spyOn(apiClient, 'getAdminDocuments').mockRejectedValue(
        new Error('Network connectivity lost')
      );

      render(
        <MemoryRouter>
          <DocumentsRAG />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Network connectivity lost')).toBeInTheDocument();
      });
    });
  });

  // ============================================================
  // AD22: RAG Subsystem Monitoring Tests
  // ============================================================
  describe('AD22 — RAG Subsystem Monitoring (/admin/documents/rag)', () => {
    it('truthfully renders deferred integration posture and configuration parameters', async () => {
      vi.spyOn(apiClient, 'getAdminRAGDiagnostics').mockResolvedValue(mockRAGData);

      render(
        <MemoryRouter>
          <RAGMonitoring />
        </MemoryRouter>
      );

      expect(screen.getByText('INTELLIGENCE INFRASTRUCTURE')).toBeInTheDocument();
      expect(screen.getByText('RAG Subsystem Monitoring')).toBeInTheDocument();

      await waitFor(() => {
        expect(
          screen.getByText(/Vector Database Integration Posture: DEFERRED_INTEGRATION/i)
        ).toBeInTheDocument();
        expect(screen.getAllByText('NONE_CONFIGURED').length).toBeGreaterThanOrEqual(1);
        expect(screen.getAllByText('text-embedding-3-small').length).toBeGreaterThanOrEqual(1);
        expect(screen.getByText('800 characters')).toBeInTheDocument();
      });

      // Events table
      expect(screen.getByText('Blueprint Published')).toBeInTheDocument();
      expect(screen.getByText('DOCUMENT_CREATED')).toBeInTheDocument();
    });

    it('renders back link to documents', async () => {
      vi.spyOn(apiClient, 'getAdminRAGDiagnostics').mockResolvedValue(mockRAGData);

      render(
        <MemoryRouter>
          <RAGMonitoring />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('RAG Subsystem Monitoring')).toBeInTheDocument();
      });

      const backLink = screen.getByRole('link', { name: /Back to Documents & Knowledge/i });
      expect(backLink).toBeInTheDocument();
      expect(backLink.getAttribute('href')).toBe('/admin/documents');
    });
  });

  // ============================================================
  // AD23: Document Generation Runs Tests
  // ============================================================
  describe('AD23 — Document Generation Runs (/admin/documents/generation)', () => {
    it('renders generation runs summary and jobs table', async () => {
      vi.spyOn(apiClient, 'getAdminGenerationJobs').mockResolvedValue(mockGenerationJobsData);

      render(
        <MemoryRouter>
          <DocumentGeneration />
        </MemoryRouter>
      );

      expect(screen.getByText('SYNTHESIS WORKLOADS')).toBeInTheDocument();
      expect(screen.getByText('Document Generation Runs')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('Total Workloads')).toBeInTheDocument();
        expect(screen.getByText('job-1111')).toBeInTheDocument();
        expect(screen.getByText('job-3333')).toBeInTheDocument();
        expect(screen.getAllByText('14.5s').length).toBeGreaterThanOrEqual(1);
      });

      // Error detail for failed job
      expect(
        screen.getByText(/Error: Upstream model timeout after 30s/i)
      ).toBeInTheDocument();
    });

    it('renders filters for workload status and type', async () => {
      const getJobsSpy = vi
        .spyOn(apiClient, 'getAdminGenerationJobs')
        .mockResolvedValue(mockGenerationJobsData);

      render(
        <MemoryRouter>
          <DocumentGeneration />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByLabelText(/Status/i)).toBeInTheDocument();
      });

      const statusSelect = screen.getByLabelText(/Status/i);
      fireEvent.change(statusSelect, { target: { value: 'COMPLETED' } });

      await waitFor(() => {
        expect(getJobsSpy).toHaveBeenCalledWith(
          expect.objectContaining({ status: 'COMPLETED' })
        );
      });
    });
  });

  // ============================================================
  // AD28: Platform Analytics Tests
  // ============================================================
  describe('AD28 — Platform Analytics (/admin/analytics)', () => {
    it('renders macro telemetry metrics and canonical distribution cards', async () => {
      vi.spyOn(apiClient, 'getAdminAnalytics').mockResolvedValue(mockAnalyticsData);

      render(
        <MemoryRouter>
          <PlatformAnalytics />
        </MemoryRouter>
      );

      expect(screen.getByText('MACRO TELEMETRY')).toBeInTheDocument();
      expect(screen.getByText('Platform Analytics')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('Total Users')).toBeInTheDocument();
        expect(screen.getByText('Total Projects')).toBeInTheDocument();
        expect(screen.getByText('Project Lifecycle Phases')).toBeInTheDocument();
        expect(screen.getByText('Project Health Classifications')).toBeInTheDocument();
        expect(screen.getByText('Task Execution Statuses')).toBeInTheDocument();
      });

      // Dimensional deep dive links
      expect(screen.getByRole('link', { name: /Projects Telemetry →/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /User Demographics →/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Deliverable Corpus →/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Event Velocity →/i })).toBeInTheDocument();
    });
  });

  // ============================================================
  // AD29: Analytics Dimensional Detail Tests
  // ============================================================
  describe('AD29 — Analytics Dimensional Detail (/admin/analytics/:dimension)', () => {
    it('renders projects dimensional detail for a valid dimension', async () => {
      vi.spyOn(apiClient, 'getAdminAnalyticsDimension').mockResolvedValue(
        mockProjectsDimensionDetail
      );

      render(
        <MemoryRouter initialEntries={['/admin/analytics/projects']}>
          <Routes>
            <Route path="/admin/analytics/:dimension" element={<AnalyticsDetail />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText('DIMENSIONAL TELEMETRY')).toBeInTheDocument();

      await waitFor(() => {
        expect(
          screen.getByText('Project Telemetry & Execution Analytics')
        ).toBeInTheDocument();
        expect(screen.getByText('PROJECTS')).toBeInTheDocument();
        expect(screen.getByText('Phases')).toBeInTheDocument();
        expect(screen.getByText('Tasks')).toBeInTheDocument();
      });
    });

    it('renders 404 EmptyState when an invalid dimension is passed', async () => {
      render(
        <MemoryRouter initialEntries={['/admin/analytics/invalid-dimension']}>
          <Routes>
            <Route path="/admin/analytics/:dimension" element={<AnalyticsDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Dimension Not Found')).toBeInTheDocument();
        expect(
          screen.getByText(/The analytics dimension "invalid-dimension" is not recognized/i)
        ).toBeInTheDocument();
      });
    });
  });
});
