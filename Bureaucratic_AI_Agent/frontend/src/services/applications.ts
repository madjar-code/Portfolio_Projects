import http from './http'
import type { Application, ApplicationSummary } from '../types/applications'

interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}

export async function listApplications(): Promise<ApplicationSummary[]> {
  const { data } = await http.get<PaginatedResponse<ApplicationSummary>>('/api/v1/applications/')
  return data.results
}

export async function getApplication(number: string): Promise<Application> {
  const { data } = await http.get<Application>(`/api/v1/applications/${number}/`)
  return data
}

export async function createApplication(
  procedure: string,
  formData: Record<string, unknown>,
  document?: File,
): Promise<Application> {
  const body = new FormData()
  body.append('procedure', procedure)
  body.append('form_data', JSON.stringify(formData))
  if (document) body.append('document', document)
  const { data } = await http.post<Application>('/api/v1/applications/create/', body)
  return data
}

export async function submitApplication(number: string): Promise<Application> {
  const { data } = await http.post<Application>(`/api/v1/applications/${number}/submit/`)
  return data
}

export async function updateApplication(
  number: string,
  formData: Record<string, unknown>,
  document?: File,
): Promise<Application> {
  const body = new FormData()
  body.append('form_data', JSON.stringify(formData))
  if (document) body.append('document', document)
  const { data } = await http.patch<Application>(`/api/v1/applications/${number}/`, body)
  return data
}

export async function deleteApplication(number: string): Promise<void> {
  await http.delete(`/api/v1/applications/${number}/`)
}
