import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services/auth.service'
import type { AuthContextType, User } from '../types/auth.types'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const checkAuth = useCallback(async () => {
    try {
      if (!authService.hasTokens()) {
        setLoading(false)
        return
      }

      const response = await authService.getCurrentUser()
      setUser(response.data)
      setIsAuthenticated(true)
    } catch (error) {
      console.error('Auth check failed:', error)
      authService.logout()
      setUser(null)
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (email: string, password: string) => {
    // Login and immediately set user state without triggering full checkAuth
    // This prevents unnecessary re-renders and allows navigation to work properly
    await authService.login(email, password)
    const response = await authService.getCurrentUser()
    setUser(response.data)
    setIsAuthenticated(true)
  }

  const logout = () => {
    authService.logout()
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
