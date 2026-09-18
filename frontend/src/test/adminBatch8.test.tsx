import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router';
import { AuthContext } from '@/auth/AuthContext';
import type { AuthContextValue, UserRole } from '@/auth/types';
import type { User } from '@supabase/supabase-js';

import { AdminSidebar } from '@/components/navigation/AdminSidebar';
import { SystemHealth } from '@/pages/Admin/SystemHealth/SystemHealth';
import { ComponentDetail } from '@/pages/Admin/ComponentDetail/ComponentDetail';
import { SecurityOverview } from '@/pages/Admin/SecurityOverview/SecurityOverview';
import { AuditLog } from '@/pages/Admin/AuditLog/AuditLog';
import { InvestigationRequests } from '@/pages/Admin/InvestigationRequests/InvestigationRequests';
import { InvestigationDetail } from '@/pages/Admin/InvestigationDetail/InvestigationDetail';
import * as apiClient from '@/lib/api/client';
import type {
  AdminSystemHealthResponse,
  AdminSubsystemDetail,
  AdminSecurityOverview,
  AdminAuditLogResponse,
  AdminInvestigationOverviewResponse,
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

const mockHealthData: AdminSystemHealthResponse = {
  overall_status: 'OPERATIONAL',
  environment: 'test',
  version: '0.1.0',
  timestamp: new Date().toISOString(),
  subsystems: [
    {
      id: 'api',
      name: 'API Runtime Process',
      status: 'OPERATIONAL',
      type: 'CORE',
      details: 'FastAPI process running on 127.0.0.1:8000',
    },
    {
      id: 'database',
      name: 'PostgreSQL Persistence',
      status: 'OPERATIONAL',
      type: 'DATABASE',
      details: 'Engine pool size: 5, max overflow: 10',
    },
  ],
  metrics: {
    outbox_pending: 0,
    outbox_failed: 0,
    outbox_published: 12,
    active_ai_keys: 1,
    db_pool_size: 5,
    db_connected: true,
  },
};

const mockComponentDetail: AdminSubsystemDetail = {
  id: 'database',
  name: 'PostgreSQL Persistence',
  status: 'OPERATIONAL',
  type: 'DATABASE',
  environment: 'test',
  checked_at: new Date().toISOString(),
  configuration: {
    pool_size: 5,
    max_overflow: 10,
    url_configured: true,
  },
  diagnostics: {
    connectivity_confirmed: true,
    engine_initialised: true,
  },
  recent_failures: [],
};

const mockSecurityOverview: AdminSecurityOverview = {
  user_posture: {
    total_users: 30,
    active_users: 29,
    inactive_users: 0,
    suspended_users: 1,
    admin_count: 2,
    mentor_count: 6,
    student_count: 22,
  },
  audit_summary: {
    total_events: 150,
    outbox_delivery_failures: 0,
  },
  recent_security_relevant_events: [
    {
      id: 'evt-1',
      event_type: 'ProjectCreated',
      title: 'Project Created',
      description: 'Project workspace initialized.',
      actor_id: 'usr-1',
      actor_role: 'STUDENT',
      resource_type: 'project',
      resource_id: 'proj-1',
      occurred_at: new Date().toISOString(),
      status: 'PUBLISHED',
    },
  ],
};

const mockAuditLog: AdminAuditLogResponse = {
  total: 1,
  limit: 25,
  offset: 0,
  events: [
    {
      id: 'evt-audit-1',
      event_type: 'ProjectCreated',
      title: 'Project Created',
      description: 'Project workspace initialized.',
      actor_id: 'usr-1',
      actor_role: 'STUDENT',
      resource_type: 'project',
      resource_id: 'proj-123',
      project_instance_id: 'proj-123',
      group_id: null,
      correlation_id: 'corr-xyz',
      status: 'PUBLISHED',
      occurred_at: new Date().toISOString(),
      metadata: { title: 'Test Project' },
    },
  ],
};

const mockInvestigations: AdminInvestigationOverviewResponse = {
  framework_status: 'GOVERNED_INSPECTION_ACTIVE',
  disclaimer: 'Governed Inspection Surface',
  total_flagged: 1,
  flagged_resources: [
    {
      resource_type: 'USER',
      resource_id: 'usr-susp-1',
      label: 'Suspended Student',
      detail: 'Account status is SUSPENDED',
      flag_reason: 'ACCOUNT_SUSPENDED',
      flagged_at: new Date().toISOString(),
      canonical_inspection_url: '/admin/students/usr-susp-1',
    },
  ],
};

describe('Admin Batch 8 — System Health, Security & Audit (AD19–AD20, AD24–AD27)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // -------------------------------------------------------------------------
  // AD19: System Health
  // -------------------------------------------------------------------------
  it('AD19: renders platform system health, stat tiles, and subsystem cards', async () => {
    vi.spyOn(apiClient, 'getAdminSystemHealth').mockResolvedValue(mockHealthData);

    render(
      <MemoryRouter>
        <SystemHealth />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1, name: /system health/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('API Runtime Process')).toBeInTheDocument();
      expect(screen.getByText('PostgreSQL Persistence')).toBeInTheDocument();
      expect(screen.getByText('Active AI Keys')).toBeInTheDocument();
    });
  });

  it('AD19: handles API failure with error alert and retry button', async () => {
    vi.spyOn(apiClient, 'getAdminSystemHealth').mockRejectedValue(new Error('Network connectivity failure'));

    render(
      <MemoryRouter>
        <SystemHealth />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/network connectivity failure/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // AD20: Component Detail
  // -------------------------------------------------------------------------
  it('AD20: renders subsystem diagnostic signals and configuration flags', async () => {
    vi.spyOn(apiClient, 'getAdminComponentDetail').mockResolvedValue(mockComponentDetail);

    render(
      <MemoryRouter initialEntries={['/admin/system-health/database']}>
        <Routes>
          <Route path="/admin/system-health/:component" element={<ComponentDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /postgresql persistence/i })).toBeInTheDocument();
      expect(screen.getByText('Safe Configuration Signals')).toBeInTheDocument();
      expect(screen.getByText('Diagnostic Telemetry')).toBeInTheDocument();
      expect(screen.getByText(/clean/i)).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // AD24: Security & Audit Overview
  // -------------------------------------------------------------------------
  it('AD24: renders user security posture, role distribution, and audit overview', async () => {
    vi.spyOn(apiClient, 'getAdminSecurityOverview').mockResolvedValue(mockSecurityOverview);

    render(
      <MemoryRouter>
        <SecurityOverview />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1, name: /security & audit governance/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Total User Accounts')).toBeInTheDocument();
      expect(screen.getByText('Suspended Accounts')).toBeInTheDocument();
      expect(screen.getByText('Role Governance Distribution')).toBeInTheDocument();
      expect(screen.getByText('Security Architecture Signals')).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // AD25: Audit Log
  // -------------------------------------------------------------------------
  it('AD25: renders dense operational audit table, search, and pagination', async () => {
    vi.spyOn(apiClient, 'getAdminAuditLog').mockResolvedValue(mockAuditLog);

    render(
      <MemoryRouter>
        <AuditLog />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1, name: /platform audit log/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Project workspace initialized.')).toBeInTheDocument();
      expect(screen.getByText(/showing 1 to 1 of 1 events/i)).toBeInTheDocument();
      expect(screen.getByRole('searchbox')).toBeInTheDocument();
    });
  });

  it('AD25: filter role triggers api reload', async () => {
    const spy = vi.spyOn(apiClient, 'getAdminAuditLog').mockResolvedValue(mockAuditLog);

    render(
      <MemoryRouter>
        <AuditLog />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(spy).toHaveBeenCalled();
    });

    const roleSelect = screen.getByLabelText(/filter by actor role/i);
    fireEvent.change(roleSelect, { target: { value: 'STUDENT' } });

    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith(expect.objectContaining({ actor_role: 'STUDENT' }));
    });
  });

  // -------------------------------------------------------------------------
  // AD26: Investigation Requests
  // -------------------------------------------------------------------------
  it('AD26: renders governed inspection surface, truthful schema disclaimer, and candidate targets', async () => {
    vi.spyOn(apiClient, 'getAdminInvestigations').mockResolvedValue(mockInvestigations);

    render(
      <MemoryRouter>
        <InvestigationRequests />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1, name: /investigation & governed inspection/i })).toBeInTheDocument();
    expect(screen.getByText(/governed resource inspection:/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Suspended Student')).toBeInTheDocument();
      expect(screen.getByText('Suspended User')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /inspect →/i })).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // AD27: Investigation Detail
  // -------------------------------------------------------------------------
  it('AD27: truthfully reports canonical investigation limitation when unresolvable', async () => {
    vi.spyOn(apiClient, 'getAdminInvestigationDetail').mockRejectedValue(new Error('Investigation record not found.'));

    render(
      <MemoryRouter initialEntries={['/admin/security/investigations/unknown-inv-1']}>
        <Routes>
          <Route path="/admin/security/investigations/:investigationId" element={<InvestigationDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /canonical investigation limitation/i })).toBeInTheDocument();
      expect(screen.getByText(/ad27 requires persistent investigation identity/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /return to governed inspection/i })).toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // Navigation: AdminSidebar
  // -------------------------------------------------------------------------
  it('Sidebar: includes System Health and Security & Audit navigation links', () => {
    const auth = createMockAuth();
    render(
      <AuthContext.Provider value={auth}>
        <MemoryRouter initialEntries={['/admin/system-health']}>
          <AdminSidebar isCollapsed={false} onToggleCollapse={vi.fn()} />
        </MemoryRouter>
      </AuthContext.Provider>
    );

    expect(screen.getByRole('link', { name: /system health/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /security & audit/i })).toBeInTheDocument();
  });
});
