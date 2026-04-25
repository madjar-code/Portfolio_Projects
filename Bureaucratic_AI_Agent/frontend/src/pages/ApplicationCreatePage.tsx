import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { listProcedures } from '../services/procedures'
import { createApplication } from '../services/applications'
import type { Procedure } from '../types/procedure'

function extractErrorMessage(data: unknown): string {
  if (!data || typeof data !== 'object') return 'Failed to create application.'
  const d = data as Record<string, unknown>
  if (typeof d.detail === 'string') return d.detail
  return Object.entries(d)
    .map(([field, msgs]) => {
      const text = Array.isArray(msgs) ? msgs.join(', ') : String(msgs)
      return `${field}: ${text}`
    })
    .join(' | ')
}

export default function ApplicationCreatePage() {
  const navigate = useNavigate()
  const [procedures, setProcedures] = useState<Procedure[]>([])
  const [selectedProcedure, setSelectedProcedure] = useState('')
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [rawJson, setRawJson] = useState('{}')
  const [file, setFile] = useState<File | undefined>()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    listProcedures().then(setProcedures).catch(() => setError('Failed to load procedures.'))
  }, [])

  const procedure = procedures.find(p => p.code === selectedProcedure)

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault()
    if (!selectedProcedure) return
    setError(null)
    setSubmitting(true)
    try {
      const app = await createApplication(selectedProcedure, formData, file)
      navigate(`/applications/${app.application_number}`)
    } catch (err: unknown) {
      const data = (err as { response?: { data?: unknown } }).response?.data
      setError(extractErrorMessage(data))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">New Application</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Procedure</label>
          <select
            value={selectedProcedure}
            onChange={e => { setSelectedProcedure(e.target.value); setFormData({}); setRawJson('{}') }}
            required
            className="w-full border rounded px-3 py-2 text-sm"
          >
            <option value="">Select a procedure…</option>
            {procedures.map(p => (
              <option key={p.code} value={p.code}>{p.name}</option>
            ))}
          </select>
          {procedure && <p className="text-xs text-gray-500 mt-1">{procedure.description}</p>}
        </div>

        {selectedProcedure && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Form data (JSON)</label>
            <textarea
              value={rawJson}
              onChange={e => {
                setRawJson(e.target.value)
                try { setFormData(JSON.parse(e.target.value)) } catch {}
              }}
              rows={6}
              className="w-full border rounded px-3 py-2 text-sm font-mono"
              placeholder="{}"
            />
          </div>
        )}

        {procedure?.document_required && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Document ({procedure.required_document_formats.join(', ')})
            </label>
            <label className="flex items-center gap-3 border rounded px-3 py-2 cursor-pointer hover:bg-gray-50">
              <span className="text-sm text-white bg-gray-600 rounded px-2 py-1 shrink-0">Choose file</span>
              <span className="text-sm text-gray-500 truncate">{file ? file.name : 'No file chosen'}</span>
              <input
                type="file"
                accept={procedure.required_document_formats.map(f => `.${f.toLowerCase()}`).join(',')}
                onChange={e => setFile(e.target.files?.[0])}
                required
                className="sr-only"
              />
            </label>
          </div>
        )}

        <button
          type="submit" disabled={submitting || !selectedProcedure}
          className="w-full bg-blue-600 text-white rounded px-3 py-2 text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Creating…' : 'Create application'}
        </button>
      </form>
    </div>
  )
}