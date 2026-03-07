# Frontend Technical Overview

## Tech Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.0 | UI library for component-based interfaces |
| **TypeScript** | 5.9.3 | Type-safe JavaScript with static typing |
| **Vite** | 7.3.1 | Fast build tool and dev server |
| **Styled Components** | 6.3.11 | CSS-in-JS for component styling |
| **React Router** | 7.13.1 | Client-side routing |
| **Axios** | 1.13.5 | HTTP client for API requests |

### Additional Libraries
- **@react-oauth/google** - Google OAuth 2.0 integration
- **@tanstack/react-query** - Server state management (optional)

---

## Project Structure

```
frontend/src/
├── components/          # Reusable UI components
│   ├── common/          # Generic components (modals, buttons, dropdowns)
│   ├── gallery/         # Gallery-specific components (photo grid, entry list)
│   └── icons/           # SVG icon components
│
├── contexts/            # React Context providers (Auth, Toast)
├── hooks/               # Custom React hooks (useInfiniteScroll)
├── pages/               # Page-level components (Login, Gallery, Entry pages)
├── services/            # API service layer (auth, photos)
├── styles/              # Global styles and theme configuration
└── types/               # TypeScript type definitions
```

---

## Styling with Styled Components

### Theme System

All styling is done through **Styled Components** with a centralized theme:

**Theme Configuration (`styles/theme.ts`):**
```typescript
export const theme = {
  colors: {
    primary: '#4285F4',      // Google Blue
    secondary: '#34A853',    // Google Green
    danger: '#EA4335',       // Google Red
    warning: '#FBBC04',      // Google Yellow
    background: '#FFFFFF',
    text: '#202124',
    // ...
  },
  spacing: { xs: '4px', sm: '8px', md: '16px', lg: '24px', xl: '32px' },
  borderRadius: { sm: '4px', md: '8px', lg: '12px', full: '9999px' },
  breakpoints: { mobile: '480px', tablet: '768px', desktop: '1024px' },
}
```

### Usage Example

```typescript
import styled from 'styled-components'

const Button = styled.button`
  padding: ${({ theme }) => theme.spacing.md};
  background: ${({ theme }) => theme.colors.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  
  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    padding: ${({ theme }) => theme.spacing.lg};
  }
`
```

### Benefits
- Component-scoped CSS (no global conflicts)
- Dynamic styling based on props and theme
- TypeScript support for theme values
- Responsive design with media queries

---

## Design Patterns

### 1. Service Layer Pattern

API calls are abstracted into service modules for reusability and maintainability.

**Example (`services/photos.service.ts`):**
```typescript
export const photosService = {
  getEntries: (page: number = 1) => 
    api.get<PaginatedResponse<Entry>>('/entries/', { params: { page } }),
  
  createEntry: (data: { title: string; description?: string }) =>
    api.post<EntryDetail>('/entries/create/', data),
  
  uploadPhoto: (entryId: string, file: File) => {
    const formData = new FormData()
    formData.append('entry', entryId)
    formData.append('file', file)
    return api.post<Photo>('/photos/create/', formData)
  },
}
```

Benefits:
- Centralized API logic
- Easy to mock for testing
- Type-safe responses

---

### 2. Context Pattern

Global state is managed using React Context API.

**Example (`contexts/AuthContext.tsx`):**
```typescript
interface AuthContextType {
  user: User | null
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  
  // ... auth logic
  
  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

Contexts in the app:
- **AuthContext** - User authentication state
- **ToastContext** - Toast notification system

---

### 3. Custom Hooks Pattern

Reusable logic is extracted into custom hooks.

**Example (`hooks/useInfiniteScroll.ts`):**
```typescript
export const useInfiniteScroll = ({ loading, hasMore, onLoadMore }) => {
  const observerRef = useRef<IntersectionObserver | null>(null)
  
  const lastElementRef = useCallback((node: HTMLElement | null) => {
    if (loading) return
    if (observerRef.current) observerRef.current.disconnect()
    
    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore) {
        onLoadMore()
      }
    })
    
    if (node) observerRef.current.observe(node)
  }, [loading, hasMore, onLoadMore])
  
  return lastElementRef
}
```

---

### 4. Compound Components Pattern

Complex UI components are built using composition.

**Example (PhotoGrid + PhotoModal):**
```typescript
// PhotoGrid displays photos in a grid
<PhotoGrid 
  photos={photos} 
  onPhotoClick={handlePhotoClick}
  onPhotoDelete={handlePhotoDelete}
/>

// PhotoModal shows full-screen photo viewer
<PhotoModal
  photos={photos}
  currentIndex={currentIndex}
  onClose={handleClose}
  onNavigate={handleNavigate}
/>
```

---

## Icon System

### SVG Icon Components

All icons are implemented as React components using inline SVG for:
- Full styling control (color, size)
- No external dependencies
- Type-safe props
- Tree-shaking support

Icon Structure (components/icons/):
```typescript
// EditIcon.tsx
interface IconProps {
  size?: number
  color?: string
  className?: string
}

export const EditIcon: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className 
}) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke={color}
    strokeWidth="2"
    width={size}
    height={size}
    className={className}
  >
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
  </svg>
)
```

Centralized Export (components/icons/index.tsx):
```typescript
export { LogoutIcon } from './LogoutIcon'
export { EditIcon } from './EditIcon'
export { TrashIcon } from './TrashIcon'
export { ChevronLeftIcon } from './ChevronLeftIcon'
// ...
```

Usage:
```typescript
import { EditIcon, TrashIcon } from '../components/icons'

<button>
  <EditIcon size={16} color="#4285F4" />
  Edit
</button>
```

---

## State Management

### Local State
- **useState** - Component-level state
- **useReducer** - Complex state logic

### Global State
- **Context API** - Authentication, Toast notifications
- **React Query** (optional) - Server state caching

### Form State
- Controlled components with `useState`
- Form validation on submit

---

## Routing

React Router v7 is used for client-side routing:

```typescript
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  
  <Route path="/gallery" element={
    <ProtectedRoute>
      <GalleryPage />
    </ProtectedRoute>
  } />
  
  <Route path="/gallery/create" element={
    <ProtectedRoute>
      <EntryCreatePage />
    </ProtectedRoute>
  } />
  
  <Route path="/gallery/:slug" element={
    <ProtectedRoute>
      <EntryDetailPage />
    </ProtectedRoute>
  } />
</Routes>
```

Protected Routes:
- Check authentication status
- Redirect to login if not authenticated

---

## API Integration

### Axios Configuration

Base Setup (services/api.ts):
```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor - Add JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      // If refresh fails, redirect to login
    }
    return Promise.reject(error)
  }
)
```

### Error Handling
- Axios interceptors for global error handling
- Toast notifications for user feedback
- Automatic token refresh on 401 errors

---

## Build & Development

### Development
```bash
npm run dev          # Start dev server (http://localhost:5173)
npm run lint         # Run ESLint
```

### Production
```bash
npm run build        # Build for production (dist/)
npm run preview      # Preview production build
```

### Environment Variables
```env
VITE_API_URL=http://localhost:8000/api
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

---

## Key Features

- **Type Safety** - Full TypeScript coverage
- **Responsive Design** - Mobile-first approach
- **Theme System** - Centralized styling with Styled Components
- **Code Splitting** - Lazy loading with React Router
- **Hot Module Replacement** - Fast development with Vite
- **Authentication** - JWT + Google OAuth
- **Toast Notifications** - User feedback system
- **Infinite Scroll** - Optimized list rendering

---

Built with modern React best practices and TypeScript for type safety and maintainability.

