import type { ApplicationStatus } from '../../types/applications'

const STYLES: Record<ApplicationStatus, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  SUBMITTED: 'bg-blue-100 text-blue-700',
  PROCESSING: 'bg-yellow-100 text-yellow-700',
  ADDITIONAL_INFO_REQUIRED: 'bg-orange-100 text-orange-700',
  APPROVED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
  CANCELLED: 'bg-gray-100 text-gray-500',
  FAILED: 'bg-red-200 text-red-800',
}

const LABELS: Record<ApplicationStatus, string> = {
  DRAFT: 'Draft',
  SUBMITTED: 'Submitted',
  PROCESSING: 'Processing',
  ADDITIONAL_INFO_REQUIRED: 'Info Required',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  CANCELLED: 'Cancelled',
  FAILED: 'System Error',
}

export default function ApplicationStatusBadge({ status }: { status: ApplicationStatus }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STYLES[status]}`}>
      {LABELS[status]}
    </span>
  )
}