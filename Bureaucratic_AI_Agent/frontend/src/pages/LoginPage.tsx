import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(email, password)
      navigate('/applications')
    } catch {
      setError('Invalid credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow w-full max-w-sm space-y-4">
        <h1 className="text-xl font-semibold">Sign in</h1>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <input
          type="email" value={email} onChange={e => setEmail(e.target.value)}
          placeholder="Email" required
          className="w-full border rounded px-3 py-2 text-sm"
        />
        <input
          type="password" value={password} onChange={e => setPassword(e.target.value)}
          placeholder="Password" required
          className="w-full border rounded px-3 py-2 text-sm"
        />
        <button
          type="submit" disabled={loading}
          className="w-full bg-blue-600 text-white rounded px-3 py-2 text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}