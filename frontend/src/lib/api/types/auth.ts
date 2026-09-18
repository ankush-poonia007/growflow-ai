/**
 * GrowFlow Authentication API Types
 *
 * Reflects backend schemas:
 * GET /api/v1/auth/me -> CurrentUser profile
 */

export type UserRole = 'STUDENT' | 'MENTOR' | 'ADMIN';
export type AccountStatus = 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';

export interface CurrentUserIdentity {
  id: string;
  email: string;
  role: UserRole;
  status: AccountStatus;
  full_name: string;
}
