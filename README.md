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
├── feature/ai-agent-bureaucracy → merged
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

A modern, full-stack web application for managing and sharing personal photo collections with authentication and responsive UI.

#### Key Features
- JWT and Google OAuth 2.0 authentication
- Photo entry (album) management with shareable links
- Multi-file upload with drag-and-drop
- Responsive Material Design-inspired interface
- Soft deletion and recovery

#### Tech Stack
- **Backend**: Django + Django REST Framework + PostgreSQL
- **Frontend**: React + TypeScript + Styled Components
- **Key Technologies**: JWT authentication, Vite, Axios, Pillow

#### Highlights
- Repository pattern with custom managers
- UUID-based primary keys and random slug generation
- Infinite scroll and lazy loading
- Custom React hooks and Context API
- Image validation and optimization

[📖 Full Documentation](./Personal_Gallery/README.md)

---

### 2. Bureaucratic AI Agent
**Status**: ✅ Complete
**Branch**: `feature/ai-agent-bureaucracy` (merged)
**Directory**: `/Bureaucratic_AI_Agent`

An AI-powered platform that automates the validation of bureaucratic procedures (passport renewal, lease agreements, business registration) for Moldova. Applicants submit documents and form data; an autonomous LLM agent validates them against canonical procedure rules and returns a structured decision.

#### Key Features
- Autonomous ReAct agent (Action → Observation → Reflection) with tool use
- Multi-procedure support driven by a knowledge base of validation rules
- Document parsing for PDF, DOCX, and images (with Tesseract OCR)
- Real-time status updates to the frontend via Server-Sent Events
- Reliable task processing with Dead Letter Queues and retries
- Comprehensive evaluation framework with LLM-as-judge

#### Tech Stack
- **Backend**: Django + Django REST Framework + Celery + PostgreSQL + Redis + MinIO
- **Agent**: Python + LangChain + OpenAI/Anthropic + LangFuse (self-hosted) + Sentry
- **Frontend**: React + TypeScript + Vite
- **Infrastructure**: Docker Compose + RabbitMQ + Nginx + Prometheus + Grafana

#### Highlights
- Four-layer defense against prompt injection (sandboxing, system prompt rules, procedure rules, regex scanner)
- Versioned prompts with a registry, enabling A/B testing of agent behavior
- Self-hosted LLM observability with token, latency, and cost tracking per trace
- Async task pipeline with HMAC-authenticated callbacks between backend and agent
- Production-grade Docker Compose setup with isolated dev/prod configurations

---

## 🚀 Getting Started

Each project has its own setup instructions in its respective directory. Navigate to the project folder and follow the README.

```bash
# Example: Personal Gallery
cd Personal_Gallery
# Follow setup instructions in Personal_Gallery/README.md

# Example: Bureaucratic AI Agent
cd Bureaucratic_AI_Agent
# Follow setup instructions in Bureaucratic_AI_Agent/README.md
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
