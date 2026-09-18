import { useContext } from 'react';
import { AuthContext } from './AuthContext';
import type { AuthContextValue } from './types';

/**
 * Hook to consume GrowFlow centralized authentication and authorization context.
 * Throws a descriptive error if used outside an AuthProvider boundary.
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an <AuthProvider>');
  }
  return context;
}
