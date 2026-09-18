import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentMentorProjectDetail } from '@/pages/Student/StudentMentorProjectDetail';
import { ProtectedRoute } from '@/auth/ProtectedRoute';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';
import * as api from '@/lib/api';
import { ApiClientError } from '@/lib/api/errors';
import type { ProjectDefinitionCatalogItem, ProjectResponse } from '@/lib/api/types';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getMentorProjectDefinition: vi.fn(),
    selectMentorProject: vi.fn(),
  };
});

const mockDefinition: ProjectDefinitionCatalogItem = {
  id: 'def-101',
  name: 'Autonomous Precision Drone',
  status: 'ACTIVE',
  version_number: 1,
  problem: 'Inefficient crop assessment and aerial disease spotting.',
  proposed_solution: 'Autonomous multispectral camera drone with edge inference.',
  complexity: 'INTERMEDIATE',
  description: 'Design and deploy an aerial imaging drone that automates disease detection.',
  duration: '8 weeks',
  constraints: 'Requires outdoor open test field',
  assumptions: 'Basic familiarity with Python and ROS',
  technology_snapshot: [
    { name: 'ROS2', category: 'Framework', purpose: 'Robotics middleware' },
    'PyTorch',
    'OpenCV',
  ],
  created_at: '2026-09-05T10:00:00.000Z',
  updated_at: '2026-09-05T10:00:00.000Z',
};

const mockProjectResponse: ProjectResponse = {
  id: 'proj-501',
  student_id: 'student-123',
  group_id: null,
  project_definition_id: 'def-101',
  source_definition_version_id: 'ver-001',
  name: 'Autonomous Precision Drone',
  problem: 'Inefficient crop assessment and aerial disease spotting.',
  proposed_solution: 'Autonomous multispectral camera drone with edge inference.',
  complexity: 'INTERMEDIATE',
  current_phase: 'IDEA',
  health: 'HEALTHY',
  progress_percentage: 0,
  status: 'ACTIVE',
  deadline: null,
  started_at: null,
  completed_at: null,
  created_at: '2026-09-12T10:00:00.000Z',
  updated_at: '2026-09-12T10:00:00.000Z',
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

function renderDetail(definitionId = 'def-101') {
  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <MemoryRouter initialEntries={[`/student/projects/mentor-catalog/${definitionId}`]}>
        <Routes>
          <Route
            path="/student/projects/mentor-catalog/:definitionId"
            element={<StudentMentorProjectDetail />}
          />
          <Route path="/student/projects/mentor-catalog" element={<div>Mentor Catalog Page</div>} />
          <Route path="/student/projects" element={<div>My Projects Page</div>} />
          <Route path="/student/dashboard" element={<div>Student Dashboard Page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('S05 — Student Mentor Project Detail & Selection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.scrollTo = vi.fn();
  });

  // 1 & 2. Route & Parameter Handling
  it('1. handles :definitionId parameter and invokes getMentorProjectDefinition with it', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(api.getMentorProjectDefinition).toHaveBeenCalledWith('def-101');
    });
  });

  // 3. Initial Loading Skeleton
  it('2. displays loading skeleton while definition request is in flight', () => {
    vi.mocked(api.getMentorProjectDefinition).mockReturnValue(new Promise(() => {}));
    renderDetail('def-101');

    expect(screen.getByLabelText(/loading mentor project details/i)).toBeInTheDocument();
  });

  // 4. Successful Detail Loading & Header
  it('3. renders project title, provenance badge, complexity, and duration in header', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /autonomous precision drone/i })).toBeInTheDocument();
    });

    expect(screen.getByText('MENTOR PROJECT')).toBeInTheDocument();
    expect(screen.getAllByText('INTERMEDIATE')[0]).toBeInTheDocument();
    expect(screen.getAllByText('8 weeks')[0]).toBeInTheDocument();
  });

  // 5. Problem Statement Rendering
  it('4. renders the actual canonical problem statement', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/inefficient crop assessment and aerial disease spotting/i)).toBeInTheDocument();
    });
  });

  // 6. Proposed Solution Rendering
  it('5. renders the actual canonical proposed solution', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/autonomous multispectral camera drone with edge inference/i)).toBeInTheDocument();
    });
  });

  // 7. Description Rendering
  it('6. renders the actual canonical detailed description', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/design and deploy an aerial imaging drone that automates disease detection/i)).toBeInTheDocument();
    });
  });

  // 8. Technology Rendering (Populated and Empty)
  it('7. renders technologies from technology_snapshot', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText('ROS2')).toBeInTheDocument();
    });
    expect(screen.getByText('Robotics middleware')).toBeInTheDocument();
    expect(screen.getByText('PyTorch')).toBeInTheDocument();
    expect(screen.getByText('OpenCV')).toBeInTheDocument();
  });

  it('8. renders quiet empty state when technology_snapshot is empty', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue({
      ...mockDefinition,
      technology_snapshot: [],
    });
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/no specific technologies pre-selected by mentor/i)).toBeInTheDocument();
    });
  });

  // 9. Constraints Rendering (Populated and Empty)
  it('9. renders constraints when present and quiet state when empty', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue({
      ...mockDefinition,
      constraints: '',
    });
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/no specific constraints provided/i)).toBeInTheDocument();
    });
  });

  // 10. Assumptions Rendering (Populated and Empty)
  it('10. renders assumptions when present and quiet state when empty', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue({
      ...mockDefinition,
      assumptions: '',
    });
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/no specific assumptions provided/i)).toBeInTheDocument();
    });
  });

  // 11. Metadata Rendering
  it('11. renders metadata values without dominant version emphasis', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText('v1')).toBeInTheDocument();
    });
    expect(screen.getByText('ACTIVE')).toBeInTheDocument();
  });

  // 12. Privacy Boundary Check
  it('12. strictly does NOT render owner_mentor_id, created_by, or current_version_id', async () => {
    const rawWithLeakedFields = {
      ...mockDefinition,
      owner_mentor_id: 'mentor-secret-uuid-999',
      created_by: 'creator-secret-uuid-888',
      current_version_id: 'ver-internal-uuid-777',
    };
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(rawWithLeakedFields as unknown as ProjectDefinitionCatalogItem);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(mockDefinition.name)).toBeInTheDocument();
    });

    expect(screen.queryByText('mentor-secret-uuid-999')).not.toBeInTheDocument();
    expect(screen.queryByText('creator-secret-uuid-888')).not.toBeInTheDocument();
    expect(screen.queryByText('ver-internal-uuid-777')).not.toBeInTheDocument();
  });

  // 13. 404 Handling
  it('13. renders calm unavailable state on 404 without revealing draft/archived status', async () => {
    const err = new ApiClientError(404, 'PROJECT_DEFINITION_NOT_FOUND', 'Project definition not found.');
    vi.mocked(api.getMentorProjectDefinition).mockRejectedValue(err);
    renderDetail('def-999');

    await waitFor(() => {
      expect(screen.getByText(/mentor project not available/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('link', { name: /back to mentor projects/i })).toBeInTheDocument();
    expect(screen.queryByText(/draft/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/archived/i)).not.toBeInTheDocument();
  });

  // 14. 403 Handling
  it('14. renders access restricted state on 403', async () => {
    const err = new ApiClientError(403, 'AUTH_FORBIDDEN_ROLE', 'Forbidden role.');
    vi.mocked(api.getMentorProjectDefinition).mockRejectedValue(err);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/access restricted/i)).toBeInTheDocument();
    });
  });

  // 15 & 16. 5xx & Network Error Handling with Retry
  it('15. renders network error message and provides working retry button', async () => {
    const networkErr = new ApiClientError(0, 'NETWORK_ERROR', 'Network error');
    vi.mocked(api.getMentorProjectDefinition)
      .mockRejectedValueOnce(networkErr)
      .mockResolvedValueOnce(mockDefinition);

    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/unable to connect to growflow services/i)).toBeInTheDocument();
    });

    const retryBtn = screen.getByRole('button', { name: /retry loading/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText(mockDefinition.name)).toBeInTheDocument();
    });
    expect(api.getMentorProjectDefinition).toHaveBeenCalledTimes(2);
  });

  // 18. Selection Button Idle State
  it('16. renders idle "Select Project" button with accurate supporting copy', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select project/i })).toBeInTheDocument();
    });

    expect(
      screen.getByText(/selecting this project creates your student project from the currently published mentor definition/i),
    ).toBeInTheDocument();
  });

  // 19 & 20. Selection In-Flight Loading
  it('17. disables button and shows loading state while selection POST is in flight', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    vi.mocked(api.selectMentorProject).mockReturnValue(new Promise(() => {}));

    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select project/i })).toBeInTheDocument();
    });

    const selectBtn = screen.getByRole('button', { name: /select project/i });
    fireEvent.click(selectBtn);

    expect(api.selectMentorProject).toHaveBeenCalledWith('def-101');
    expect(screen.getByText(/creating project\.\.\./i)).toBeInTheDocument();
    expect(selectBtn).toBeDisabled();
  });

  // 21 & 22. Successful Selection Lifecycle & Success State
  it('18. transitions to success confirmation displaying actual canonical ProjectResponse values', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    vi.mocked(api.selectMentorProject).mockResolvedValue(mockProjectResponse);

    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select project/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /select project/i }));

    await waitFor(() => {
      expect(screen.getByText(/project created successfully!/i)).toBeInTheDocument();
    });

    // Validates canonical fields rendered
    expect(screen.getByText(mockProjectResponse.name)).toBeInTheDocument();
    expect(screen.getByText(mockProjectResponse.id)).toBeInTheDocument();
    expect(screen.getByText('IDEA')).toBeInTheDocument();
    expect(screen.getByText('HEALTHY')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();

    // CTAs
    expect(screen.getByRole('link', { name: /view in my projects/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /browse more mentor projects/i })).toBeInTheDocument();
  });

  // 23 & 24. 409 PROJECT_ALREADY_SELECTED Handling
  it('19. handles 409 Conflict with dedicated non-destructive duplicate banner and portfolio link', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    const conflictErr = new ApiClientError(
      409,
      'PROJECT_ALREADY_SELECTED',
      'Student already has an active instance of this project definition.',
    );
    vi.mocked(api.selectMentorProject).mockRejectedValue(conflictErr);

    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select project/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /select project/i }));

    await waitFor(() => {
      expect(screen.getByText(/you've already selected this mentor project/i)).toBeInTheDocument();
    });

    expect(
      screen.getByText(/an active student project instance for this definition already exists in your workspace/i),
    ).toBeInTheDocument();

    expect(screen.getByRole('link', { name: /view in my projects/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /browse mentor catalog/i })).toBeInTheDocument();
  });

  // 25 & 26. Breadcrumb & Back Navigation
  it('20. renders working back link returning to /student/projects/mentor-catalog', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('link', { name: /back to mentor projects/i })).toBeInTheDocument();
    });

    const backLink = screen.getByRole('link', { name: /back to mentor projects/i });
    expect(backLink).toHaveAttribute('href', '/student/projects/mentor-catalog');
  });

  // 27. Accessibility Semantics
  it('21. contains proper aria and landmark semantics', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    expect(screen.getByRole('navigation', { name: /breadcrumb/i })).toBeInTheDocument();
  });

  // 28. Route protection redirect when unauthenticated
  it('22. protects route and redirects unauthenticated users to student sign-in', () => {
    const unauthContext: AuthContextValue = {
      ...mockAuthContext,
      status: 'UNAUTHENTICATED',
      isAuthenticated: false,
      user: null,
      session: null,
      supabaseUser: null,
    };

    render(
      <AuthContext.Provider value={unauthContext}>
        <MemoryRouter initialEntries={['/student/projects/mentor-catalog/def-101']}>
          <Routes>
            <Route
              path="/student/projects/mentor-catalog/:definitionId"
              element={
                <ProtectedRoute requiredRole="STUDENT">
                  <StudentMentorProjectDetail />
                </ProtectedRoute>
              }
            />
            <Route path="/auth/student/sign-in" element={<div>Student Sign In Page</div>} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByText('Student Sign In Page')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Precision Drone')).not.toBeInTheDocument();
  });

  // 29. 5xx Server Error Handling
  it('23. renders generic error UI with retry button on 500 server error', async () => {
    const serverErr = new ApiClientError(500, 'INTERNAL_SERVER_ERROR', 'Internal server error occurred.');
    vi.mocked(api.getMentorProjectDefinition)
      .mockRejectedValueOnce(serverErr)
      .mockResolvedValueOnce(mockDefinition);

    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByText(/unable to load project definition/i)).toBeInTheDocument();
    });

    const retryBtn = screen.getByRole('button', { name: /retry loading/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText(mockDefinition.name)).toBeInTheDocument();
    });
    expect(api.getMentorProjectDefinition).toHaveBeenCalledTimes(2);
  });

  // 30. Missing / Empty definitionId Parameter
  it('24. renders calm not found state when definitionId is not provided', async () => {
    render(
      <AuthContext.Provider value={mockAuthContext}>
        <MemoryRouter initialEntries={['/student/projects/mentor-catalog/']}>
          <Routes>
            <Route
              path="/student/projects/mentor-catalog/"
              element={<StudentMentorProjectDetail />}
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    await waitFor(() => {
      expect(screen.getByText(/mentor project not available/i)).toBeInTheDocument();
    });
  });

  // 31. Keyboard Navigation
  it('25. supports keyboard focus on the primary select button', async () => {
    vi.mocked(api.getMentorProjectDefinition).mockResolvedValue(mockDefinition);
    renderDetail('def-101');

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select project/i })).toBeInTheDocument();
    });

    const selectBtn = screen.getByRole('button', { name: /select project/i });
    selectBtn.focus();
    expect(selectBtn).toHaveFocus();
  });
});
