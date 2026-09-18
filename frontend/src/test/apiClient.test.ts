import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getCurrentUser,
  getProjects,
  getProject,
  createProject,
  ApiClientError,
  API_BASE_URL,
} from '@/lib/api';
import { supabase } from '@/lib/supabase';
import type { Session } from '@supabase/supabase-js';

describe('API Client Foundation', () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('attaches Supabase Bearer token when active session exists', async () => {
    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: {
        session: {
          access_token: 'test-supabase-access-token',
        } as unknown as Session,
      },
      error: null,
    });

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        success: true,
        data: { id: 'usr-1', email: 'test@growflow.com', role: 'STUDENT' },
      }),
    });
    globalThis.fetch = mockFetch;

    const user = await getCurrentUser();

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/v1/auth/me`,
      expect.objectContaining({
        headers: expect.any(Headers),
      }),
    );

    const callArgs = mockFetch.mock.calls[0];
    const headersUsed: Headers = callArgs ? callArgs[1].headers : new Headers();
    expect(headersUsed.get('Authorization')).toBe('Bearer test-supabase-access-token');
    expect(user.id).toBe('usr-1');
  });

  it('unwraps canonical success response envelope and returns inner data', async () => {
    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: null },
      error: null,
    });

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        success: true,
        message: 'Projects retrieved.',
        data: [
          {
            id: 'proj-1',
            name: 'GrowFlow Engine',
            current_phase: 'IDEA',
            health: 'HEALTHY',
            progress_percentage: 0,
            status: 'ACTIVE',
          },
        ],
      }),
    });

    const projects = await getProjects();
    expect(projects).toHaveLength(1);
    expect(projects[0]?.name).toBe('GrowFlow Engine');
    expect(projects[0]?.current_phase).toBe('IDEA');
  });

  it('throws ApiClientError with parsed code and message on 401 Unauthorized', async () => {
    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: null },
      error: null,
    });

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        success: false,
        error: {
          code: 'AUTH_INVALID_TOKEN',
          message: 'Authentication token is expired.',
        },
      }),
    });

    await expect(getProjects()).rejects.toThrow(ApiClientError);

    try {
      await getProjects();
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError);
      const apiErr = err as ApiClientError;
      expect(apiErr.status).toBe(401);
      expect(apiErr.code).toBe('AUTH_INVALID_TOKEN');
      expect(apiErr.message).toBe('Authentication token is expired.');
      expect(apiErr.isUnauthorized).toBe(true);
      expect(apiErr.isForbidden).toBe(false);
    }
  });

  it('throws ApiClientError with isForbidden on 403 response', async () => {
    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: null },
      error: null,
    });

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        success: false,
        error: {
          code: 'AUTH_ROLE_REQUIRED',
          message: 'Student role required.',
        },
      }),
    });

    try {
      await getProject('proj-123');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError);
      const apiErr = err as ApiClientError;
      expect(apiErr.status).toBe(403);
      expect(apiErr.isForbidden).toBe(true);
    }
  });

  it('normalizes network failures to status 0 and code NETWORK_ERROR', async () => {
    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: null },
      error: null,
    });

    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    try {
      await getProjects();
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError);
      const apiErr = err as ApiClientError;
      expect(apiErr.status).toBe(0);
      expect(apiErr.code).toBe('NETWORK_ERROR');
      expect(apiErr.isNetworkError).toBe(true);
    }
  });

  it('serializes JSON body correctly for POST mutations', async () => {
    vi.spyOn(supabase.auth, 'getSession').mockResolvedValue({
      data: { session: null },
      error: null,
    });

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        success: true,
        data: {
          id: 'new-proj-id',
          name: 'My New AI Tool',
          current_phase: 'IDEA',
          health: 'HEALTHY',
          progress_percentage: 0,
        },
      }),
    });
    globalThis.fetch = mockFetch;

    const created = await createProject({
      name: 'My New AI Tool',
      problem: 'Manual planning takes too long',
      complexity: 'INTERMEDIATE',
    });

    expect(created.id).toBe('new-proj-id');
    expect(mockFetch).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/v1/projects`,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          name: 'My New AI Tool',
          problem: 'Manual planning takes too long',
          complexity: 'INTERMEDIATE',
        }),
      }),
    );
  });
});
