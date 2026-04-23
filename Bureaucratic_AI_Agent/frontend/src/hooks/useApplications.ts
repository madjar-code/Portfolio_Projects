import { useState, useEffect, useCallback } from 'react'
import { listApplications } from '../services/applications'
import { useSSE } from './useSSE'
import type { ApplicationSummary, ApplicationStatus } from '../types/applications'

export function useApplications() {
  const [applications, setApplications] = useState<ApplicationSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      setApplications(await listApplications())
      setError(null)
    } catch {
      setError('Failed to load applications.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const patchStatus = useCallback((id: string, status: ApplicationStatus) => {
    setApplications(prev =>
      prev.map(a => a.id === id ? { ...a, status } : a)
    )
  }, [])

  useSSE(patchStatus)

  return { applications, loading, error, refetch: fetch }
}