import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentTasks } from '@/pages/Student/StudentTasks/StudentTasks';
import { StudentTaskDetail } from '@/pages/Student/StudentTaskDetail/StudentTaskDetail';
import { StudentMilestones } from '@/pages/Student/StudentMilestones/StudentMilestones';
import { StudentMilestoneDetail } from '@/pages/Student/StudentMilestoneDetail/StudentMilestoneDetail';
import { StudentRisks } from '@/pages/Student/StudentRisks/StudentRisks';
import { StudentRiskDetail } from '@/pages/Student/StudentRiskDetail/StudentRiskDetail';
import { StudentRoadmap } from '@/pages/Student/StudentRoadmap/StudentRoadmap';
import { StudentDocuments } from '@/pages/Student/StudentDocuments/StudentDocuments';
import { StudentDocumentDetail } from '@/pages/Student/StudentDocumentDetail/StudentDocumentDetail';
import type {
  ProjectResponse,
  TaskResponse,
  MilestoneResponse,
  RiskResponse,
  RoadmapResponse,
  DocumentResponse,
} from '@/lib/api/types';
import * as api from '@/lib/api';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProject: vi.fn(),
    getTasks: vi.fn(),
    getTask: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
    getMilestones: vi.fn(),
    getMilestone: vi.fn(),
    createMilestone: vi.fn(),
    updateMilestone: vi.fn(),
    getRisks: vi.fn(),
    getRisk: vi.fn(),
    createRisk: vi.fn(),
    updateRisk: vi.fn(),
    deleteRisk: vi.fn(),
    getRoadmap: vi.fn(),
    getDocuments: vi.fn(),
    getDocument: vi.fn(),
    createDocument: vi.fn(),
    updateDocument: vi.fn(),
    downloadDocument: vi.fn(),
  };
});

const mockProject: ProjectResponse = {
  id: 'proj-123',
  student_id: 'student-999',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Precision Drone Telemetry System',
  problem: 'Real-time telemetry tracking gaps',
  proposed_solution: 'Autonomous sensor fusion drone',
  complexity: 'INTERMEDIATE',
  current_phase: 'BLUEPRINT',
  health: 'HEALTHY',
  progress_percentage: 35,
  status: 'ACTIVE',
  deadline: '2026-12-31T00:00:00Z',
  started_at: '2026-09-13T00:00:00Z',
  completed_at: null,
  created_at: '2026-09-13T00:00:00Z',
  updated_at: '2026-09-13T00:00:00Z',
};

const mockTasks: TaskResponse[] = [
  {
    id: 'task-1',
    project_instance_id: 'proj-123',
    milestone_id: 'm-1',
    task_code: 'T01',
    title: 'Initialize repository and database schema',
    description: 'Set up PostgreSQL with Alembic migrations',
    status: 'TODO',
    priority: 'HIGH',
    category: 'BACKEND',
    phase: 'PLANNING',
    due_date: '2026-10-01T00:00:00Z',
    dependencies: [],
    acceptance_criteria: ['Migrations run', 'Tests pass'],
    completed_at: null,
    created_at: '2026-09-13T00:00:00Z',
    updated_at: '2026-09-13T00:00:00Z',
  },
  {
    id: 'task-2',
    project_instance_id: 'proj-123',
    milestone_id: 'm-1',
    task_code: 'T02',
    title: 'Build telemetry websocket stream',
    description: 'Stream live GPS and sensor data',
    status: 'IN_PROGRESS',
    priority: 'CRITICAL',
    category: 'BACKEND',
    phase: 'IMPLEMENTATION',
    due_date: null,
    dependencies: ['T01'],
    acceptance_criteria: [],
    completed_at: null,
    created_at: '2026-09-13T00:00:00Z',
    updated_at: '2026-09-13T00:00:00Z',
  },
];

const mockMilestones: MilestoneResponse[] = [
  {
    id: 'm-1',
    project_instance_id: 'proj-123',
    gate_code: 'M1',
    title: 'Architecture & Foundations',
    description: 'Establish core models and baseline services',
    status: 'IN_PROGRESS',
    progress_percent: 50,
    target_date: '2026-10-15T00:00:00Z',
    deliverables: ['Database Schema', 'FastAPI Scaffolding'],
    section_order: 1,
    task_count: 2,
    completed_task_count: 0,
    tasks: mockTasks,
    created_at: '2026-09-13T00:00:00Z',
    updated_at: '2026-09-13T00:00:00Z',
  },
];

const mockRisks: RiskResponse[] = [
  {
    id: 'risk-1',
    project_instance_id: 'proj-123',
    risk_code: 'R01',
    title: 'Wireless signal degradation at altitude',
    description: 'Signal loss during inclement weather',
    severity: 'HIGH',
    probability: 'MEDIUM',
    impact: 'HIGH',
    status: 'OPEN',
    mitigation: 'Implement dual-band antenna failover',
    owner: 'Student',
    review_date: '2026-10-10T00:00:00Z',
    created_at: '2026-09-13T00:00:00Z',
    updated_at: '2026-09-13T00:00:00Z',
  },
];

const mockRoadmap: RoadmapResponse = {
  project_id: 'proj-123',
  project_name: 'Precision Drone Telemetry System',
  current_phase: 'BLUEPRINT',
  summary: {
    total_milestones: 1,
    completed_milestones: 0,
    total_tasks: 2,
    completed_tasks: 0,
    overdue_tasks_count: 0,
    blocked_tasks_count: 0,
    current_phase: 'BLUEPRINT',
    overall_progress: 35,
  },
  milestones: [
    {
      id: 'm-1',
      gate_code: 'M1',
      title: 'Architecture & Foundations',
      description: 'Establish core models and baseline services',
      status: 'IN_PROGRESS',
      progress_percent: 50,
      target_date: '2026-10-15T00:00:00Z',
      deliverables: ['Database Schema'],
      tasks: mockTasks,
    },
  ],
  grouped_tasks: {
    overdue: [],
    blocked: [],
    in_progress: [mockTasks[1]!],
    upcoming: [mockTasks[0]!],
    completed: [],
  },
};

const mockDocuments: DocumentResponse[] = [
  {
    id: 'doc-1',
    project_instance_id: 'proj-123',
    document_key: 'master_architecture',
    title: 'Master Architecture Blueprint',
    doc_type: 'BLUEPRINT',
    format: 'markdown',
    content: '# Master Architecture\n\nSystem architecture details.',
    version: '1.0',
    status: 'ACTIVE',
    source: 'BLUEPRINT_INIT',
    created_at: '2026-09-13T00:00:00Z',
    updated_at: '2026-09-13T00:00:00Z',
  },
];

describe('Batch 5 Execution Management Components (S18–S26)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.getProject).mockResolvedValue(mockProject);
    vi.mocked(api.getTasks).mockResolvedValue(mockTasks);
    vi.mocked(api.getTask).mockResolvedValue(mockTasks[0]!);
    vi.mocked(api.getMilestones).mockResolvedValue(mockMilestones);
    vi.mocked(api.getMilestone).mockResolvedValue(mockMilestones[0]!);
    vi.mocked(api.getRisks).mockResolvedValue(mockRisks);
    vi.mocked(api.getRisk).mockResolvedValue(mockRisks[0]!);
    vi.mocked(api.getRoadmap).mockResolvedValue(mockRoadmap);
    vi.mocked(api.getDocuments).mockResolvedValue(mockDocuments);
    vi.mocked(api.getDocument).mockResolvedValue(mockDocuments[0]!);
  });

  // 1. S18 Tasks
  it('renders S18 tasks view with stats, filters, and kanban board', async () => {
    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/tasks']}>
        <Routes>
          <Route path="/student/projects/:projectId/tasks" element={<StudentTasks />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Precision Drone Telemetry System')).toBeInTheDocument();
      expect(screen.getByText('Initialize repository and database schema')).toBeInTheDocument();
      expect(screen.getByText('Build telemetry websocket stream')).toBeInTheDocument();
    });

    // Check stats
    expect(screen.getByText('Total Tasks')).toBeInTheDocument();
    expect(screen.getByText('+ New Task')).toBeInTheDocument();

    // Toggle to list view
    const listBtn = screen.getByRole('button', { name: /Table view/i });
    fireEvent.click(listBtn);
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  // 2. S19 Task Detail
  it('renders S19 task detail and allows saving updates', async () => {
    vi.mocked(api.updateTask).mockResolvedValue({
      ...mockTasks[0]!,
      status: 'COMPLETED',
    });

    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/tasks/task-1']}>
        <Routes>
          <Route path="/student/projects/:projectId/tasks/:taskId" element={<StudentTaskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Initialize repository and database schema')).toBeInTheDocument();
    });

    // Save changes
    const saveBtn = screen.getByRole('button', { name: /Save Task Changes/i });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(api.updateTask).toHaveBeenCalledWith(
        'proj-123',
        'task-1',
        expect.objectContaining({ title: 'Initialize repository and database schema' })
      );
    });
  });

  // 3. S20 Milestones
  it('renders S20 milestones list with gate progression', async () => {
    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/milestones']}>
        <Routes>
          <Route path="/student/projects/:projectId/milestones" element={<StudentMilestones />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Execution Milestones & Quality Gates')).toBeInTheDocument();
      expect(screen.getByText('Architecture & Foundations')).toBeInTheDocument();
      expect(screen.getByText('50%')).toBeInTheDocument();
    });
  });

  // 4. S21 Milestone Detail
  it('renders S21 milestone detail with deliverables and assigned tasks', async () => {
    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/milestones/m-1']}>
        <Routes>
          <Route path="/student/projects/:projectId/milestones/:milestoneId" element={<StudentMilestoneDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText('Architecture & Foundations')[0]).toBeInTheDocument();
      expect(screen.getAllByText(/Database Schema/i)[0]).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Save Milestone Changes/i })).toBeInTheDocument();
    });
  });

  // 5. S22 Risks
  it('renders S22 risk register with severity badges and search', async () => {
    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/risks']}>
        <Routes>
          <Route path="/student/projects/:projectId/risks" element={<StudentRisks />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Wireless signal degradation at altitude')).toBeInTheDocument();
      expect(screen.getByText(/HIGH Severity/i)).toBeInTheDocument();
      expect(screen.getByText('+ New Risk')).toBeInTheDocument();
    });
  });

  // 6. S23 Risk Detail
  it('renders S23 risk detail and saves updates', async () => {
    vi.mocked(api.updateRisk).mockResolvedValue({
      ...mockRisks[0]!,
      status: 'MITIGATING',
    });

    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/risks/risk-1']}>
        <Routes>
          <Route path="/student/projects/:projectId/risks/:riskId" element={<StudentRiskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Wireless signal degradation at altitude')).toBeInTheDocument();
    });

    const saveBtn = screen.getByRole('button', { name: /Save Risk Changes/i });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(api.updateRisk).toHaveBeenCalledWith(
        'proj-123',
        'risk-1',
        expect.objectContaining({ title: 'Wireless signal degradation at altitude' })
      );
    });
  });

  // 7. S24 Roadmap
  it('renders S24 roadmap projection with overall progress and queues', async () => {
    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/roadmap']}>
        <Routes>
          <Route path="/student/projects/:projectId/roadmap" element={<StudentRoadmap />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('35%')).toBeInTheDocument();
      expect(screen.getByText(/Sequential Stage Gates/i)).toBeInTheDocument();
      expect(screen.getByText(/Active In Progress/i)).toBeInTheDocument();
      expect(screen.getByText(/Next in Queue/i)).toBeInTheDocument();
    });
  });

  // 8. S25 Documents
  it('renders S25 documents list and supports download action', async () => {
    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/documents']}>
        <Routes>
          <Route path="/student/projects/:projectId/documents" element={<StudentDocuments />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Master Architecture Blueprint')).toBeInTheDocument();
      expect(screen.getByText('+ New Document')).toBeInTheDocument();
    });

    const dlBtn = screen.getByRole('button', { name: /📥 .md/i });
    fireEvent.click(dlBtn);
    expect(api.downloadDocument).toHaveBeenCalledWith(
      'proj-123',
      'doc-1',
      'master_architecture.md'
    );
  });

  // 9. S26 Document Detail
  it('renders S26 document detail and switches between preview and edit mode', async () => {
    render(
      <MemoryRouter initialEntries={['/student/projects/proj-123/documents/doc-1']}>
        <Routes>
          <Route path="/student/projects/:projectId/documents/:documentId" element={<StudentDocumentDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Master Architecture Blueprint')).toBeInTheDocument();
      expect(screen.getByText('System architecture details.')).toBeInTheDocument();
    });

    // Switch to edit mode
    const editTab = screen.getByRole('tab', { name: /Edit Document/i });
    fireEvent.click(editTab);

    expect(screen.getByPlaceholderText(/# Enter markdown content.../i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Save & Bump Version/i })).toBeInTheDocument();
  });
});
