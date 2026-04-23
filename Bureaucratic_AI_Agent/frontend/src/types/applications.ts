export type ApplicationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'PROCESSING'
  | 'ADDITIONAL_INFO_REQUIRED'
  | 'APPROVED'
  | 'REJECTED'
  | 'CANCELLED'
  | 'FAILED'

export interface ValidationIssue {
  field: string
  detail: string
  severity: 'critical' | 'warning' | 'info'
}

export interface AIReport {
  decision: 'ACCEPT' | 'REJECT' | 'ERROR'
  confidence_score: number
  extracted_data: Record<string, unknown>
  issues_found: ValidationIssue[]
  recommendations: string | null
  ai_model_used: string
  prompt_version: string
  processing_time_seconds: number
  created_at: string
}

export interface Document {
  id: string
  file_name: string
  file_format: string
  file: string
  created_at: string
}

export interface Application {
  id: string
  application_number: string
  procedure: string
  status: ApplicationStatus
  form_data: Record<string, unknown>
  submitted_at: string | null
  created_at: string
  updated_at: string
  documents: Document[]
  report: AIReport | null
}

export interface ApplicationSummary {
  id: string
  application_number: string
  procedure: string
  status: ApplicationStatus
  created_at: string
}