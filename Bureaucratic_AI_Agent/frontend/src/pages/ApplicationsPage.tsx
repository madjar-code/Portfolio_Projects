import { Link } from 'react-router-dom'
import { useApplications } from '../hooks/useApplications'
import ApplicationStatusBadge from '../components/applications/ApplicationStatusBadge'

export default function ApplicationsPage() {
  const { applications, loading, error } = useApplications()

  if (loading) return <p className="text-gray-500">Loading…</p>
  if (error) return <p className="text-red-600">{error}</p>

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Applications</h1>
        <Link to="/applications/create"
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700">
          New application
        </Link>
      </div>

      {applications.length === 0 && (
        <p className="text-gray-500">No applications yet.</p>
      )}

      <ul className="space-y-2">
        {applications.map(app => (
          <li key={app.id}>
            <Link to={`/applications/${app.application_number}`}
              className="block bg-white rounded-lg border p-4 hover:border-blue-400 transition-colors">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium text-gray-800">{app.application_number}</p>
                  <p className="text-sm text-gray-500 mt-0.5">{app.procedure}</p>
                </div>
                <ApplicationStatusBadge status={app.status} />
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {new Date(app.created_at).toLocaleDateString()}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}