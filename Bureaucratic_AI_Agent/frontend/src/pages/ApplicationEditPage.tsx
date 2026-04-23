import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getApplication, updateApplication } from '../services/applications'
import { listProcedures } from '../services/procedures'
import type { Application } from '../types/applications'
import type { Procedure } from '../types/procedure'

function extractErrorMessage(data: unknown): string {
  if (!data || typeof data !== 'object') return 'Failed to update application.'
  const d = data as Record<string, unknown>
  if (typeof d.detail === 'string') return d.detail
  return Object.entries(d)
    .map(([field, msgs]) => {
      const text = Array.isArray(msgs) ? msgs.join(', ') : String(msgs)
      return `${field}: ${text}`
    })
    .join(' | ')
}

export default function ApplicationEditPage() {
  const { number } = useParams<{ number: string }>()
  const navigate = useNavigate()
  const [application, setApplication] = useState<Application | null>(null)
  const [procedure, setProcedure] = useState<Procedure | null>(null)
  const [formData, setFormData] = useState<Record<string, unknown>>({})
  const [formDataText, setFormDataText] = useState('')
  const [file, setFile] = useState<File | undefined>()
  const [loadError, setLoadError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    Promise.all([
      getApplication(number!),
      listProcedures(),
    ]).then(([app, procedures]) => {
      if (app.status !== 'DRAFT') {
        setLoadError('Only DRAFT applications can be edited.')
        return
      }
      setApplication(app)
      setFormData(app.form_data)
      setFormDataText(JSON.stringify(app.form_data, null, 2))
      const proc = procedures.find(p => p.code === app.procedure) ?? null
      setProcedure(proc)
    }).catch(() => setLoadError('Failed to load application.'))
  }, [number])

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault()
    if (!application) return
    setError(null)
    setSubmitting(true)
    try {
      await updateApplication(application.application_number, formData, file)
      navigate(`/applications/${application.application_number}`)
    } catch (err: unknown) {
      const data = (err as { response?: { data?: unknown } }).response?.data
      setError(extractErrorMessage(data))
    } finally {
      setSubmitting(false)
    }
  }

  if (loadError) return <p className="text-red-600">{loadError}</p>
  if (!application) return <p className="text-gray-500">Loading…</p>

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link to={`/applications/${application.application_number}`} className="text-sm text-gray-500 hover:text-gray-700">
          ← Back
        </Link>
        <h1 className="text-2xl font-semibold">Edit {application.application_number}</h1>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Procedure</label>
          <p className="text-sm text-gray-800 border rounded px-3 py-2 bg-gray-50">
            {procedure?.name ?? application.procedure}
          </p>
          <p className="text-xs text-gray-500 mt-1">Procedure cannot be changed after creation.</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Form data (JSON)</label>
          <textarea
            value={formDataText}
            onChange={e => {
              setFormDataText(e.target.value)
              try { setFormData(JSON.parse(e.target.value)) } catch {}
            }}
            rows={6}
            className="w-full border rounded px-3 py-2 text-sm font-mono"
          />
        </div>

        {procedure?.document_required && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Replace document (optional — {procedure.required_document_formats.join(', ')})
            </label>
            <label className="flex items-center gap-3 border rounded px-3 py-2 cursor-pointer hover:bg-gray-50">
              <span className="text-sm text-white bg-gray-600 rounded px-2 py-1 shrink-0">Choose file</span>
              <span className="text-sm text-gray-500 truncate">{file ? file.name : 'No file chosen'}</span>
              <input
                type="file"
                accept={procedure.required_document_formats.map(f => `.${f.toLowerCase()}`).join(',')}
                onChange={e => setFile(e.target.files?.[0])}
                className="sr-only"
              />
            </label>
            {application.documents.length > 0 && (
              <p className="text-xs text-gray-500 mt-1">
                Current: {application.documents[application.documents.length - 1].file_name}
              </p>
            )}
          </div>
        )}

        <button
          type="submit" disabled={submitting}
          className="w-full bg-blue-600 text-white rounded px-3 py-2 text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Saving…' : 'Save changes'}
        </button>
      </form>
    </div>
  )
}
