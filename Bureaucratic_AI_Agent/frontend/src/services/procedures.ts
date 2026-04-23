import http from './http'
import type { Procedure } from '../types/procedure'

export async function listProcedures(): Promise<Procedure[]> {
  const { data } = await http.get<Procedure[]>('/api/v1/procedures/')
  return data
}