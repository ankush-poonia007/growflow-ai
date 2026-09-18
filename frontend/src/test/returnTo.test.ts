import { describe, it, expect } from 'vitest';
import {
  sanitizeReturnTo,
  getSafeReturnTo,
  getDefaultDestinationForRole,
  DEFAULT_STUDENT_DESTINATION,
} from '@/auth/returnTo';

describe('sanitizeReturnTo', () => {
  it('preserves valid internal paths', () => {
    expect(sanitizeReturnTo('/student/projects/123')).toBe('/student/projects/123');
    expect(sanitizeReturnTo('/student/dashboard?tab=milestones')).toBe(
      '/student/dashboard?tab=milestones',
    );
    expect(sanitizeReturnTo('/features#security')).toBe('/features#security');
  });

  it('falls back to default destination when input is null, undefined, or empty', () => {
    expect(sanitizeReturnTo(null)).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo(undefined)).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('   ')).toBe(DEFAULT_STUDENT_DESTINATION);
  });

  it('rejects external absolute URLs', () => {
    expect(sanitizeReturnTo('https://evil.example')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('http://evil.example/phish')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('https://google.com')).toBe(DEFAULT_STUDENT_DESTINATION);
  });

  it('rejects protocol-relative and backslash variants', () => {
    expect(sanitizeReturnTo('//evil.example')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('//evil.example/path')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('/\\evil.example')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('\\evil.example')).toBe(DEFAULT_STUDENT_DESTINATION);
  });

  it('rejects dangerous script schemes and control characters', () => {
    expect(sanitizeReturnTo('javascript:alert(1)')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('/path?x=javascript:alert(1)')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('data:text/html,evil')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('/student\r\ndashboard')).toBe(DEFAULT_STUDENT_DESTINATION);
    expect(sanitizeReturnTo('/student\x00dashboard')).toBe(DEFAULT_STUDENT_DESTINATION);
  });

  it('supports custom fallback destination', () => {
    expect(sanitizeReturnTo('https://evil.com', '/features')).toBe('/features');
  });
});

describe('getSafeReturnTo', () => {
  it('reads and sanitizes returnTo from URLSearchParams', () => {
    const params = new URLSearchParams('returnTo=%2Fstudent%2Fprojects%2F456');
    expect(getSafeReturnTo(params)).toBe('/student/projects/456');

    const evilParams = new URLSearchParams('returnTo=https%3A%2F%2Fevil.example');
    expect(getSafeReturnTo(evilParams)).toBe(DEFAULT_STUDENT_DESTINATION);
  });
});

describe('getDefaultDestinationForRole', () => {
  it('returns appropriate default destination for all roles', () => {
    expect(getDefaultDestinationForRole('ADMIN')).toBe('/admin/overview');
    expect(getDefaultDestinationForRole('admin')).toBe('/admin/overview');
    expect(getDefaultDestinationForRole('MENTOR')).toBe('/mentor/overview');
    expect(getDefaultDestinationForRole('mentor')).toBe('/mentor/overview');
    expect(getDefaultDestinationForRole('STUDENT')).toBe('/student/dashboard');
    expect(getDefaultDestinationForRole('student')).toBe('/student/dashboard');
    expect(getDefaultDestinationForRole(null)).toBe('/student/dashboard');
    expect(getDefaultDestinationForRole(undefined)).toBe('/student/dashboard');
  });
});
