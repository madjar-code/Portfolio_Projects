# Technology Stack

## Overview

The project uses a modern technology stack for three main components: Frontend (SPA), Backend API, and AI-Agent.

---

## Frontend (Web Client)

| Technology | Purpose |
|------------|------------|
| **React + Vite** | SPA framework |
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
| **Celery** | Asynchronous task manager |
| **RabbitMQ** | Message broker for Celery |
| **S3 / MinIO** | Object Storage for documents |
| **JWT (simplejwt)** | Authentication |
| **Pydantic** | Validation of callback from AI agent |
| **Django Streaming (SSE)** | Push notifications to client |
| **Gunicorn / Uvicorn** | WSGI/ASGI server |

---

## AI-Agent

| Technology | Purpose |
|------------|------------|
| **Python 3.12+** | Main language |
| **OpenAI API (gpt-4o-mini)** | Main LLM |
| **Anthropic API (Claude)** | Alternative LLM |
| **Tesseract / pytesseract** | OCR — text extraction from images (optional) |
| **PyMuPDF / pdfplumber** | PDF processing |
| **python-docx** | DOCX processing |
| **Markdown files** | Procedure knowledge base |
| **Pydantic** | Data and AIReport validation |
| **aio-pika** | RabbitMQ consumer (async) |
| **httpx** | HTTP client for callback |

---

## Infrastructure & DevOps

| Technology | Purpose |
|------------|------------|
| **Docker** | Containerization |
| **Docker Compose** | Local development |
| **DigitalOcean** | Production infrastructure |
| **Nginx** | Reverse proxy |
| **GitHub Actions** | CI/CD |

---

## Monitoring & Observability

| Technology | Purpose |
|------------|------------|
| **Sentry** | Error tracking |
| **Langfuse** | AI agent tracing |
| **Prometheus + Grafana** | Infrastructure metrics |
| **python-json-logger** | Structured logging |
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

