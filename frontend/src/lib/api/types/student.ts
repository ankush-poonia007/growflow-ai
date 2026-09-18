/**
 * GrowFlow Student Profile API Types
 *
 * Reflects backend schemas:
 * GET /api/v1/students/me -> StudentProfileResponseSchema
 * PATCH /api/v1/students/me -> StudentProfileUpdateSchema
 */

export interface StudentTechnologyItem {
  id?: string;
  technology_id: string;
  proficiency?: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | string;
  relationship_type?: 'KNOWN' | 'PREVIOUSLY_USED' | 'LEARNING' | string;
}

export interface StudentProfile {
  user_id: string;
  student_id: string | null;
  bio: string | null;
  goals: string | null;
  interests: string | null;
  technologies: StudentTechnologyItem[];
}

export interface StudentProfileUpdatePayload {
  bio?: string | null;
  goals?: string | null;
  interests?: string | null;
  technologies?: StudentTechnologyItem[] | null;
}
