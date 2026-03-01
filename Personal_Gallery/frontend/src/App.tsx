import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { LoginPage } from './pages/LoginPage'
import { GalleryPage } from './pages/GalleryPage'
import { EntryDetailPage } from './pages/EntryDetailPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
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
            path="/gallery/:slug"
            element={
              <ProtectedRoute>
                <EntryDetailPage />
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