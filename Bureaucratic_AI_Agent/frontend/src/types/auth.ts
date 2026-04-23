export interface User {
  id: string
  email: string
  full_name: string
  phone: string | null
  avatar: string | null
}

export interface TokenPair {
  access: string
  refresh: string
}