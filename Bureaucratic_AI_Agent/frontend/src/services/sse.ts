export function createSSEConnection(
  baseUrl: string,
  token: string,
  onMessage: (applicationId: string, status: string) => void,
  onError: () => void,
): () => void {
  const url = `${baseUrl}/api/v1/sse/?token=${encodeURIComponent(token)}`
  const source = new EventSource(url)

  // Backend sends named events ("event: application_updated"), not the default
  // message event — onmessage silently ignores them; addEventListener is required.
  source.addEventListener('application_updated', (event) => {
    try {
      const data = JSON.parse(event.data) as { application_id: string; status: string }
      onMessage(data.application_id, data.status)
    } catch {}
  })

  source.onerror = () => {
    onError()
  }

  return () => source.close()
}