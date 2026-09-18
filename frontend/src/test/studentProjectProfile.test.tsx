import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentProjectProfile } from '@/pages/Student/StudentProjectProfile/StudentProjectProfile';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';
import * as api from '@/lib/api';
import type {
  ProjectResponse,
  ProjectOverviewResponse,
  ProjectDefinitionCatalogItem,
} from '@/lib/api/types';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getProject: vi.fn(),
    getProjectOverview: vi.fn(),
    getMentorProjectDefinition: vi.fn(),
    updateProject: vi.fn(),
  };
});

const mockIndependentProject: ProjectResponse = {
  id: 'proj-101',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Autonomous Solar Rover',
  problem: 'Remote arid terrain ground monitoring bottlenecks.',
  proposed_solution: 'Solar-powered autonomous rover with edge computer vision.',
  complexity: 'INTERMEDIATE',
  current_phase: 'IDEA',
  health: 'HEALTHY',
  progress_percentage: 15,
  status: 'ACTIVE',
  deadline: '2026-12-15T00:00:00.000Z',
  started_at: '2026-09-01T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-09-01T00:00:00.000Z',
  updated_at: '2026-09-10T00:00:00.000Z',
};

const mockMentorProject: ProjectResponse = {
  id: 'proj-102',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: 'def-505',
  source_definition_version_id: 'ver-909',
  name: 'EcoTrack IoT Hydrology',
  problem: 'Urban stormwater runoff pollution.',
  proposed_solution: 'LoRaWAN IoT water quality sensing network.',
  complexity: 'ADVANCED',
  current_phase: 'ASSESSMENT',
  health: 'WARNING',
  progress_percentage: 25,
  status: 'ACTIVE',
  deadline: '2026-11-20T00:00:00.000Z',
  started_at: '2026-08-15T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-08-15T00:00:00.000Z',
  updated_at: '2026-09-11T00:00:00.000Z',
};

const mockOverview: ProjectOverviewResponse = {
  id: 'proj-101',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: null,
  name: 'Autonomous Solar Rover',
  problem: 'Remote arid terrain ground monitoring bottlenecks.',
  proposed_solution: 'Solar-powered autonomous rover with edge computer vision.',
  complexity: 'INTERMEDIATE',
  current_phase: 'IDEA',
  health: 'HEALTHY',
  progress_percentage: 15,
  status: 'ACTIVE',
  deadline: '2026-12-15T00:00:00.000Z',
  days_remaining: 92,
  profile: {
    objective: 'Autonomous ground monitoring without grid power dependencies.',
    scope: 'Prototype mechanical rover platform with solar recharging.',
    expected_outcome: 'Continuous 48-hour autonomous terrain survey.',
    constraints: 'Weight under 15kg, power budget 100W peak.',
    assumptions: 'Minimum 5 hours daily direct solar irradiance.',
    target_users: 'Geological field researchers',
  },
  technologies: [
    {
      id: 'tech-1',
      technology_id: 'ROS2',
      category: 'Framework',
      purpose: 'Robotics middleware',
      why_selected: 'Standardized distributed nodes',
    },
    {
      id: 'tech-2',
      technology_id: 'Python',
      category: 'Language',
      purpose: 'Edge inference scripting',
      why_selected: 'Broad ecosystem support',
    },
  ],
  recent_activity: {},
};

const mockMentorDefinition: ProjectDefinitionCatalogItem = {
  id: 'def-505',
  name: 'EcoTrack IoT Hydrology Framework',
  status: 'ACTIVE',
  version_number: 2,
  problem: 'Urban runoff pollution',
  proposed_solution: 'LoRaWAN water quality nodes',
  complexity: 'ADVANCED',
  description: 'Full-stack IoT sensor architecture for watershed monitoring',
  duration: '12 weeks',
  constraints: 'IP67 enclosure requirement',
  assumptions: 'Local LoRaWAN gateway coverage',
  technology_snapshot: [],
  created_at: '2026-08-01T00:00:00.000Z',
  updated_at: '2026-08-10T00:00:00.000Z',
};

const mockAuthContext: AuthContextValue = {
  status: 'AUTHENTICATED',
  session: {
    access_token: 'mock-token',
    refresh_token: 'mock-refresh',
    expires_in: 3600,
    token_type: 'bearer',
    user: { id: 'student-123', email: 'alex@example.com' } as unknown as User,
  },
  supabaseUser: { id: 'student-123', email: 'alex@example.com' } as unknown as User,
  user: {
    id: 'student-123',
    email: 'alex@example.com',
    role: 'STUDENT',
    status: 'ACTIVE',
    fullName: 'Alex Student',
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

function renderProfile(projectId = 'proj-101') {
  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <MemoryRouter initialEntries={[`/student/projects/${projectId}`]}>
        <Routes>
          <Route path="/student/projects/:projectId" element={<StudentProjectProfile />} />
          <Route path="/student/projects" element={<div>My Projects List</div>} />
          <Route path="/student/dashboard" element={<div>Student Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('S06 — Student Project Information / Profile (/student/projects/:projectId)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.getProject).mockResolvedValue(mockIndependentProject);
    vi.mocked(api.getProjectOverview).mockResolvedValue(mockOverview);
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockMentorDefinition);
    vi.mocked(api.updateProject).mockResolvedValue(mockIndependentProject);
  });

  it('1. renders loading skeleton while API requests are in flight', () => {
    vi.mocked(api.getProject).mockReturnValue(new Promise(() => {}));
    renderProfile('proj-101');

    expect(screen.getByRole('status', { name: /loading project profile/i })).toBeInTheDocument();
  });

  it('2. calls getProject and getProjectOverview with route projectId', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(api.getProject).toHaveBeenCalledWith('proj-101');
      expect(api.getProjectOverview).toHaveBeenCalledWith('proj-101');
    });
  });

  it('3. renders canonical project identity and metadata for independent project', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Autonomous Solar Rover' })).toBeInTheDocument();
    });

    // Provenance badge
    expect(screen.getAllByText('Independent Project').length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Stage 1 of 8/i).length).toBeGreaterThan(0);

    // Problem & Solution
    expect(screen.getByText('Remote arid terrain ground monitoring bottlenecks.')).toBeInTheDocument();
    expect(screen.getByText('Solar-powered autonomous rover with edge computer vision.')).toBeInTheDocument();

    // Complexity
    expect(screen.getAllByText('INTERMEDIATE').length).toBeGreaterThan(0);

    // Days remaining from overview
    expect(screen.getByText(/92 days remaining/i)).toBeInTheDocument();
  });

  it('4. renders mentor project provenance and version snapshot when project has definition ID', async () => {
    vi.mocked(api.getProject).mockResolvedValue(mockMentorProject);
    vi.mocked(api.getProjectOverview).mockResolvedValue({
      ...mockOverview,
      id: 'proj-102',
      project_definition_id: 'def-505',
    });

    renderProfile('proj-102');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'EcoTrack IoT Hydrology' })).toBeInTheDocument();
    });

    // Provenance indicator
    expect(screen.getAllByText('Mentor Project').length).toBeGreaterThan(0);
    expect(api.getMentorProjectDefinition).toHaveBeenCalledWith('def-505');

    // Shows source definition name & version
    expect(screen.getByText('EcoTrack IoT Hydrology Framework')).toBeInTheDocument();
    expect(screen.getByText(/Pinned to Version Snapshot #2/i)).toBeInTheDocument();

    // Immutability notice
    expect(screen.getByText(/Immutable Baseline & Instance Isolation/i)).toBeInTheDocument();
  });

  it('5. renders canonical profile objectives, scope, constraints, and technologies from overview', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByText('Autonomous ground monitoring without grid power dependencies.')).toBeInTheDocument();
    });

    expect(screen.getByText('Prototype mechanical rover platform with solar recharging.')).toBeInTheDocument();
    expect(screen.getByText('Continuous 48-hour autonomous terrain survey.')).toBeInTheDocument();
    expect(screen.getByText('Weight under 15kg, power budget 100W peak.')).toBeInTheDocument();
    expect(screen.getByText('Minimum 5 hours daily direct solar irradiance.')).toBeInTheDocument();

    // Real technologies
    expect(screen.getByText('ROS2')).toBeInTheDocument();
    expect(screen.getByText('Robotics middleware')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
  });

  it('6. renders system-controlled fields as read-only with lifecycle notice', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByText('Operational & Lifecycle State')).toBeInTheDocument();
    });

    expect(screen.getByText(/Stage 1: IDEA/i)).toBeInTheDocument();
    expect(screen.getByText('15%')).toBeInTheDocument();
    expect(screen.getAllByText('Healthy').length).toBeGreaterThan(0);
    expect(
      screen.getByText(/These fields are maintained automatically by GrowFlow lifecycle gates/i),
    ).toBeInTheDocument();
  });

  it('7. enters edit mode on Edit button click and initializes form with current values', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Edit Information/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Edit Information/i }));

    expect(screen.getByRole('heading', { level: 2, name: 'Edit Project Information' })).toBeInTheDocument();
    expect(screen.getByText('EDIT MODE')).toBeInTheDocument();

    const nameInput = screen.getByLabelText(/Project Name/i) as HTMLInputElement;
    expect(nameInput.value).toBe('Autonomous Solar Rover');

    const problemInput = screen.getByLabelText(/Problem Statement/i) as HTMLTextAreaElement;
    expect(problemInput.value).toBe('Remote arid terrain ground monitoring bottlenecks.');
  });

  it('8. disables Save button when no changes exist in edit mode', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Edit Information/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Edit Information/i }));

    const saveButton = screen.getByRole('button', { name: /Save Changes/i });
    expect(saveButton).toBeDisabled();
  });

  it('9. enables Save button when fields are modified', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Edit Information/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Edit Information/i }));

    const nameInput = screen.getByLabelText(/Project Name/i);
    fireEvent.change(nameInput, { target: { value: 'Solar Rover Mark II' } });

    const saveButton = screen.getByRole('button', { name: /Save Changes/i });
    expect(saveButton).not.toBeDisabled();
  });

  it('10. validates project name cannot be empty and prevents dispatch', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Edit Information/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Edit Information/i }));

    const nameInput = screen.getByLabelText(/Project Name/i);
    fireEvent.change(nameInput, { target: { value: '   ' } });

    // The form is dirty now (different from initial), so save button is enabled
    const saveButton = screen.getByRole('button', { name: /Save Changes/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Project name is required.')).toBeInTheDocument();
    });
    expect(api.updateProject).not.toHaveBeenCalled();
  });

  it('11. dispatches updateProject and reconciles UI with updated response on valid save', async () => {
    const updatedResponse: ProjectResponse = {
      ...mockIndependentProject,
      name: 'Autonomous Solar Rover Mk II',
      problem: 'Updated problem statement.',
      complexity: 'ADVANCED',
    };
    vi.mocked(api.updateProject).mockResolvedValue(updatedResponse);

    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Edit Information/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Edit Information/i }));

    const nameInput = screen.getByLabelText(/Project Name/i);
    fireEvent.change(nameInput, { target: { value: 'Autonomous Solar Rover Mk II' } });

    const problemInput = screen.getByLabelText(/Problem Statement/i);
    fireEvent.change(problemInput, { target: { value: 'Updated problem statement.' } });

    const saveButton = screen.getByRole('button', { name: /Save Changes/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(api.updateProject).toHaveBeenCalledWith(
        'proj-101',
        expect.objectContaining({
          name: 'Autonomous Solar Rover Mk II',
          problem: 'Updated problem statement.',
        }),
      );
    });

    // Exits edit mode and displays updated values
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Autonomous Solar Rover Mk II' })).toBeInTheDocument();
      expect(screen.getByText('Updated problem statement.')).toBeInTheDocument();
    });
  });

  it('12. cancels edit mode and restores canonical data without calling updateProject', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Edit Information/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Edit Information/i }));

    const nameInput = screen.getByLabelText(/Project Name/i);
    fireEvent.change(nameInput, { target: { value: 'Discarded Name' } });

    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    fireEvent.click(cancelButton);

    // Returns to view mode with original name
    expect(screen.queryByText('EDIT MODE')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: 'Autonomous Solar Rover' })).toBeInTheDocument();
    expect(api.updateProject).not.toHaveBeenCalled();
  });

  it('13. displays server error and preserves user input when updateProject fails', async () => {
    vi.mocked(api.updateProject).mockRejectedValue(
      new Error('Project name already exists in your workspace.'),
    );

    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Edit Information/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Edit Information/i }));

    const nameInput = screen.getByLabelText(/Project Name/i);
    fireEvent.change(nameInput, { target: { value: 'Colliding Name' } });

    const saveButton = screen.getByRole('button', { name: /Save Changes/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Project name already exists in your workspace.')).toBeInTheDocument();
    });

    // Remains in edit mode with input preserved
    expect(screen.getByText('EDIT MODE')).toBeInTheDocument();
    expect((screen.getByLabelText(/Project Name/i) as HTMLInputElement).value).toBe('Colliding Name');
  });

  it('14. renders 404 Not Found state when project does not exist', async () => {
    vi.mocked(api.getProject).mockRejectedValue(
      new Error('Project not found (404).'),
    );

    renderProfile('proj-nonexistent');

    await waitFor(() => {
      expect(screen.getByText('Project Not Found')).toBeInTheDocument();
    });

    expect(screen.getByRole('link', { name: /Return to My Projects/i })).toBeInTheDocument();
  });

  it('15. renders 403 Forbidden state when user lacks access to project', async () => {
    vi.mocked(api.getProject).mockRejectedValue(
      new Error('Access to this project is denied (403).'),
    );

    renderProfile('proj-forbidden');

    await waitFor(() => {
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });

    expect(screen.getByRole('link', { name: /Return to My Projects/i })).toBeInTheDocument();
  });

  it('16. renders network error state with retry action', async () => {
    vi.mocked(api.getProject).mockRejectedValueOnce(
      new Error('Network error: connection refused.'),
    );

    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByText('Unable to Load Project Profile')).toBeInTheDocument();
    });

    const retryButton = screen.getByRole('button', { name: /Retry Loading/i });
    expect(retryButton).toBeInTheDocument();

    // On retry, getProject succeeds
    vi.mocked(api.getProject).mockResolvedValue(mockIndependentProject);
    fireEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Autonomous Solar Rover' })).toBeInTheDocument();
    });
  });

  it('17. provides breadcrumb navigation back to student projects collection', async () => {
    renderProfile('proj-101');

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Back to Projects/i })).toBeInTheDocument();
    });

    const backLink = screen.getByRole('link', { name: /Back to Projects/i });
    expect(backLink).toHaveAttribute('href', '/student/projects');
  });
});
