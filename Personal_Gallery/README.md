# 📸 Personal Gallery

A modern, full-stack web application for managing and sharing personal photo collections. Built with Django REST Framework and React with TypeScript.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Future Work](#future-work)

---

## 🎯 Overview

Personal Gallery is a photo management application that allows users to:
- Create and organize photo entries (albums)
- Upload and manage photos with automatic validation
- Share entries via unique links
- Edit entry metadata (title, description)
- Soft-delete entries and photos (recoverable)

The application features a clean, Google Material Design-inspired UI with responsive layouts for mobile and desktop.

---

## 🏗️ Architecture

### **High-Level Architecture**

```
┌─────────────┐      HTTP/REST      ┌─────────────┐
│   React     │ ←─────────────────→ │   Django    │
│  Frontend   │      JSON/JWT       │   Backend   │
└─────────────┘                     └─────────────┘
                                           │
                                           ↓
                                    ┌─────────────┐
                                    │  PostgreSQL │
                                    │  Database   │
                                    └─────────────┘
```

### **Backend Architecture**

- **Framework:** Django 5.1.5 + Django REST Framework
- **Authentication:** JWT (djangorestframework-simplejwt) + Google OAuth 2.0
- **Database:** PostgreSQL with UUID primary keys
- **File Storage:** Local filesystem (configurable for S3/cloud storage)
- **Key Patterns:**
  - Repository pattern with custom managers
  - Soft deletion for all models
  - UUID-based primary keys
  - Random slug generation for entries
  - Image validation and processing with Pillow

### **Frontend Architecture**

- **Framework:** React 19 + TypeScript
- **Routing:** React Router v7
- **Styling:** Styled Components with theme support
- **State Management:** React Context API (Auth, Toast)
- **HTTP Client:** Axios with interceptors
- **Key Patterns:**
  - Custom hooks (useInfiniteScroll, useAuth)
  - Context providers for global state
  - Compound components (PhotoGrid, PhotoModal)
  - Toast notification system

---

## ✨ Features

### **Authentication & Authorization**
- ✅ JWT-based authentication with refresh tokens
- ✅ Google OAuth 2.0 integration
- ✅ Email activation flow
- ✅ Protected routes and API endpoints

### **Entry Management**
- ✅ Create entries with title and description
- ✅ Random slug generation (8-character, URL-safe)
- ✅ Edit entry metadata
- ✅ Soft delete with confirmation modals
- ✅ Copy shareable links to clipboard

### **Photo Management**
- ✅ Multi-file upload with drag-and-drop support
- ✅ Client-side validation (format, size, count)
- ✅ Server-side validation before upload
- ✅ Image metadata extraction (dimensions, file size)
- ✅ Photo grid with responsive layout
- ✅ Full-screen photo viewer with navigation
- ✅ Delete photos with confirmation

### **UI/UX**
- ✅ Responsive design (mobile-first)
- ✅ Google Material Design color palette
- ✅ Toast notifications for user feedback
- ✅ Loading states and error handling
- ✅ Infinite scroll for entry list
- ✅ Smooth animations and transitions
- ✅ Dropdown menus for actions

### **Performance & Optimization**
- ✅ Lazy loading with infinite scroll
- ✅ Image optimization on upload
- ✅ Efficient database queries with prefetch_related
- ✅ JWT token refresh mechanism
- ✅ Debounced API calls

---

## 🛠️ Tech Stack

### **Backend**
- **Python:** 3.12+
- **Django:** 5.1.5
- **Django REST Framework:** 3.15.2
- **PostgreSQL:** 16+
- **JWT:** djangorestframework-simplejwt
- **OAuth:** google-auth, google-auth-oauthlib
- **Image Processing:** Pillow
- **CORS:** django-cors-headers

### **Frontend**
- **React:** 19.2.0
- **TypeScript:** 5.9.3
- **React Router:** 7.13.1
- **Styled Components:** 6.3.11
- **Axios:** 1.13.5
- **Google OAuth:** @react-oauth/google
- **Build Tool:** Vite 7.3.1

---

## 🚀 Getting Started

### **Prerequisites**

- Python 3.12+
- Node.js 18+ and npm
- PostgreSQL 16+
- Git

### **Project Initialization**

This project was initialized using modern Python and JavaScript tooling:

**Backend (Django with uv):**
```bash
# Install uv (fast Python package installer)
pip install uv

# Create Django project with uv
uv init backend
cd backend
uv add django djangorestframework
```

**Frontend (React with Vite):**
```bash
# Create React + TypeScript project with Vite
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### **Installation**

#### **1. Clone the repository**

```bash
git clone <repository-url>
cd Personal_Gallery
```

#### **2. Backend Setup**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (or use uv)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Or with uv:
# uv pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL
# - SECRET_KEY
# - GOOGLE_CLIENT_ID
# - GOOGLE_CLIENT_SECRET
# - EMAIL settings

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

#### **3. Frontend Setup**

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit .env with your configuration:
# - VITE_API_URL=http://localhost:8000
# - VITE_GOOGLE_CLIENT_ID

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### **Running the Application**

1. Start PostgreSQL database
2. Start backend server: `cd backend && python manage.py runserver`
3. Start frontend dev server: `cd frontend && npm run dev`
4. Open browser at `http://localhost:5173`

---

## 📁 Project Structure

```
Personal_Gallery/
├── backend/
│   ├── apps/
│   │   ├── common/          # Shared utilities, mixins, managers
│   │   ├── photos/          # Photo & Entry models, API
│   │   └── users/           # User model, authentication
│   ├── config/              # Django settings, URLs
│   ├── media/               # Uploaded photos
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── common/      # Buttons, modals, dropdowns
│   │   │   ├── gallery/     # Photo grid, entry list
│   │   │   └── icons/       # SVG icon components
│   │   ├── contexts/        # React contexts (Auth, Toast)
│   │   ├── hooks/           # Custom hooks
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── styles/          # Global styles, theme
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## 📚 API Documentation

### **Authentication Endpoints**

```
POST   /api/auth/register/              # Register new user
POST   /api/auth/activate/<uid>/<token>/ # Activate account
POST   /api/auth/login/                 # Login with credentials
POST   /api/auth/google/                # Login with Google OAuth
POST   /api/auth/token/refresh/         # Refresh JWT token
GET    /api/auth/me/                    # Get current user
```

### **Entry Endpoints**

```
GET    /api/entries/                    # List user's entries (paginated)
POST   /api/entries/create/             # Create new entry
GET    /api/entries/<slug>/             # Get entry details
PUT    /api/entries/<slug>/update/      # Update entry
DELETE /api/entries/<slug>/delete/      # Soft delete entry
```

### **Photo Endpoints**

```
GET    /api/photos/                     # List user's photos
POST   /api/photos/create/              # Upload photo
POST   /api/photos/validate/            # Validate photo before upload
GET    /api/photos/<id>/                # Get photo details
DELETE /api/photos/<id>/delete/         # Soft delete photo
```

---

## 🔮 Future Work

### **Deployment**
- Deploy backend to cloud platform (Heroku, AWS, Railway, DigitalOcean)
- Deploy frontend to Vercel or Netlify
- Configure production environment variables
- Set up cloud storage for media files (S3, Cloudinary)
- Configure SSL/HTTPS and custom domain

### **Monitoring & CI/CD**
- Set up error tracking (Sentry)
- Implement CI/CD pipeline with GitHub Actions
- Add automated testing (pytest, Jest)
- Configure logging and performance monitoring
- Set up health check endpoints

### **Features**
- Photo tagging and search functionality
- Entry categories and collections
- Public/private entry visibility
- Photo editing tools (crop, rotate, filters)
- Social sharing capabilities
- Export entries as ZIP archives

### **Performance & Security**
- Implement CDN for images
- Add Redis caching layer
- Implement rate limiting
- Add two-factor authentication
- Set up content security policy

---

## 📝 License

This project is private and not licensed for public use.

---

## 👤 Author

**Ivan Madjar**
- GitHub: [@madjar-quorum](https://github.com/madjar-quorum)

---

## 🙏 Acknowledgments

- Google Material Design for color palette
- React community for excellent libraries
- Django REST Framework for robust API development

---

**Built with ❤️ using Django and React**

