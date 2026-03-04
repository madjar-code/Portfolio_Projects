import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { LoginPage } from './pages/LoginPage'
import { GalleryPage } from './pages/GalleryPage'
import { EntryDetailPage } from './pages/EntryDetailPage'
import { RegisterPage } from './pages/RegisterPage'
import { ActivationPage } from './pages/ActivationPage'
import { EntryEditPage } from './pages/EntryEditPage'
import { EntryCreatePage } from './pages/EntryCreatePage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/auth/activate/:uid/:token" element={<ActivationPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/gallery"
            element={
              <ProtectedRoute>
                <GalleryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/gallery/create"
            element={
              <ProtectedRoute>
                <EntryCreatePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/gallery/:slug"
            element={
              <ProtectedRoute>
                <EntryDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/gallery/:slug/edit"
            element={
              <ProtectedRoute>
                <EntryEditPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/gallery" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App