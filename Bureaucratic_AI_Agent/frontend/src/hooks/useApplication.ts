import { useState, useEffect, useCallback, useRef } from 'react'
import { getApplication, submitApplication } from '../services/applications'
import { useSSE } from './useSSE'
import type { Application, ApplicationStatus } from '../types/applications'

const TERMINAL: ApplicationStatus[] = ['APPROVED', 'REJECTED', 'FAILED']

export function useApplication(number: string) {
  const [application, setApplication] = useState<Application | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Stable ref so the SSE callback never needs to be recreated
  const applicationIdRef = useRef<string | null>(null)
  const numberRef = useRef(number)
  numberRef.current = number

  useEffect(() => {
    setLoading(true)
    getApplication(number)
      .then((app) => {
        setApplication(app)
        applicationIdRef.current = app.id
      })
      .catch(() => setError('Application not found.'))
      .finally(() => setLoading(false))
  }, [number])

  // Stable callback — no deps, reads current values via refs
  const patchStatus = useCallback((id: string, status: ApplicationStatus) => {
    if (applicationIdRef.current !== id) return
    setApplication(prev => prev ? { ...prev, status } : prev)
    // Terminal state means the AI report has been written — refetch to get it
    if (TERMINAL.includes(status)) {
      getApplication(numberRef.current).then(setApplication).catch(() => {})
    }
  }, [])

  useSSE(patchStatus)

  const submit = useCallback(async () => {
    if (!application) return
    setSubmitting(true)
    try {
      setApplication(await submitApplication(application.application_number))
    } catch {
      setError('Failed to submit application.')
    } finally {
      setSubmitting(false)
    }
  }, [application])

  return { application, loading, error, submitting, submit }
}