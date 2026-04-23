import http from './http'
import type { User, TokenPair } from '../types/auth'

export async function login(email: string, password: string): Promise<User> {
  const { data } = await http.post<TokenPair>('/api/v1/auth/login/', { email, password })
  localStorage.setItem('access_token', data.access)
  localStorage.setItem('refresh_token', data.refresh)
  return getMe()
}

export async function logout(): Promise<void> {
  const refresh = localStorage.getItem('refresh_token')
  if (refresh) await http.post('/api/v1/auth/logout/', { refresh }).catch(() => {})
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function getMe(): Promise<User> {
  const { data } = await http.get<User>('/api/v1/auth/me/')
  return data
}