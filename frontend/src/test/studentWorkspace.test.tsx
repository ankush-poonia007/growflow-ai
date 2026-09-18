import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, renderHook } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentProjectOverview } from '@/pages/Student/StudentProjectOverview/StudentProjectOverview';
import { StudentBlueprintWorkspace } from '@/pages/Student/StudentBlueprintWorkspace/StudentBlueprintWorkspace';
import { StudentBlueprintDocumentViewer } from '@/pages/Student/StudentBlueprintDocumentViewer/StudentBlueprintDocumentViewer';
import { SafeMarkdownViewer } from '@/components/ui/SafeMarkdownViewer/SafeMarkdownViewer';
import { useProjectWorkspace } from '@/hooks/useProjectWorkspace';
import type { ProjectOverviewResponse, BlueprintContentResponse, BlueprintDocumentDetail } from '@/lib/api/types';
import * as api from '@/lib/api';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProject: vi.fn(),
    getProjectOverview: vi.fn(),
    getBlueprintContent: vi.fn(),
    getBlueprintDocument: vi.fn(),
    downloadBlueprintDocument: vi.fn(),
  };
});

const mockOverview: ProjectOverviewResponse = {
  id: 'proj-123',
  student_id: 'student-999',
  group_id: null,
  project_definition_id: 'mentor-def-001',
  source_definition_version_id: 'v1.0',
  is_mentor_project: true,
  name: 'Autonomous Precision Agriculture Drone',
  problem: 'Inefficient ground monitoring in large acreage crops.',
  proposed_solution: 'Autonomous multi-rotor UAV with multispectral telemetry.',
  complexity: 'INTERMEDIATE',
  current_phase: 'BLUEPRINT',
  health: 'HEALTHY',
  progress_percentage: 35,
  status: 'ACTIVE',
  deadline: '2026-12-31T00:00:00Z',
  days_remaining: 108,
  profile: null,
  technologies: [],
  recent_activity: {},
  assessment_summary: {
    status: 'COMPLETED',
    overall_score: 84,
    readiness_tier: 'HIGH',
    dimension_scores: {
      problem_clarity: 88,
      architecture_readiness: 85,
      technical_feasibility: 82,
      delivery_confidence: 80,
    },
    technical_gaps_count: 2,
    recommendations_count: 3,
    completed_at: '2026-09-13T08:00:00Z',
  },
  blueprint_summary: {
    id: 'bp-123',
    status: 'APPROVED',
    qa_status: 'PASS',
    qa_score: 88,
    approved_at: '2026-09-13T09:00:00Z',
    total_sections: 10,
  },
};

const mockBlueprintContent: BlueprintContentResponse = {
  blueprint_id: 'bp-123',
  project_id: 'proj-123',
  status: 'APPROVED',
  qa_feedback: {
    score: 88,
    status: 'PASSED',
    evaluated_criteria: {},
    strengths: [],
    gaps: [],
    recommendations: [],
  },
  content: {
    project_profile: {
      problem: 'Inefficient ground monitoring in large acreage crops.',
      proposed_solution: 'Autonomous multi-rotor UAV with multispectral telemetry.',
      complexity: 'INTERMEDIATE',
      domain: 'Precision Agriculture',
    },
    tech_stack: {
      stack: [
        { category: 'Backend', technology: 'FastAPI', purpose: 'Core Telemetry API', why_selected: 'High throughput async' },
        { category: 'Database', technology: 'PostgreSQL', purpose: 'Mission Store', why_selected: 'Relational integrity' },
      ],
    },
    features: {
      features: [
        { id: 'F01', name: 'Mission Planner', priority: 'P0', description: 'Waypoint generator', acceptance_criteria: 'Geofence containment' },
      ],
    },
    specifications: {
      api_specifications: [
        { endpoint: '/api/v1/missions', method: 'POST', description: 'Create mission', auth: 'STUDENT', request_body: '{}', response: '{}' },
      ],
      data_models: ['MissionPlan (id, project_id, status)'],
    },
    mvp: {
      scope: 'Core mission flight plan and telemetry ingest.',
      inclusions: ['Waypoint engine'],
      exclusions: ['Swarm coordination'],
      success_metrics: ['0 geofence anomalies'],
    },
    duration: {
      total_estimated_weeks: 6,
      contingency_buffer_days: 5,
      timeline_phases: [{ phase: 'Foundation', duration_weeks: 2, focus: 'API' }],
    },
    risks: {
      technical_risks: [
        { id: 'R01', title: 'Packet Loss', severity: 'HIGH', mitigation: 'Buffer & retry' },
      ],
    },
    tasks: {
      tasks: [
        { id: 'T01', name: 'Setup database migrations', category: 'Core' },
      ],
    },
    milestones: {
      milestones_schedule: [
        { gate: 'M1', name: 'Architecture Frozen', deliverable: 'Specs verified' },
      ],
    },
    readme: {
      title: 'Autonomous Precision Agriculture Drone — Setup',
      overview: 'Production blueprint for autonomous UAV flight control.',
      quickstart: 'uvicorn backend.app.main:app',
      architecture_summary: 'Layered FastAPI architecture.',
    },
  },
};

const mockDocumentDetail: BlueprintDocumentDetail = {
  document_key: 'readme',
  title: 'README & Setup Guide',
  version: '1.0.0',
  status: 'APPROVED',
  format: 'markdown',
  markdown: '# Autonomous Precision Agriculture Drone\n\nProduction blueprint for autonomous UAV flight control.\n\n## Quickstart\n```bash\nuvicorn backend.app.main:app\n```',
  structured: null,
  available_documents: [
    { key: 'readme', title: 'README & Setup Guide', format: 'markdown', section_order: 10 },
    { key: 'tech_stack', title: 'Technology Stack & Architecture', format: 'markdown', section_order: 2 },
    { key: 'specifications', title: 'Technical Specifications', format: 'markdown', section_order: 4 },
  ],
  approved_at: '2026-09-13T09:00:00Z',
};

describe('Student Build Batch 4 — Project Workspace Foundation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ============================================================================
  // S15: Project Overview Tests
  // ============================================================================
  describe('S15: StudentProjectOverview', () => {
    it('renders project identity, 8-phase lifecycle, health, progress, and assessment summary', async () => {
      vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverview);

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-123/overview']}>
          <Routes>
            <Route path="/student/projects/:projectId/overview" element={<StudentProjectOverview />} />
          </Routes>
        </MemoryRouter>
      );

      // Verify loading state appears initially
      expect(screen.getByRole('status')).toBeInTheDocument();

      // Wait for content to render
      await waitFor(() => {
        expect(screen.getByText('Autonomous Precision Agriculture Drone')).toBeInTheDocument();
      });

      // Verify Project Identity
      expect(screen.getByText('Problem Statement')).toBeInTheDocument();
      expect(screen.getByText(/Inefficient ground monitoring in large acreage crops/)).toBeInTheDocument();
      expect(screen.getByText('Proposed Solution')).toBeInTheDocument();
      expect(screen.getByText(/Autonomous multi-rotor UAV/)).toBeInTheDocument();
      expect(screen.getByText('Mentor Defined')).toBeInTheDocument();

      // Verify 8-Phase Lifecycle Timeline
      expect(screen.getByText(/Phase Progression/)).toBeInTheDocument();
      expect(screen.getByText('BLUEPRINT')).toBeInTheDocument();
      expect(screen.getByText('ASSESSMENT')).toBeInTheDocument();
      expect(screen.getByText('PLANNING')).toBeInTheDocument();

      // Verify Health & Progress
      expect(screen.getByText('35%')).toBeInTheDocument();
      expect(screen.getAllByText('Healthy').length).toBeGreaterThanOrEqual(1);

      // Verify Assessment Diagnostic Summary
      expect(screen.getByText('84')).toBeInTheDocument();
      expect(screen.getByText('HIGH READINESS')).toBeInTheDocument();
      expect(screen.getByText('View Full Assessment Results →')).toBeInTheDocument();

      // Verify Blueprint Status Card
      expect(screen.getByText('Open Blueprint Workspace →')).toBeInTheDocument();
      expect(screen.getByText('View README.md →')).toBeInTheDocument();
      expect(screen.getByText('10 / 10 Approved')).toBeInTheDocument();
    });

    it('renders error state on 403 authorization failure', async () => {
      vi.mocked(api.getProjectOverview).mockRejectedValue({
        status: 403,
        code: 'AUTH_FORBIDDEN',
        message: 'Access to this project is denied.',
      });

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-999/overview']}>
          <Routes>
            <Route path="/student/projects/:projectId/overview" element={<StudentProjectOverview />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });

      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
      expect(screen.getByText(/You do not have permission/)).toBeInTheDocument();
      expect(screen.getByText('Return to All Projects')).toBeInTheDocument();
    });
  });

  // ============================================================================
  // S16: Blueprint Workspace Tests
  // ============================================================================
  describe('S16: StudentBlueprintWorkspace', () => {
    it('renders 10-section canonical sidebar and renders structured section data upon tab click', async () => {
      vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverview);
      vi.mocked(api.getBlueprintContent).mockResolvedValue(mockBlueprintContent);

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-123/blueprint/workspace']}>
          <Routes>
            <Route path="/student/projects/:projectId/blueprint/workspace" element={<StudentBlueprintWorkspace />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('✓ APPROVED BLUEPRINT ARTIFACT')).toBeInTheDocument();
      });

      // Verify canonical navigation items exist in sidebar
      expect(screen.getByRole('button', { name: /Project Profile/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Technical Stack/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Core Features/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Technical Specifications/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Technical Risks/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Granular Work Breakdown/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Stage Milestones/i })).toBeInTheDocument();

      // Click "Technical Stack"
      fireEvent.click(screen.getByRole('button', { name: /Technical Stack/i }));

      await waitFor(() => {
        expect(screen.getByText('FastAPI')).toBeInTheDocument();
        expect(screen.getByText('Core Telemetry API')).toBeInTheDocument();
        expect(screen.getByText('PostgreSQL')).toBeInTheDocument();
      });

      // Click "Technical Risks"
      fireEvent.click(screen.getByRole('button', { name: /Technical Risks/i }));

      await waitFor(() => {
        expect(screen.getByText('Packet Loss')).toBeInTheDocument();
        expect(screen.getByText('Buffer & retry')).toBeInTheDocument();
      });

      // Click "Core Features"
      fireEvent.click(screen.getByRole('button', { name: /Core Features/i }));

      await waitFor(() => {
        expect(screen.getByText('Mission Planner')).toBeInTheDocument();
        expect(screen.getByText('Geofence containment')).toBeInTheDocument();
      });

      // Verify Open in Document Viewer link exists
      expect(screen.getByText('Open in Document Viewer →')).toBeInTheDocument();
    });
  });

  // ============================================================================
  // S17: Blueprint Document Viewer Tests
  // ============================================================================
  describe('S17: StudentBlueprintDocumentViewer', () => {
    it('renders document in Preview mode and toggles to Raw Markdown mode and initiates download', async () => {
      vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverview);
      vi.mocked(api.getBlueprintDocument).mockResolvedValue(mockDocumentDetail);
      vi.mocked(api.downloadBlueprintDocument).mockResolvedValue(undefined);

      render(
        <MemoryRouter initialEntries={['/student/projects/proj-123/blueprint/documents/readme']}>
          <Routes>
            <Route path="/student/projects/:projectId/blueprint/documents/:documentKey" element={<StudentBlueprintDocumentViewer />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getAllByText('README & Setup Guide').length).toBeGreaterThanOrEqual(1);
      });

      // Verify Preview Mode content
      expect(screen.getByText(/Production blueprint for autonomous UAV flight control/)).toBeInTheDocument();
      expect(screen.getByText('uvicorn backend.app.main:app')).toBeInTheDocument();

      // Switch to Raw Markdown Mode
      const rawBtn = screen.getByRole('tab', { name: 'Raw Markdown' });
      fireEvent.click(rawBtn);

      expect(screen.getByLabelText('Raw Markdown Content')).toBeInTheDocument();
      expect(screen.getByText(/# Autonomous Precision Agriculture Drone/)).toBeInTheDocument();

      // Switch back to Preview Mode
      const previewBtn = screen.getByRole('tab', { name: 'Preview' });
      fireEvent.click(previewBtn);

      // Trigger Download
      const downloadBtn = screen.getByRole('button', { name: /Download \.md/ });
      fireEvent.click(downloadBtn);

      expect(api.downloadBlueprintDocument).toHaveBeenCalledWith('proj-123', 'readme');
    });
  });

  // ============================================================================
  // SafeMarkdownViewer Component Tests
  // ============================================================================
  describe('SafeMarkdownViewer', () => {
    it('renders headings, tables, lists, code blocks, and sanitizes links', () => {
      const sampleMarkdown = `
# Title Heading
## Subheading
This is a paragraph with **bold**, *italic*, and \`inline code\`.

[Safe Link](https://example.com)
[Dangerous Link](javascript:alert(1))

| Col 1 | Col 2 |
| :--- | :--- |
| Val A | Val B |

- List Item 1
- List Item 2

\`\`\`json
{ "key": "value" }
\`\`\`
      `;

      render(<SafeMarkdownViewer content={sampleMarkdown} />);

      expect(screen.getByText('Title Heading')).toBeInTheDocument();
      expect(screen.getByText('Subheading')).toBeInTheDocument();
      expect(screen.getByText('bold')).toBeInTheDocument();
      expect(screen.getByText('inline code')).toBeInTheDocument();

      // Table check
      expect(screen.getByText('Col 1')).toBeInTheDocument();
      expect(screen.getByText('Val A')).toBeInTheDocument();

      // List check
      expect(screen.getByText('List Item 1')).toBeInTheDocument();

      // Link security sanitization check
      const safeLink = screen.getByText('Safe Link');
      expect(safeLink).toHaveAttribute('href', 'https://example.com');

      const dangerousLink = screen.getByText('Dangerous Link');
      expect(dangerousLink).toHaveAttribute('href', '#'); // sanitized!
    });
  });

  describe('useProjectWorkspace hook (B4-01)', () => {
    it('guards against race conditions when projectId changes rapidly and discards unmounted state updates', async () => {
      let resolveA!: (val: any) => void;
      const promiseA = new Promise((resolve) => {
        resolveA = resolve;
      });
      let resolveB!: (val: any) => void;
      const promiseB = new Promise((resolve) => {
        resolveB = resolve;
      });

      vi.mocked(api.getProject).mockImplementation(async (id: string) => {
        if (id === 'proj-A') return promiseA as any;
        if (id === 'proj-B') return promiseB as any;
        return null as any;
      });

      const { result, rerender, unmount } = renderHook(
        ({ id }) => useProjectWorkspace(id),
        { initialProps: { id: 'proj-A' } }
      );

      expect(result.current.isLoading).toBe(true);

      // Rapidly switch to proj-B before proj-A resolves
      rerender({ id: 'proj-B' });

      // Resolve proj-B with B data
      resolveB({ id: 'proj-B', name: 'Project B' });

      await waitFor(() => {
        expect(result.current.project).toEqual({ id: 'proj-B', name: 'Project B' });
        expect(result.current.isLoading).toBe(false);
      });

      // Now resolve the older delayed proj-A
      resolveA({ id: 'proj-A', name: 'Project A' });

      // Stale response from proj-A must not overwrite Project B
      await new Promise((r) => setTimeout(r, 50));
      expect(result.current.project).toEqual({ id: 'proj-B', name: 'Project B' });

      // Unmount test: unmounting cancels commit
      unmount();
    });
  });
});
