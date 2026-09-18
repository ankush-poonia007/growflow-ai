/**
 * GrowFlow Safe ReturnTo / Deep Link Sanitizer
 *
 * Requirements:
 * - Validate internal application routes only
 * - Reject protocol schemes (http:, https:, javascript:, data:, etc.)
 * - Reject protocol-relative slashes (//evil.example, /\evil.example)
 * - Reject control characters and malformed characters
 * - Provide safe fallback (default: /student/dashboard)
 */

export const DEFAULT_STUDENT_DESTINATION = '/student/dashboard';
export const DEFAULT_MENTOR_DESTINATION = '/mentor/overview';
export const DEFAULT_ADMIN_DESTINATION = '/admin/overview';

export function getDefaultDestinationForRole(role?: string | null): string {
  switch (role?.toUpperCase()) {
    case 'ADMIN':
      return DEFAULT_ADMIN_DESTINATION;
    case 'MENTOR':
      return DEFAULT_MENTOR_DESTINATION;
    case 'STUDENT':
    default:
      return DEFAULT_STUDENT_DESTINATION;
  }
}

export function sanitizeReturnTo(
  rawPath: string | null | undefined,
  fallback: string = DEFAULT_STUDENT_DESTINATION,
): string {
  if (!rawPath || typeof rawPath !== 'string') {
    return fallback;
  }

  const trimmed = rawPath.trim();

  // Reject empty string
  if (!trimmed) {
    return fallback;
  }

  // Reject control characters (0x00 - 0x1F, 0x7F)
  // eslint-disable-next-line no-control-regex
  if (/[\x00-\x1F\x7F]/.test(trimmed)) {
    return fallback;
  }

  // Must strictly start with a single forward slash
  if (!trimmed.startsWith('/')) {
    return fallback;
  }

  // Reject protocol-relative URLs (//) or backslash variants (/\, \/)
  if (trimmed.startsWith('//') || trimmed.startsWith('/\\') || trimmed.startsWith('\\')) {
    return fallback;
  }

  // Reject dangerous schemes or protocol patterns anywhere before a query/hash
  const normalized = trimmed.toLowerCase();
  if (
    normalized.includes('javascript:') ||
    normalized.includes('data:') ||
    normalized.includes('vbscript:') ||
    normalized.includes('file:')
  ) {
    return fallback;
  }

  // Attempt URL parsing with a fixed dummy origin to ensure it's strictly a relative path
  try {
    const parsed = new URL(trimmed, 'https://growflow.local');
    if (parsed.origin !== 'https://growflow.local') {
      return fallback;
    }
    // Return relative pathname + search + hash
    return `${parsed.pathname}${parsed.search}${parsed.hash}`;
  } catch {
    return fallback;
  }
}

export function getSafeReturnTo(
  searchParams: URLSearchParams,
  fallback: string = DEFAULT_STUDENT_DESTINATION,
): string {
  const returnTo = searchParams.get('returnTo');
  return sanitizeReturnTo(returnTo, fallback);
}
