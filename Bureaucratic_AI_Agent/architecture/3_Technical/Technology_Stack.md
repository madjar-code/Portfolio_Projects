# Technology Stack

## Overview

The project uses a modern technology stack for three main components: Frontend (SPA), Backend API, and AI-Agent.

---

## Frontend (Web Client)

| Technology | Purpose |
|------------|------------|
| **Next.js** | React-based framework with SSR/SSG |
| **TypeScript** | Code typing |
| **React** | UI components |
| **Tailwind CSS** | Styling |
| **React Query / SWR** | Server state management |
| **EventSource (SSE)** | Real-time notifications from backend |

---

## Backend API

| Technology | Purpose |
|------------|------------|
| **Django** | Main web framework |
| **Django REST Framework** | REST API |
| **PostgreSQL** | Main database |
| **Celery** | Asynchronous tasks |
| **Redis / RabbitMQ** | Message broker for Celery |
| **S3 / MinIO** | Object Storage for documents |
| **JWT (simplejwt)** | Authentication |
| **Pydantic** | Validation of callback from AI agent |
| **Django Streaming (SSE)** | Push notifications to client |
| **Gunicorn / Uvicorn** | WSGI/ASGI server |

---

## AI-Agent

| Technology | Purpose |
|------------|------------|
| **Python 3.11+** | Main language |
| **LangChain / LangGraph** | AI workflow orchestration |
| **OpenAI API (GPT-4)** | Main LLM |
| **Anthropic API (Claude)** | Alternative LLM |
| **Tesseract / pytesseract** | OCR — text extraction from images |
| **PyMuPDF / pdfplumber** | PDF processing |
| **python-docx** | DOCX processing |
| **SQLite** | Local storage of procedure metadata |
| **Pydantic** | Data and AIReport validation |
| **httpx** | HTTP client for callback |

---

## Infrastructure & DevOps

| Technology | Purpose |
|------------|------------|
| **Docker** | Containerization |
| **Docker Compose** | Local development |
| **AWS** | Production infrastructure |
| **Nginx** | Reverse proxy |
| **GitHub Actions** | CI/CD |

---

## Monitoring & Observability

| Technology | Purpose |
|------------|------------|
| **Sentry** | Error tracking |
| **LangSmith** | AI agent tracing |
| **CloudWatch** | Logs (prod) |
| **LLM-as-Judge** | Agent evaluation |

---

## Development Tools

| Technology | Purpose |
|------------|------------|
| **UV / pip** | Python dependencies |
| **npm / pnpm** | JS dependencies |
| **Ruff / Black** | Python linting & formatting |
| **ESLint / Prettier** | JS/TS linting & formatting |
| **pytest** | Python tests |
| **mypy** | Static Python typing |

