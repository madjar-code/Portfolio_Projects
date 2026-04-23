import { Outlet, Link, useNavigate } from 'react-router-dom'
import { logout } from '../../services/auth'

export default function AppLayout() {
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-6 py-3 flex justify-between items-center">
        <Link to="/applications" className="font-semibold text-gray-800">Bureaucratic AI</Link>
        <button onClick={handleLogout} className="text-sm text-gray-500 hover:text-gray-800">
          Logout
        </button>
      </nav>
      <main className="max-w-4xl mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}