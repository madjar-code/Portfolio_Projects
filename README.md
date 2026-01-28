# Portfolio Projects Collection

This repository serves as a **curated collection of portfolio projects** demonstrating various software development skills, architectural patterns, and technology stacks. Each project is developed independently in its own feature branch and merged into the main branch upon completion.

## 📋 Repository Structure

This is a **mono-repository** containing multiple independent projects. Each project:
- Lives in its own dedicated feature branch during development
- Has its own directory in the main branch after merging
- Includes comprehensive documentation and architecture diagrams
- Demonstrates specific technologies, patterns, or architectural approaches

## 🌳 Branching Strategy

```
main (production-ready projects)
├── feature/personal-gallery → merged
├── feature/project-2 → in development
└── feature/project-3 → planned
```

### Workflow:
1. **Development**: Each project is developed in a dedicated feature branch (e.g., `feature/personal-gallery`)
2. **Isolation**: Branches remain independent until the project reaches a stable, documented state
3. **Merge**: Once complete, the feature branch is merged into `main`
4. **Maintenance**: Bug fixes and updates are made directly in `main` or via hotfix branches

---

## 📂 Projects

### 1. Personal Gallery
**Status**: ✅ Complete
**Branch**: `feature/personal-gallery` (merged)
**Directory**: `/Personal_Gallery`

An educational web platform for uploading and managing a personal photo gallery with authentication.

#### Core Features
- **Authentication**: Google OAuth + Email/Password registration
- **Photo Management**: Upload photos individually or in batches, organized into "Entries" (albums)
- **Gallery Viewing**: Browse entries (index page) and view detailed entry pages with photos
- **Admin Panel**: Django Admin for moderation and management
- **Statistics**: Aggregated stats on entries (cached with Redis)

#### Tech Stack
- **Frontend**: React SPA (TypeScript optional)
- **Backend**: Django + Django REST Framework with JWT authentication
- **Database**: PostgreSQL (metadata)
- **Storage**: S3-compatible object storage (DigitalOcean Spaces/MinIO) for photos
- **Caching**: Redis
- **Background Tasks**: Celery (image processing, email notifications)
- **Deployment**: Docker + docker-compose + Nginx on VPS

#### Architecture
**N-tier monolithic backend** with clear layer separation:
1. **API Layer** (DRF Views) → thin controllers
2. **Serializers** → validation & transformation
3. **Service Layer** → business logic
4. **Models & Managers** → data persistence (no repository pattern)
5. **Adapters** → external services (S3, Redis, OAuth, SMTP)

#### Project Goals
Educational/portfolio project focused on:
- System design & architecture documentation
- Production-like infrastructure setup
- Working with object storage, caching, and background processing
- End-to-end development with proper deployment

[📖 Full Documentation](./Personal_Gallery/README.md)

---

## 🚀 Getting Started

Each project has its own setup instructions in its respective directory. Navigate to the project folder and follow the README.

```bash
# Example: Personal Gallery
cd Personal_Gallery
# Follow setup instructions in Personal_Gallery/README.md
```

---

## 🎯 Purpose

This repository demonstrates:
- **Full-stack development** capabilities across different technology stacks
- **Architectural thinking** with documented design decisions
- **Production-ready practices** including deployment, testing, and CI/CD
- **Clean code principles** with proper separation of concerns
- **DevOps skills** with containerization and infrastructure setup

---

## 📞 Contact

For questions or collaboration opportunities, please reach out via GitHub issues or the contact information in my profile.

---

## 📄 License

Each project may have its own license. Please refer to individual project directories for specific licensing information.
