import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isRefreshing = false
let queue: Array<(token: string) => void> = []

http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    const isAuthEndpoint = original.url?.includes('/auth/login') || original.url?.includes('/auth/token/refresh')
    if (error.response?.status !== 401 || original._retry || isAuthEndpoint) {
      return Promise.reject(error)
    }
    original._retry = true

    if (isRefreshing) {
      return new Promise((resolve) => {
        queue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(http(original))
        })
      })
    }

    isRefreshing = true
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) throw new Error('No refresh token')
      const { data } = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/token/refresh/`,
        { refresh },
      )
      localStorage.setItem('access_token', data.access)
      queue.forEach((cb) => cb(data.access))
      queue = []
      original.headers.Authorization = `Bearer ${data.access}`
      return http(original)
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(error)
    } finally {
      isRefreshing = false
    }
  },
)

export default http