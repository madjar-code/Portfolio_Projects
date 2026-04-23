import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/layout/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/LoginPage'
import ApplicationsPage from './pages/ApplicationsPage'
import ApplicationDetailPage from './pages/ApplicationDetailPage'
import ApplicationCreatePage from './pages/ApplicationCreatePage'
import ApplicationEditPage from './pages/ApplicationEditPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/applications" element={<ApplicationsPage />} />
          <Route path="/applications/create" element={<ApplicationCreatePage />} />
          <Route path="/applications/:number/edit" element={<ApplicationEditPage />} />
          <Route path="/applications/:number" element={<ApplicationDetailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}