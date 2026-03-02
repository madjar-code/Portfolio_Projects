export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
}

export interface User {
  id: string
  email: string
  name: string
  is_verified: boolean
  is_email_user: boolean
  is_oauth_user: boolean
  oauth_provider: string | null
  created_at: string
  updated_at: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export interface RegisterRequest {
  email: string
  name: string
  password: string
  re_password: string
}

export interface RegisterResponse {
  id: string
  email: string
  name: string
}

export interface ActivationRequest {
  uid: string
  token: string
}
