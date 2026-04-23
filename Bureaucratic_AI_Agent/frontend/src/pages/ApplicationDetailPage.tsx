import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useApplication } from '../hooks/useApplication'
import ApplicationStatusBadge from '../components/applications/ApplicationStatusBadge'
import AIReportPanel from '../components/applications/AIReportPanel'
import { deleteApplication } from '../services/applications'

const PENDING_STATUSES = ['SUBMITTED', 'PROCESSING']
const DELAY_THRESHOLD_MS = 2 * 60 * 1000 // 2 minutes

export default function ApplicationDetailPage() {
  const { number } = useParams<{ number: string }>()
  const navigate = useNavigate()
  const { application, loading, error, submitting, submit } = useApplication(number!)
  const [showDelayBanner, setShowDelayBanner] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  useEffect(() => {
    if (!application || !PENDING_STATUSES.includes(application.status)) {
      setShowDelayBanner(false)
      return
    }
    const timer = setTimeout(() => setShowDelayBanner(true), DELAY_THRESHOLD_MS)
    return () => clearTimeout(timer)
  }, [application?.status])

  async function handleDelete() {
    if (!application) return
    if (!window.confirm('Delete this application? This cannot be undone.')) return
    setDeleting(true)
    setDeleteError(null)
    try {
      await deleteApplication(application.application_number)
      navigate('/applications')
    } catch {
      setDeleteError('Failed to delete application.')
      setDeleting(false)
    }
  }

  if (loading) return <p className="text-gray-500">Loading…</p>
  if (error || !application) return <p className="text-red-600">{error ?? 'Not found.'}</p>

  const canDelete = !PENDING_STATUSES.includes(application.status)
  const canEdit = application.status === 'DRAFT'

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-semibold">{application.application_number}</h1>
          <p className="text-sm text-gray-500 mt-0.5">{application.procedure}</p>
        </div>
        <ApplicationStatusBadge status={application.status} />
      </div>

      {showDelayBanner && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4 text-sm text-yellow-800">
          Processing is taking longer than expected. This may indicate that the processing
          service is temporarily unavailable. The application will be processed once the
          service recovers — no action is required.
        </div>
      )}

      {application.status === 'FAILED' && (
        <div className="bg-red-50 border border-red-200 rounded p-4 text-sm text-red-700">
          This application could not be processed due to a system error. This is not a rejection —
          the application was not evaluated. Please try submitting again or contact support.
        </div>
      )}

      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-sm font-medium text-gray-700 mb-3">Form data</h2>
        <pre className="text-xs text-gray-600 overflow-auto">
          {JSON.stringify(application.form_data, null, 2)}
        </pre>
      </div>

      {application.documents.length > 0 && (
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-sm font-medium text-gray-700 mb-3">Documents</h2>
          <ul className="space-y-2">
            {application.documents.map(doc => (
              <li key={doc.id} className="flex items-center justify-between text-sm">
                <span className="text-gray-800">{doc.file_name}</span>
                <span className="text-xs text-gray-400 uppercase">{doc.file_format}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {application.report && <AIReportPanel report={application.report} />}

      {deleteError && (
        <p className="text-sm text-red-600">{deleteError}</p>
      )}

      <div className="flex gap-2 flex-wrap">
        {canEdit && (
          <Link
            to={`/applications/${application.application_number}/edit`}
            className="bg-gray-100 text-gray-700 text-sm px-4 py-2 rounded hover:bg-gray-200"
          >
            Edit
          </Link>
        )}
        {canEdit && (
          <button
            onClick={submit} disabled={submitting}
            className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? 'Submitting…' : 'Submit for processing'}
          </button>
        )}
        {canDelete && (
          <button
            onClick={handleDelete} disabled={deleting}
            className="ml-auto text-sm text-red-600 border border-red-200 px-4 py-2 rounded hover:bg-red-50 disabled:opacity-50"
          >
            {deleting ? 'Deleting…' : 'Delete'}
          </button>
        )}
      </div>
    </div>
  )
}
