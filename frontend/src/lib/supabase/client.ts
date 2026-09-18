import { createClient, type SupabaseClient } from '@supabase/supabase-js';

/**
 * GrowFlow Frontend Supabase Client
 *
 * Requirements:
 * - Singleton instance
 * - Public browser-only configuration (never service-role or backend secrets)
 * - Safe for browser environments and unit test runners
 */

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

let clientInstance: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient {
  if (clientInstance) {
    return clientInstance;
  }

  if (!supabaseUrl || !supabaseAnonKey) {
    console.warn(
      '[GrowFlow Auth] Supabase URL or Anon Key is missing. Check your VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY configuration.',
    );
  }

  // Fallback dummy URL and key to prevent createClient from hard-throwing during headless test imports
  const effectiveUrl = supabaseUrl || 'https://placeholder.supabase.co';
  const effectiveKey = supabaseAnonKey || 'placeholder-anon-key';

  clientInstance = createClient(effectiveUrl, effectiveKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
      flowType: 'pkce',
    },
  });

  return clientInstance;
}

export const supabase = getSupabase();
