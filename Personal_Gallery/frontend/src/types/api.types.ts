export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface APIError {
  error: {
    message: string
    code: string
    status: number
    details: Record<string, any>
  }
}