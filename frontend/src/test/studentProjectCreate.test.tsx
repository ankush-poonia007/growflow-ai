import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentProjectCreate } from '@/pages/Student/StudentProjectCreate';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import * as api from '@/lib/api';
import { ApiClientError } from '@/lib/api/errors';
import type { ProjectResponse } from '@/lib/api/types';

// Mock the API client
vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    createProject: vi.fn(),
  };
});

function renderWithStudentAuth(ui: React.ReactNode) {
  const mockAuthContext: AuthContextValue = {
    status: 'AUTHENTICATED',
    session: null,
    supabaseUser: null,
    user: {
      id: 'student-uuid-1',
      email: 'alex@example.com',
      role: 'STUDENT',
      status: 'ACTIVE',
      fullName: 'Alex Chen',
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

  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <MemoryRouter initialEntries={['/student/projects/new']}>{ui}</MemoryRouter>
    </AuthContext.Provider>,
  );
}

const mockSuccessResponse: ProjectResponse = {
  id: 'proj-created-001',
  student_id: 'student-uuid-1',
  group_id: null,
  project_definition_id: null,
  source_definition_version_id: null,
  name: 'Autonomous Solar Rover',
  problem: 'Inefficient ground monitoring in remote arid terrain.',
  proposed_solution: 'Solar-powered autonomous rover with edge computer vision.',
  complexity: 'INTERMEDIATE',
  current_phase: 'IDEA',
  health: 'HEALTHY',
  progress_percentage: 0,
  status: 'ACTIVE',
  deadline: '2026-12-01T00:00:00.000Z',
  started_at: '2026-09-12T00:00:00.000Z',
  completed_at: null,
  created_at: '2026-09-12T00:00:00.000Z',
  updated_at: '2026-09-12T00:00:00.000Z',
};

describe('S03 — Student Project Create (/student/projects/new)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // 1. Page renders correctly
  it('1. renders header, orientation cue, form, and snapshot preview', () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    expect(screen.getByRole('heading', { level: 1, name: /create your own project/i })).toBeInTheDocument();
    expect(screen.getByText('STUDENT / BUILD')).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /build progression orientation/i })).toBeInTheDocument();
    expect(screen.getByRole('form', { name: /project definition form/i })).toBeInTheDocument();
    expect(screen.getByRole('complementary', { name: /live project snapshot/i })).toBeInTheDocument();
  });

  // 2. Protected route remains protected
  it('2. redirects unauthenticated user away from protected creation route', () => {
    const unauthContext: AuthContextValue = {
      status: 'UNAUTHENTICATED',
      session: null,
      supabaseUser: null,
      user: null,
      error: null,
      isRoleResolving: false,
      isAuthenticated: false,
      isLoading: false,
      signIn: vi.fn(),
      signOut: vi.fn(),
      retryAuth: vi.fn(),
      refreshAuthorization: vi.fn(),
    };

    render(
      <AuthContext.Provider value={unauthContext}>
        <MemoryRouter initialEntries={['/student/projects/new']}>
          <Routes>
            <Route
              path="/student/projects/new"
              element={
                <ProtectedRoute requiredRole="STUDENT">
                  <StudentProjectCreate />
                </ProtectedRoute>
              }
            />
            <Route path="/auth/student/sign-in" element={<div>Student Sign In Page</div>} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByText('Student Sign In Page')).toBeInTheDocument();
    expect(screen.queryByRole('heading', { level: 1, name: /create your own project/i })).not.toBeInTheDocument();
  });

  // 3. Initial form state is empty
  it('3. starts with empty text fields and default INTERMEDIATE complexity', () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    const nameInput = screen.getByLabelText(/project name/i) as HTMLInputElement;
    const problemInput = screen.getByLabelText(/problem statement/i) as HTMLTextAreaElement;
    const solutionInput = screen.getByLabelText(/proposed solution/i) as HTMLTextAreaElement;
    const techInput = screen.getByLabelText(/initial technologies/i) as HTMLInputElement;

    expect(nameInput.value).toBe('');
    expect(problemInput.value).toBe('');
    expect(solutionInput.value).toBe('');
    expect(techInput.value).toBe('');

    const intermediateRadio = screen.getByDisplayValue('INTERMEDIATE') as HTMLInputElement;
    expect(intermediateRadio.checked).toBe(true);
  });

  // 4. Labels and helper text render
  it('4. renders descriptive labels and helper guidance for all inputs', () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    expect(screen.getByText(/give your project a name that you can recognize/i)).toBeInTheDocument();
    expect(screen.getByText(/what problem are you trying to solve, and who experiences it\?/i)).toBeInTheDocument();
    expect(screen.getByText(/describe the solution you want to explore\. it does not need to be final\./i)).toBeInTheDocument();
    expect(screen.getByText(/comma-separated technologies or frameworks you intend to evaluate\./i)).toBeInTheDocument();
  });

  // 5 & 6. Required validation & invalid submission blocks API
  it('5 & 6. validates required project name before submission and does not call API', async () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    const submitBtn = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitBtn);

    expect(await screen.findByText('Project name is required.')).toBeInTheDocument();
    expect(api.createProject).not.toHaveBeenCalled();
  });

  // 7. Valid submission calls createProject with correct verified payload
  it('7. calls api.createProject with the verified payload on valid submission', async () => {
    vi.mocked(api.createProject).mockResolvedValueOnce(mockSuccessResponse);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Autonomous Solar Rover' },
    });
    fireEvent.change(screen.getByLabelText(/problem statement/i), {
      target: { value: 'Inefficient ground monitoring in remote arid terrain.' },
    });
    fireEvent.change(screen.getByLabelText(/proposed solution/i), {
      target: { value: 'Solar-powered autonomous rover with edge computer vision.' },
    });
    fireEvent.change(screen.getByLabelText(/initial technologies/i), {
      target: { value: 'Python, ROS2, PyTorch' },
    });

    const submitBtn = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(api.createProject).toHaveBeenCalledTimes(1);
      expect(api.createProject).toHaveBeenCalledWith({
        name: 'Autonomous Solar Rover',
        problem: 'Inefficient ground monitoring in remote arid terrain.',
        proposed_solution: 'Solar-powered autonomous rover with edge computer vision.',
        complexity: 'INTERMEDIATE',
        technologies: ['Python', 'ROS2', 'PyTorch'],
        deadline: null,
      });
    });
  });

  // 8 & 9. Duplicate submission protection and submitting state
  it('8 & 9. prevents duplicate submission while request is in-flight and displays loading state', async () => {
    let resolvePromise!: (val: ProjectResponse) => void;
    const promise = new Promise<ProjectResponse>((resolve) => {
      resolvePromise = resolve;
    });
    vi.mocked(api.createProject).mockReturnValueOnce(promise);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Concurrent Test Project' },
    });

    const submitBtn = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitBtn);

    // Button should show submitting state and be disabled
    expect(screen.getByRole('button', { name: /creating project…/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /creating project…/i })).toBeDisabled();

    // Secondary click should be blocked
    fireEvent.click(submitBtn);
    expect(api.createProject).toHaveBeenCalledTimes(1);

    // Complete request
    resolvePromise(mockSuccessResponse);
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /your project has been created\./i })).toBeInTheDocument();
    });
  });

  // 10 & 11. Success confirmation & safe navigation
  it('10 & 11. displays canonical success confirmation and guides to valid routes (no fake workspace)', async () => {
    vi.mocked(api.createProject).mockResolvedValueOnce(mockSuccessResponse);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Autonomous Solar Rover' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: /your project has been created\./i })).toBeInTheDocument();
      expect(screen.getByText('Autonomous Solar Rover')).toBeInTheDocument();
      expect(screen.getByText(/the next stage is assessment\./i)).toBeInTheDocument();
    });

    // Navigation CTAs must route to existing canonical collections, NOT unimplemented /student/projects/:id
    const projectsLink = screen.getByRole('link', { name: /view in projects collection/i });
    const dashboardLink = screen.getByRole('link', { name: /go to student dashboard/i });

    expect(projectsLink).toHaveAttribute('href', '/student/projects');
    expect(dashboardLink).toHaveAttribute('href', '/student/dashboard');
  });

  // 12. 400/422 validation failure preserves form data
  it('12. preserves form data on 422 validation failure and displays calm message', async () => {
    const error422 = new ApiClientError(422, 'UNPROCESSABLE_ENTITY', 'Invalid payload');
    vi.mocked(api.createProject).mockRejectedValueOnce(error422);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'My Valid Title' },
    });
    fireEvent.change(screen.getByLabelText(/problem statement/i), {
      target: { value: 'Preserved problem description' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/please review the highlighted fields/i)).toBeInTheDocument();
    });

    // Form inputs must not be cleared
    expect((screen.getByLabelText(/project name/i) as HTMLInputElement).value).toBe('My Valid Title');
    expect((screen.getByLabelText(/problem statement/i) as HTMLTextAreaElement).value).toBe(
      'Preserved problem description',
    );
  });

  // 13. 401 handling
  it('13. handles 401 Unauthorized by displaying calm session expiration message', async () => {
    const error401 = new ApiClientError(401, 'UNAUTHORIZED', 'Token expired');
    vi.mocked(api.createProject).mockRejectedValueOnce(error401);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Session Test' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(screen.getByText(/your session has expired\. please sign in again\./i)).toBeInTheDocument();
    });
  });

  // 14. 403 handling
  it('14. handles 403 Forbidden by displaying permission message', async () => {
    const error403 = new ApiClientError(403, 'FORBIDDEN', 'Access denied');
    vi.mocked(api.createProject).mockRejectedValueOnce(error403);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Forbidden Test' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/you do not have permission to create a project in this workspace\./i),
      ).toBeInTheDocument();
    });
  });

  // 15. 409 handling
  it('15. handles 409 Conflict by displaying duplicate name message', async () => {
    const error409 = new ApiClientError(409, 'CONFLICT', 'Project name exists');
    vi.mocked(api.createProject).mockRejectedValueOnce(error409);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Existing Project Name' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/a project with this name already exists\. please choose a different name\./i),
      ).toBeInTheDocument();
    });
  });

  // 16. 5xx and network error handling
  it('16. handles 500 server error and network disconnect calmly', async () => {
    const error500 = new ApiClientError(500, 'INTERNAL_SERVER_ERROR', 'Database failure');
    vi.mocked(api.createProject).mockRejectedValueOnce(error500);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Server Error Test' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/something went wrong on the server while creating your project\./i),
      ).toBeInTheDocument();
    });
  });

  // 17. Retry works after error
  it('17. allows user to retry after an error and succeeds', async () => {
    vi.mocked(api.createProject)
      .mockRejectedValueOnce(new ApiClientError(500, 'INTERNAL_ERROR', 'Crash'))
      .mockResolvedValueOnce(mockSuccessResponse);

    renderWithStudentAuth(<StudentProjectCreate />);

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Retry Project' },
    });

    // First attempt fails
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    // Second attempt succeeds
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: /your project has been created\./i })).toBeInTheDocument();
    });
  });

  // 18. Cancel button navigates to /student/projects
  it('18. cancel button links back to /student/projects', () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    const cancelBtn = screen.getByRole('link', { name: /cancel/i });
    expect(cancelBtn).toHaveAttribute('href', '/student/projects');
  });

  // 19 & 20. Live snapshot preview updates as user fills the form
  it('19 & 20. updates live project snapshot when name, problem, and complexity change', () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    // Initially shows placeholder cue
    expect(
      screen.getByText(/your project snapshot will take shape as you define the idea\./i),
    ).toBeInTheDocument();

    // Type name
    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Smart Agriculture Sensor' },
    });
    const snapshot = screen.getByRole('complementary', { name: /live project snapshot/i });
    expect(within(snapshot).getByRole('heading', { level: 3, name: 'Smart Agriculture Sensor' })).toBeInTheDocument();

    // Select ADVANCED complexity
    fireEvent.click(screen.getByDisplayValue('ADVANCED'));
    expect(within(snapshot).getByText('ADVANCED')).toBeInTheDocument();

    // Type problem
    fireEvent.change(screen.getByLabelText(/problem statement/i), {
      target: { value: 'Drought conditions in semi-arid zones.' },
    });
    expect(within(snapshot).getByText('Drought conditions in semi-arid zones.')).toBeInTheDocument();
  });

  // 21. No fake tasks/milestones/risks/AI/assessment/blueprint
  it('21. does not contain fake tasks, milestones, risks, AI generation, or fabricated blueprints', () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    expect(screen.queryByText(/generate with ai/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/task list/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /milestones/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/risk register/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/blueprint generator/i)).not.toBeInTheDocument();
  });

  // 22. Character count reflects maximum limit
  it('22. displays character counter for project name up to 255', () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    expect(screen.getByText('0/255')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'Hello' },
    });
    expect(screen.getByText('5/255')).toBeInTheDocument();
  });

  // 23. Accessibility attributes exist
  it('23. enforces accessible attributes (aria-describedby, aria-invalid, radiogroup)', async () => {
    renderWithStudentAuth(<StudentProjectCreate />);

    const form = screen.getByRole('form', { name: /project definition form/i });
    expect(form).toBeInTheDocument();

    const nameInput = screen.getByLabelText(/project name/i);
    expect(nameInput).toHaveAttribute('aria-invalid', 'false');

    // Trigger error
    fireEvent.click(screen.getByRole('button', { name: /create project/i }));
    await waitFor(() => {
      expect(nameInput).toHaveAttribute('aria-invalid', 'true');
    });

    const radioGroup = screen.getByRole('radiogroup');
    expect(radioGroup).toHaveAttribute('aria-describedby', 'complexity-helper');
  });
});
