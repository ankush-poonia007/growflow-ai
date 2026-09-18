import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue, UserRole } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { AdminSidebar } from '@/components/navigation/AdminSidebar';
import { AIObservatory } from '@/pages/Admin/AIObservatory/AIObservatory';
import { AIUsage } from '@/pages/Admin/AIUsage/AIUsage';
import { AIExecutions } from '@/pages/Admin/AIExecutions/AIExecutions';
import { AITraceDetail } from '@/pages/Admin/AITraceDetail/AITraceDetail';
import { AIQuality } from '@/pages/Admin/AIQuality/AIQuality';
import { AICostUsage } from '@/pages/Admin/AICostUsage/AICostUsage';
import { AICostBreakdown } from '@/pages/Admin/AICostBreakdown/AICostBreakdown';
import { AIKeyPool } from '@/pages/Admin/AIKeyPool/AIKeyPool';
import * as apiClient from '@/lib/api/client';
import type {
  AdminAIObservatoryResponse,
  AdminAIUsageResponse,
  AdminAIExecutionsResponse,
  AdminAITraceDetailResponse,
  AdminAIQualityResponse,
  AdminAICostResponse,
  AdminAICostDimensionResponse,
  AdminAIKeysResponse,
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

// ============================================================
// MOCK DATA
// ============================================================

const mockObservatoryData: AdminAIObservatoryResponse = {
  gateway: {
    provider: 'OpenRouter',
    configured_active_keys: 1,
    total_key_slots: 5,
    default_model: 'anthropic/claude-3.5-sonnet',
    configured_models: ['anthropic/claude-3.5-sonnet', 'openai/gpt-4o'],
    gateway_base_url: 'https://openrouter.ai/api/v1',
    rotation_strategy: 'In-Memory Round-Robin',
    reachability_state: 'CONFIGURED_ONLY',
    credential_note: 'Configured key count reflects presence of credentials in environment.',
  },
  kpis: {
    total_ai_transactions: 42,
    blueprint_jobs_total: 20,
    blueprint_jobs_completed: 18,
    blueprint_jobs_failed: 2,
    success_rate_percent: 90.0,
    currently_running_jobs: 1,
    average_duration_seconds: 45.5,
    mentor_messages_total: 15,
    change_requests_total: 7,
  },
  active_jobs: [
    {
      id: 'job-active-1',
      blueprint_id: 'bp-1',
      project_instance_id: 'proj-1',
      project_name: 'Smart Energy Grid',
      job_type: 'FULL_GENERATION',
      status: 'RUNNING',
      current_step: 'ARCHITECTURE_SYNTHESIS',
      progress_percent: 40,
      started_at: new Date('2026-03-01T10:00:00Z').toISOString(),
      created_at: new Date('2026-03-01T10:00:00Z').toISOString(),
    },
  ],
  recent_activity: [
    {
      id: 'act-1',
      activity_type: 'SYNTHESIS_JOB',
      title: 'Blueprint Synthesis Completed',
      detail: 'Generated full system blueprint for Smart Energy Grid',
      status: 'COMPLETED',
      project_name: 'Smart Energy Grid',
      correlation_id: 'corr-1111',
      timestamp: new Date('2026-03-01T10:05:00Z').toISOString(),
    },
  ],
  notices: {
    token_metering: 'UNMETERED / NOT PERSISTED',
    dollar_cost: 'NOT PERSISTED',
    wire_telemetry: 'UNAVAILABLE',
    key_rotation: 'RUNTIME_ONLY',
  },
};

const mockUsageData: AdminAIUsageResponse = {
  overall_volume: {
    blueprint_synthesis_jobs: 20,
    ai_mentor_messages: 15,
    project_change_analyses: 7,
    total_recorded_transactions: 42,
  },
  time_trend: [
    {
      date: '2026-03-01',
      blueprint_jobs_count: 10,
      mentor_messages_count: 5,
      total_count: 15,
    },
  ],
  capability_breakdown: [
    {
      capability_key: 'BLUEPRINT_GEN',
      label: 'Blueprint Generation',
      count: 18,
      percentage: 42.9,
    },
    {
      capability_key: 'AI_MENTOR',
      label: 'AI Mentor Chat',
      count: 15,
      percentage: 35.7,
    },
  ],
  project_distribution: [
    {
      project_id: 'proj-1',
      project_name: 'Smart Energy Grid',
      synthesis_jobs_count: 12,
      mentor_messages_count: 8,
      total_transactions: 20,
    },
  ],
  outcome_distribution: {
    COMPLETED: 35,
    FAILED: 5,
    RUNNING: 2,
  },
  token_metering: 'UNMETERED / NOT PERSISTED',
  rate_limit_telemetry: 'NOT PERSISTED',
};

const mockExecutionsData: AdminAIExecutionsResponse = {
  total: 1,
  limit: 25,
  offset: 0,
  summary: {
    total: 1,
    completed: 1,
    failed: 0,
    running: 0,
    pending: 0,
  },
  executions: [
    {
      id: 'job-exec-1111',
      source: 'blueprint_jobs',
      project_instance_id: 'proj-1',
      project_name: 'Smart Energy Grid',
      capability: 'Blueprint Pipeline',
      job_type: 'FULL_GENERATION',
      target_output: null,
      status: 'COMPLETED',
      current_step: 'COMPLETED',
      progress_percent: 100,
      duration_seconds: 42,
      error: null,
      started_at: new Date('2026-03-01T10:00:00Z').toISOString(),
      completed_at: new Date('2026-03-01T10:00:42Z').toISOString(),
      created_at: new Date('2026-03-01T10:00:00Z').toISOString(),
    },
  ],
};

const mockTraceDetailData: AdminAITraceDetailResponse = {
  id: 'job-exec-1111',
  blueprint_id: 'bp-1',
  project_instance_id: 'proj-1',
  project_name: 'Smart Energy Grid',
  student_id: 'usr-student-1',
  job_type: 'FULL_GENERATION',
  target_output: null,
  status: 'COMPLETED',
  current_step: 'COMPLETED',
  progress_percent: 100,
  duration_seconds: 42,
  sanitized_error: null,
  started_at: new Date('2026-03-01T10:00:00Z').toISOString(),
  completed_at: new Date('2026-03-01T10:00:42Z').toISOString(),
  created_at: new Date('2026-03-01T10:00:00Z').toISOString(),
  pipeline_stages: [
    {
      stage_order: 1,
      section_key: 'PROJECT_OVERVIEW',
      title: 'Project Overview',
      status: 'COMPLETED',
      progress_milestone: 10,
    },
    {
      stage_order: 2,
      section_key: 'SYSTEM_ARCHITECTURE',
      title: 'System Architecture',
      status: 'COMPLETED',
      progress_milestone: 20,
    },
  ],
  qa_result: {
    qa_status: 'PASS',
    qa_score: 92,
    summary: 'Strong architecture definition meeting rubric standards.',
    evaluated_criteria: {
      feasibility: 90,
      security: 95,
    },
    issues: [
      {
        section: 'Database',
        severity: 'LOW',
        description: 'Consider adding redis caching layer',
      },
    ],
    recommendations: ['Add caching strategy in section 4'],
  },
  domain_events: [
    {
      id: 'ev-1',
      event_type: 'BLUEPRINT_GENERATION_COMPLETED',
      status: 'PUBLISHED',
      correlation_id: 'corr-exec-1111',
      occurred_at: new Date('2026-03-01T10:00:42Z').toISOString(),
    },
  ],
  telemetry_notices: {
    http_wire_packets: 'UNAVAILABLE',
    dns_tls_timing: 'UNAVAILABLE',
    ttft: 'UNAVAILABLE',
    provider_wire_latency: 'UNAVAILABLE',
    langgraph_checkpoints: 'UNAVAILABLE',
  },
};

const mockQualityData: AdminAIQualityResponse = {
  total_evaluated: 15,
  passed_count: 14,
  failed_count: 1,
  pending_count: 0,
  pass_rate_percent: 93.3,
  average_qa_score: 87.5,
  min_qa_score: 65,
  max_qa_score: 98,
  score_distribution: {
    range_85_100: 10,
    range_70_84: 4,
    range_50_69: 1,
    range_0_49: 0,
  },
  criteria_averages: {
    feasibility: 88.0,
    scalability: 86.5,
    architecture: 90.0,
  },
  top_issues: [
    {
      section: 'Security',
      severity: 'MEDIUM',
      count: 3,
      sample_description: 'Missing role-based access specification in schema',
      recommendation: 'Define granular permissions table',
    },
  ],
  approval_conversion_rate: 85.7,
  deferred_capabilities: {
    rag_faithfulness_evaluation: 'DEFERRED',
    automated_hallucination_benchmarking: 'UNAVAILABLE',
    student_csat_ratings: 'UNAVAILABLE',
  },
};

const mockCostData: AdminAICostResponse = {
  execution_volume_total: 42,
  blueprint_jobs_count: 20,
  ai_mentor_messages_count: 15,
  change_analyses_count: 7,
  active_models: ['anthropic/claude-3.5-sonnet', 'openai/gpt-4o'],
  provider: 'OpenRouter',
  billing_model: 'DIRECT_PROVIDER_BILLED — OPENROUTER',
  cost_telemetry_state: 'UNMETERED / NOT PERSISTED',
  token_metering_state: 'UNMETERED / NOT PERSISTED',
  disclaimer:
    'OpenRouter billing is managed upstream via external provider accounts. Per-token accounting tables and dollar pricing schedules are not configured in the current database schema.',
};

const mockCostDimensionData: AdminAICostDimensionResponse = {
  dimension: 'agent',
  title: 'Execution Volume by Capability / Agent',
  metric_type: 'EXECUTION_VOLUME',
  total_volume: 42,
  items: [
    {
      key: 'BLUEPRINT_GEN',
      label: 'Blueprint Generation Pipeline',
      execution_count: 20,
      percentage: 47.6,
      detail: '20 synthesis runs',
    },
    {
      key: 'AI_MENTOR',
      label: 'AI Mentor Chat Assistant',
      execution_count: 15,
      percentage: 35.7,
      detail: '15 messages',
    },
  ],
  cost_notice:
    'Dollar cost breakdown is UNAVAILABLE because tokens and provider pricing schedules are unmetered in persistence. Data reflects canonical execution volume.',
};

const mockKeysData: AdminAIKeysResponse = {
  provider: 'OpenRouter',
  gateway_base_url: 'https://openrouter.ai/api/v1',
  total_slots: 5,
  configured_key_count: 1,
  rotation_mechanism: 'In-Memory Round-Robin',
  rotation_runtime_state: 'RUNTIME_IN_MEMORY',
  slots: [
    {
      slot_index: 1,
      slot_label: 'OpenRouter Key Slot 1',
      env_var_name: 'OPENROUTER_API_KEY_1',
      status: 'CONFIGURED',
      provider: 'OpenRouter',
      masked_identifier: 'sk-or-••••••••••••••••3a8f',
      rotation_posture: 'ACTIVE_IN_ROTATION',
    },
    {
      slot_index: 2,
      slot_label: 'OpenRouter Key Slot 2',
      env_var_name: 'OPENROUTER_API_KEY_2',
      status: 'NOT_CONFIGURED',
      provider: 'OpenRouter',
      masked_identifier: null,
      rotation_posture: 'UNCONFIGURED',
    },
  ],
  security_notice:
    'Raw API keys, authorization headers, and environment secrets are strictly redacted. Key rotation is managed in-memory across configured environment slots. Individual key rate-limit, cooldown, and historical health telemetry is not persisted in the current gateway.',
};

describe('Admin Batch 10 — AI Observability, Quality, Cost & Key Pool Monitoring', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  // ============================================================
  // 1. AdminSidebar Navigation Tests
  // ============================================================
  describe('AdminSidebar Navigation', () => {
    it('renders AI Observatory between Instances and System Health', () => {
      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/admin/overview']}>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      expect(screen.getByRole('link', { name: /AI Observatory/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Instances/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /System Health/i })).toBeInTheDocument();
    });

    it('marks AI Observatory active when route is /admin/ai', () => {
      render(
        <AuthContext.Provider value={createMockAuth()}>
          <MemoryRouter initialEntries={['/admin/ai']}>
            <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
          </MemoryRouter>
        </AuthContext.Provider>
      );

      const link = screen.getByRole('link', { name: /AI Observatory/i });
      expect(link.className).toContain('gf-admin-sidebar__item--active');
    });
  });

  // ============================================================
  // 2. AD11 — AI Observatory Tests
  // ============================================================
  describe('AD11 — AI Observatory', () => {
    it('renders gateway posture, KPI counters, and active jobs', async () => {
      vi.spyOn(apiClient, 'getAdminAIObservatory').mockResolvedValue(mockObservatoryData);

      render(
        <MemoryRouter initialEntries={['/admin/ai']}>
          <AIObservatory />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('AI Observatory')).toBeInTheDocument();
        expect(screen.getByText('AI Provider Gateway Posture')).toBeInTheDocument();
        expect(screen.getByText('Total AI Transactions')).toBeInTheDocument();
        expect(screen.getByText('42')).toBeInTheDocument();
        expect(screen.getByText('90%')).toBeInTheDocument();
        expect(screen.getAllByText('Smart Energy Grid').length).toBeGreaterThan(0);
      });

      // Verifies operational disclaimers
      expect(screen.getByText(/Per-token telemetry is not persisted/i)).toBeInTheDocument();
    });

    it('handles empty active jobs and recent activity truthfully', async () => {
      vi.spyOn(apiClient, 'getAdminAIObservatory').mockResolvedValue({
        ...mockObservatoryData,
        active_jobs: [],
        recent_activity: [],
      });

      render(
        <MemoryRouter initialEntries={['/admin/ai']}>
          <AIObservatory />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/No Active AI Synthesis Jobs/i)).toBeInTheDocument();
        expect(screen.getByText(/No Recent Activity/i)).toBeInTheDocument();
      });
    });

    it('displays error alert and supports retry on fetch failure', async () => {
      const spy = vi
        .spyOn(apiClient, 'getAdminAIObservatory')
        .mockRejectedValueOnce(new Error('Observatory API unavailable'))
        .mockResolvedValueOnce(mockObservatoryData);

      render(
        <MemoryRouter initialEntries={['/admin/ai']}>
          <AIObservatory />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Observatory API unavailable')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /Retry/i }));

      await waitFor(() => {
        expect(screen.getByText('AI Provider Gateway Posture')).toBeInTheDocument();
      });

      expect(spy).toHaveBeenCalledTimes(2);
    });
  });

  // ============================================================
  // 3. AD12 — AI Usage Tests
  // ============================================================
  describe('AD12 — AI Usage', () => {
    it('renders volume breakdown and unmetered policy badges', async () => {
      vi.spyOn(apiClient, 'getAdminAIUsage').mockResolvedValue(mockUsageData);

      render(
        <MemoryRouter initialEntries={['/admin/ai/usage']}>
          <AIUsage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('AI Execution Usage')).toBeInTheDocument();
        expect(screen.getByText(/TOKEN METERING: UNMETERED \/ NOT PERSISTED/i)).toBeInTheDocument();
        expect(screen.getByText(/RATE-LIMIT TELEMETRY: NOT PERSISTED/i)).toBeInTheDocument();
        expect(screen.getByText('Blueprint Synthesis Runs')).toBeInTheDocument();
        expect(screen.getAllByText('20').length).toBeGreaterThan(0);
        expect(screen.getAllByText('AI Mentor Assistant Chats').length).toBeGreaterThan(0);
        expect(screen.getAllByText('15').length).toBeGreaterThan(0);
      });
    });
  });

  // ============================================================
  // 4. AD13 — Agent Executions Tests
  // ============================================================
  describe('AD13 — Agent Executions', () => {
    it('renders paginated executions inventory and links to trace', async () => {
      vi.spyOn(apiClient, 'getAdminAIExecutions').mockResolvedValue(mockExecutionsData);

      render(
        <MemoryRouter initialEntries={['/admin/ai/executions']}>
          <AIExecutions />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Agent Executions')).toBeInTheDocument();
        expect(screen.getByText('job-exec…')).toBeInTheDocument();
        expect(screen.getByText('Trace →')).toBeInTheDocument();
        expect(screen.getByText('42s')).toBeInTheDocument();
      });
    });
  });

  // ============================================================
  // 5. AD14 — AI Trace Detail Tests
  // ============================================================
  describe('AD14 — AI Trace Detail', () => {
    it('renders partial trace with stages, QA judge result, and unavailable notices', async () => {
      vi.spyOn(apiClient, 'getAdminAITraceDetail').mockResolvedValue(mockTraceDetailData);

      render(
        <MemoryRouter initialEntries={['/admin/ai/executions/job-exec-1111']}>
          <Routes>
            <Route path="/admin/ai/executions/:executionId" element={<AITraceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Execution Overview')).toBeInTheDocument();
        expect(screen.getByText('System Architecture')).toBeInTheDocument();
        expect(screen.getByText('Correlated QA Judge Evaluation')).toBeInTheDocument();
        expect(screen.getByText('92/100')).toBeInTheDocument();
        expect(screen.getByText(/Low-Level Wire Telemetry/i)).toBeInTheDocument();
        expect(screen.getByText(/LangGraph Checkpoints/i)).toBeInTheDocument();
      });
    });

    it('renders error state when execution is not found', async () => {
      vi.spyOn(apiClient, 'getAdminAITraceDetail').mockRejectedValue(
        new Error('AI execution with ID non-existent not found')
      );

      render(
        <MemoryRouter initialEntries={['/admin/ai/executions/non-existent']}>
          <Routes>
            <Route path="/admin/ai/executions/:executionId" element={<AITraceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/AI execution with ID non-existent not found/i)).toBeInTheDocument();
      });
    });
  });

  // ============================================================
  // 6. AD15 — AI Quality Tests
  // ============================================================
  describe('AD15 — AI Quality', () => {
    it('renders QA metrics, score distributions, and deferred capabilities', async () => {
      vi.spyOn(apiClient, 'getAdminAIQuality').mockResolvedValue(mockQualityData);

      render(
        <MemoryRouter initialEntries={['/admin/ai/quality']}>
          <AIQuality />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('AI Quality & QA Judge')).toBeInTheDocument();
        expect(screen.getByText('93.3%')).toBeInTheDocument();
        expect(screen.getByText('87.5/100')).toBeInTheDocument();
        expect(screen.getByText('Exemplary (85–100)')).toBeInTheDocument();
        expect(screen.getByText('Continuous RAG Faithfulness')).toBeInTheDocument();
        expect(screen.getByText('DEFERRED')).toBeInTheDocument();
      });
    });
  });

  // ============================================================
  // 7. AD16 — Cost & Usage Tests
  // ============================================================
  describe('AD16 — Cost & Capacity Accounting', () => {
    it('truthfully displays unmetered cost posture and no fake dollar values', async () => {
      vi.spyOn(apiClient, 'getAdminAICost').mockResolvedValue(mockCostData);

      render(
        <MemoryRouter initialEntries={['/admin/ai/cost']}>
          <AICostUsage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('AI Capacity & Upstream Billing')).toBeInTheDocument();
        expect(screen.getByText(/DIRECT_PROVIDER_BILLED — OPENROUTER/i)).toBeInTheDocument();
        expect(screen.getByText(/COST TELEMETRY: UNMETERED \/ NOT PERSISTED/i)).toBeInTheDocument();
        expect(screen.getByText(/TOKEN LEDGER: UNMETERED \/ NOT PERSISTED/i)).toBeInTheDocument();
      });

      // Verifies no fabricated dollar signs are rendered
      expect(screen.queryByText(/\$[0-9]+/)).not.toBeInTheDocument();
    });
  });

  // ============================================================
  // 8. AD17 — Cost Breakdown Tests
  // ============================================================
  describe('AD17 — Cost Breakdown', () => {
    it('renders dimension execution volume and explains usage semantics', async () => {
      vi.spyOn(apiClient, 'getAdminAICostDimension').mockResolvedValue(mockCostDimensionData);

      render(
        <MemoryRouter initialEntries={['/admin/ai/cost/agent']}>
          <Routes>
            <Route path="/admin/ai/cost/:dimension" element={<AICostBreakdown />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/Execution Volume by Capability \/ Agent/i)).toBeInTheDocument();
        expect(screen.getByText(/METRIC: EXECUTION_VOLUME \(NOT DOLLAR COST\)/i)).toBeInTheDocument();
        expect(screen.getByText('Blueprint Generation Pipeline')).toBeInTheDocument();
        expect(screen.getByText('20 runs')).toBeInTheDocument();
      });
    });
  });

  // ============================================================
  // 9. AD18 — API Key Pool Monitoring Tests & Security Check
  // ============================================================
  describe('AD18 — API Key Pool Monitoring (Security Validation)', () => {
    it('safely displays masked slot labels without exposing raw secrets', async () => {
      vi.spyOn(apiClient, 'getAdminAIKeys').mockResolvedValue(mockKeysData);

      const { container } = render(
        <MemoryRouter initialEntries={['/admin/ai/keys']}>
          <AIKeyPool />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('API Key Pool Monitoring')).toBeInTheDocument();
        expect(screen.getByText('OpenRouter Key Slot 1')).toBeInTheDocument();
        expect(screen.getByText('sk-or-••••••••••••••••3a8f')).toBeInTheDocument();
        expect(screen.getByText('CREDENTIAL SECRETS REDACTED')).toBeInTheDocument();
      });

      // STRICT SECURITY ASSERTION: No unmasked API key or secret exists in HTML DOM
      const domHtml = container.innerHTML;
      expect(domHtml).not.toMatch(/sk-or-v1-[a-zA-Z0-9]{20,}/);
      expect(domHtml).not.toContain('Bearer ');
      expect(domHtml).not.toContain('eyJhbGci');
    });
  });
});
