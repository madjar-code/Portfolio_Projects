import { useEffect } from 'react'
import { createSSEConnection } from '../services/sse'
import type { ApplicationStatus } from '../types/applications'

export function useSSE(patchStatus: (id: string, status: ApplicationStatus) => void) {
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const close = createSSEConnection(
      import.meta.env.VITE_API_BASE_URL,
      token,
      (id, status) => patchStatus(id, status as ApplicationStatus),
      () => { /* reconnect is automatic via EventSource */ },
    )

    return close
  }, [patchStatus])
}