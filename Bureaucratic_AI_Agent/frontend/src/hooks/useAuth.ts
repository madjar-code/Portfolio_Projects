import { useState, useEffect, useCallback } from 'react'
import { login as authLogin, logout as authLogout, getMe } from '../services/auth'
import type { User } from '../types/auth'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { setLoading(false); return }
    getMe().then(setUser).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const u = await authLogin(email, password)
    setUser(u)
  }, [])

  const logout = useCallback(async () => {
    await authLogout()
    setUser(null)
  }, [])

  return { user, loading, login, logout }
}