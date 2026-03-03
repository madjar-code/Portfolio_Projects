import { api } from "./api"
import type {
  RegisterResponse,
  ActivationRequest,
  LoginResponse,
  RegisterRequest,
  User,
  GoogleOAuthResponse,
} from "../types/auth.types"

const TOKEN_KEY = "access_token"
const REFRESH_TOKEN_KEY = "refresh_token"

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post<LoginResponse>('/auth/jwt/create/', {
      email,
      password,
    })

    localStorage.setItem(TOKEN_KEY, response.data.access)
    localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh)

    return response.data
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },

  googleLogin: async (googleToken: string) => {
    const response = await api.post<GoogleOAuthResponse>('/auth/google/token/', {
      token: googleToken
    })

    localStorage.setItem(TOKEN_KEY, response.data.access)
    localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh)

    return response.data
  },

  register: async (data: RegisterRequest) => {
    const response = await api.post<RegisterResponse>('/auth/users/', data)
    return response.data
  },

  activateAccount: async (data: ActivationRequest) => {
    await api.post('/auth/users/activation/', data)
  },

  resendActivation: async (email: string) => {
    await api.post('/auth/users/resend_activation/', { email })
  },

  getCurrentUser: () => api.get<User>('/auth/users/me/'),

  refreshToken: async () => {
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refresh) throw new Error('No refresh token')

    const response = await api.post<{ access: string }>('/auth/jwt/refresh/', {
      refresh,
    })

    localStorage.setItem(TOKEN_KEY, response.data.access)
    return response.data.access
  },

  getAccessToken: () => localStorage.getItem(TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  hasTokens: () => !!localStorage.getItem(TOKEN_KEY),
}