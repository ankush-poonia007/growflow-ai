import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { StudentMentorProjectCatalog } from '@/pages/Student/StudentMentorProjectCatalog';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue } from '@/auth/types';
import type { User } from '@supabase/supabase-js';
import * as api from '@/lib/api';
import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { Sidebar } from '@/components/navigation/Sidebar';
import { MobileWorkspaceDrawer } from '@/components/navigation/MobileWorkspaceDrawer';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api')>('@/lib/api');
  return {
    ...actual,
    getMentorProjectCatalog: vi.fn(),
  };
});

const mockItem1: ProjectDefinitionCatalogItem = {
  id: 'def-001',
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
  technology_snapshot: ['ROS2', 'PyTorch', 'C++', 'OpenCV'],
  created_at: '2026-09-05T10:00:00.000Z',
  updated_at: '2026-09-05T10:00:00.000Z',
};

const mockItem2: ProjectDefinitionCatalogItem = {
  id: 'def-002',
  name: 'Quantum Key Distribution Simulator',
  status: 'ACTIVE',
  version_number: 2,
  problem: 'Vulnerability of classical RSA encryption to Shor algorithm.',
  proposed_solution: 'Simulate BB84 quantum key distribution protocol over optical channels.',
  complexity: 'ADVANCED',
  description: 'Simulate quantum cryptographic key generation under eavesdropping attacks.',
  duration: '12 weeks',
  constraints: 'Mathematical quantum simulation only',
  assumptions: 'Knowledge of linear algebra and Dirac notation',
  technology_snapshot: ['Qiskit', 'Python', 'NumPy'],
  created_at: '2026-09-01T12:00:00.000Z',
  updated_at: '2026-09-08T12:00:00.000Z',
};

const mockItem3: ProjectDefinitionCatalogItem = {
  id: 'def-003',
  name: 'Accessible Voice Interface for Dysarthria',
  status: 'ACTIVE',
  version_number: 1,
  problem: 'Standard ASR models fail on atypical and dysarthric speech patterns.',
  proposed_solution: 'Fine-tune Whisper tiny model with personalized voice samples.',
  complexity: 'BEGINNER',
  description: 'Build an accessible speech-to-text converter optimized for dysarthric speakers.',
  duration: '6 weeks',
  constraints: '',
  assumptions: '',
  technology_snapshot: ['HuggingFace', 'Whisper', 'WebAudio API'],
  created_at: '2026-09-09T08:00:00.000Z',
  updated_at: '2026-09-09T08:00:00.000Z',
};

const mockCatalog: ProjectDefinitionCatalogItem[] = [mockItem1, mockItem2, mockItem3];

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

function renderCatalog(initialEntries = ['/student/projects/mentor-catalog']) {
  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route
            path="/student/projects/mentor-catalog"
            element={<StudentMentorProjectCatalog />}
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('S04 — Mentor Project Catalog (/student/projects/mentor-catalog)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('1. renders loading skeleton while catalog request is in flight', () => {
    vi.mocked(api.getMentorProjectCatalog).mockReturnValue(new Promise(() => {}));
    renderCatalog();

    expect(screen.getByLabelText(/loading mentor project catalog/i)).toBeInTheDocument();
  });

  it('2. calls getMentorProjectCatalog exactly once on initial load', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /mentor projects/i })).toBeInTheDocument();
    });

    expect(api.getMentorProjectCatalog).toHaveBeenCalledTimes(1);
  });

  it('3. renders real mentor definitions with MENTOR PROJECT provenance badge', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const provenanceBadges = screen.getAllByText('MENTOR PROJECT');
    expect(provenanceBadges.length).toBe(3);
  });

  it('4. renders name, complexity, duration, description, problem, and technologies', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    expect(screen.getByText('INTERMEDIATE')).toBeInTheDocument();
    expect(screen.getByText('8 weeks')).toBeInTheDocument();
    expect(
      screen.getByText('Design and deploy an aerial imaging drone that automates disease detection.'),
    ).toBeInTheDocument();
    expect(screen.getByText('ROS2')).toBeInTheDocument();
    expect(screen.getByText('PyTorch')).toBeInTheDocument();
  });

  it('5. handles missing optional fields gracefully without crashing', async () => {
    const minimalItem: ProjectDefinitionCatalogItem = {
      id: 'def-minimal',
      name: 'Minimal Clean Definition',
      status: 'ACTIVE',
      version_number: null,
      problem: '',
      proposed_solution: '',
      complexity: '',
      description: 'A minimal description.',
      duration: '',
      constraints: '',
      assumptions: '',
      technology_snapshot: [],
      created_at: null,
      updated_at: null,
    };

    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue([minimalItem]);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Minimal Clean Definition')).toBeInTheDocument();
    });

    expect(screen.getByText('A minimal description.')).toBeInTheDocument();
    expect(screen.getByText('MENTOR PROJECT')).toBeInTheDocument();
  });

  it('6. filters catalog by search query matching name', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'Quantum' } });

    expect(screen.getByText('Quantum Key Distribution Simulator')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Precision Drone')).not.toBeInTheDocument();
    expect(screen.queryByText('Accessible Voice Interface for Dysarthria')).not.toBeInTheDocument();
  });

  it('7. filters catalog by search query matching problem', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'crop assessment' } });

    expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    expect(screen.queryByText('Quantum Key Distribution Simulator')).not.toBeInTheDocument();
  });

  it('8. filters catalog by search query matching proposed_solution', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'Whisper tiny model' } });

    expect(screen.getByText('Accessible Voice Interface for Dysarthria')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Precision Drone')).not.toBeInTheDocument();
  });

  it('9. filters catalog by search query matching description', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'eavesdropping attacks' } });

    expect(screen.getByText('Quantum Key Distribution Simulator')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Precision Drone')).not.toBeInTheDocument();
  });

  it('10. performs case-insensitive search', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'qUaNtUm' } });

    expect(screen.getByText('Quantum Key Distribution Simulator')).toBeInTheDocument();
  });

  it('11. filters catalog by complexity (BEGINNER, INTERMEDIATE, ADVANCED)', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const select = screen.getByLabelText(/filter by complexity/i);
    fireEvent.change(select, { target: { value: 'BEGINNER' } });

    expect(screen.getByText('Accessible Voice Interface for Dysarthria')).toBeInTheDocument();
    expect(screen.queryByText('Autonomous Precision Drone')).not.toBeInTheDocument();
    expect(screen.queryByText('Quantum Key Distribution Simulator')).not.toBeInTheDocument();
  });

  it('12. combines search query and complexity filter', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'Drone' } });

    const select = screen.getByLabelText(/filter by complexity/i);
    fireEvent.change(select, { target: { value: 'INTERMEDIATE' } });

    expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();

    // Now change complexity to ADVANCED while search is still 'Drone'
    fireEvent.change(select, { target: { value: 'ADVANCED' } });
    expect(screen.queryByText('Autonomous Precision Drone')).not.toBeInTheDocument();
    expect(screen.getByText(/no mentor projects match your filters/i)).toBeInTheDocument();
  });

  it('13. sorts catalog by recently created (descending) by default', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const headings = screen.getAllByRole('heading', { level: 3 });
    // mockItem3 was created 2026-09-09, mockItem1 was 2026-09-05, mockItem2 was 2026-09-01
    expect(headings[0]).toHaveTextContent('Accessible Voice Interface for Dysarthria');
    expect(headings[1]).toHaveTextContent('Autonomous Precision Drone');
    expect(headings[2]).toHaveTextContent('Quantum Key Distribution Simulator');
  });

  it('14. sorts catalog by Name A-Z', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const sortSelect = screen.getByLabelText(/sort mentor projects/i);
    fireEvent.change(sortSelect, { target: { value: 'name_asc' } });

    const headings = screen.getAllByRole('heading', { level: 3 });
    expect(headings[0]).toHaveTextContent('Accessible Voice Interface for Dysarthria');
    expect(headings[1]).toHaveTextContent('Autonomous Precision Drone');
    expect(headings[2]).toHaveTextContent('Quantum Key Distribution Simulator');
  });

  it('15. sorts catalog by Name Z-A', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const sortSelect = screen.getByLabelText(/sort mentor projects/i);
    fireEvent.change(sortSelect, { target: { value: 'name_desc' } });

    const headings = screen.getAllByRole('heading', { level: 3 });
    expect(headings[0]).toHaveTextContent('Quantum Key Distribution Simulator');
    expect(headings[1]).toHaveTextContent('Autonomous Precision Drone');
    expect(headings[2]).toHaveTextContent('Accessible Voice Interface for Dysarthria');
  });

  it('16. sorts catalog by Complexity (Beginner first and Advanced first)', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const sortSelect = screen.getByLabelText(/sort mentor projects/i);

    // Beginner first: BEGINNER -> INTERMEDIATE -> ADVANCED
    fireEvent.change(sortSelect, { target: { value: 'complexity_asc' } });
    let headings = screen.getAllByRole('heading', { level: 3 });
    expect(headings[0]).toHaveTextContent('Accessible Voice Interface for Dysarthria'); // Beginner
    expect(headings[1]).toHaveTextContent('Autonomous Precision Drone'); // Intermediate
    expect(headings[2]).toHaveTextContent('Quantum Key Distribution Simulator'); // Advanced

    // Advanced first: ADVANCED -> INTERMEDIATE -> BEGINNER
    fireEvent.change(sortSelect, { target: { value: 'complexity_desc' } });
    headings = screen.getAllByRole('heading', { level: 3 });
    expect(headings[0]).toHaveTextContent('Quantum Key Distribution Simulator'); // Advanced
    expect(headings[1]).toHaveTextContent('Autonomous Precision Drone'); // Intermediate
    expect(headings[2]).toHaveTextContent('Accessible Voice Interface for Dysarthria'); // Beginner
  });

  it('17. clears filters when Clear filters button is clicked', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'Quantum' } });

    const clearButton = screen.getByRole('button', { name: /clear filters/i });
    fireEvent.click(clearButton);

    expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    expect(screen.getByText('Quantum Key Distribution Simulator')).toBeInTheDocument();
    expect(screen.getByText('Accessible Voice Interface for Dysarthria')).toBeInTheDocument();
  });

  it('18. initializes filters from URL query parameters (?q=, ?complexity=, ?sort=)', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog(['/student/projects/mentor-catalog?q=Drone&complexity=INTERMEDIATE&sort=name_asc']);

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    expect(screen.queryByText('Quantum Key Distribution Simulator')).not.toBeInTheDocument();
    const searchInput = screen.getByPlaceholderText(/search mentor projects/i) as HTMLInputElement;
    expect(searchInput.value).toBe('Drone');
  });

  it('19. falls back to defaults when URL parameters are invalid', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog(['/student/projects/mentor-catalog?complexity=INVALID_COMPLEXITY&sort=INVALID_SORT']);

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    // All three items should render because complexity fell back to 'ALL'
    expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    expect(screen.getByText('Quantum Key Distribution Simulator')).toBeInTheDocument();
    expect(screen.getByText('Accessible Voice Interface for Dysarthria')).toBeInTheDocument();
  });

  it('20. renders empty backend catalog state when catalog array is empty', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue([]);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText(/no mentor projects available yet/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/mentor-defined opportunities are not currently available/i)).toBeInTheDocument();
  });

  it('21. renders no matches state when filters exclude all items', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search mentor projects/i);
    fireEvent.change(searchInput, { target: { value: 'NonexistentProjectQueryXYZ' } });

    expect(screen.getByText(/no mentor projects match your filters/i)).toBeInTheDocument();
    const clearButtons = screen.getAllByRole('button', { name: /clear filters/i });
    expect(clearButtons.length).toBeGreaterThan(0);
  });

  it('22. displays calm error message and allows retry on 401 unauthorized', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockRejectedValue(new Error('401 Unauthorized'));
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByText(/your session has expired\. please sign in again/i)).toBeInTheDocument();
  });

  it('23. displays calm error message on 403 forbidden', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockRejectedValue(new Error('403 Forbidden'));
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByText(/you don't have permission to browse mentor projects/i)).toBeInTheDocument();
  });

  it('24. displays calm error message on 404 not found', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockRejectedValue(new Error('404 Not Found'));
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByText(/mentor projects are currently unavailable/i)).toBeInTheDocument();
  });

  it('25. displays calm error message on 429 rate limit', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockRejectedValue(new Error('429 Too Many Requests'));
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByText(/too many requests\. please wait a moment and try again/i)).toBeInTheDocument();
  });

  it('26. displays calm error message on 500 server error', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockRejectedValue(new Error('500 Internal Server Error'));
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByText(/we couldn't load mentor projects right now/i)).toBeInTheDocument();
  });

  it('27. displays calm error message on network failure and retries successfully', async () => {
    vi.mocked(api.getMentorProjectCatalog)
      .mockRejectedValueOnce(new Error('Failed to fetch network error'))
      .mockResolvedValueOnce(mockCatalog);

    renderCatalog();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByText(/we couldn't reach growflow/i)).toBeInTheDocument();

    const retryBtn = screen.getByRole('button', { name: /try again/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });
  });

  it('28. guarantees no project assignment or selection API is called', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    // Verify no buttons exist on the cards that trigger assignment or mutation
    const allButtons = screen.queryAllByRole('button');
    const assignmentButtons = allButtons.filter((b) =>
      /assign|select|claim|start project/i.test(b.textContent || ''),
    );
    expect(assignmentButtons.length).toBe(0);
  });

  it('29. guarantees no student-instance fields are displayed', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    // No student project instance lifecycle progress, health indicators, or milestones
    expect(screen.queryByText(/lifecycle progress/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/stage \d of 8/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/healthy/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/at risk/i)).not.toBeInTheDocument();
  });

  it('30. guarantees no fake catalog data or ratings are displayed', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    expect(screen.queryByText(/trending/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/stars|rating/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/recommended for you/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/most selected/i)).not.toBeInTheDocument();
  });

  it('31. has accessible landmarks, search input label, and polite summary bar', async () => {
    vi.mocked(api.getMentorProjectCatalog).mockResolvedValue(mockCatalog);
    renderCatalog();

    await waitFor(() => {
      expect(screen.getByText('Autonomous Precision Drone')).toBeInTheDocument();
    });

    expect(screen.getByLabelText(/search mentor project/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/filter by complexity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sort mentor projects/i)).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /mentor project definitions/i })).toBeInTheDocument();
  });

  it('32. sidebar and mobile drawer contain Mentor Projects navigation link', () => {
    const { container: sidebarContainer } = render(
      <MemoryRouter initialEntries={['/student/projects/mentor-catalog']}>
        <Sidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
      </MemoryRouter>,
    );

    const mentorLink = within(sidebarContainer).getByRole('link', { name: /mentor projects/i });
    expect(mentorLink).toHaveAttribute('href', '/student/projects/mentor-catalog');
    expect(mentorLink).toHaveAttribute('aria-current', 'page');

    const { container: drawerContainer } = render(
      <AuthContext.Provider value={mockAuthContext}>
        <MemoryRouter initialEntries={['/student/projects/mentor-catalog']}>
          <MobileWorkspaceDrawer isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    const drawerMentorLink = within(drawerContainer).getByRole('link', { name: /mentor projects/i });
    expect(drawerMentorLink).toHaveAttribute('href', '/student/projects/mentor-catalog');
  });
});
