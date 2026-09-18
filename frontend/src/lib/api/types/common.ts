/**
 * GrowFlow API Response Envelope Types
 *
 * Adheres to Phase 6C canonical envelope architecture:
 * Success: { success: true, message: string, data: T, meta?: ApiMetadata }
 * Error:   { success: false, error: ApiErrorBody, meta?: ApiMetadata }
 */

export interface ApiMetadata {
  timestamp?: string;
  request_id?: string;
  pagination?: {
    page?: number;
    page_size?: number;
    total_items?: number;
    total_pages?: number;
  };
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: unknown;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: ApiErrorBody;
  meta?: ApiMetadata;
}
