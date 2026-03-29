# Technology Stack

## Overview

Проект использует современный стек технологий для трёх основных компонентов: Frontend (SPA), Backend API и AI-Agent.

---

## Frontend (Web Client)

| Технология | Назначение |
|------------|------------|
| **Next.js** | React-based фреймворк с SSR/SSG |
| **TypeScript** | Типизация кода |
| **React** | UI-компоненты |
| **Tailwind CSS** | Стилизация |
| **React Query / SWR** | Управление серверным состоянием |
| **EventSource (SSE)** | Real-time уведомления от backend |

---

## Backend API

| Технология | Назначение |
|------------|------------|
| **Django** | Основной веб-фреймворк |
| **Django REST Framework** | REST API |
| **PostgreSQL** | Основная база данных |
| **Celery** | Асинхронные задачи |
| **Redis / RabbitMQ** | Message broker для Celery |
| **S3 / MinIO** | Object Storage для документов |
| **JWT (simplejwt)** | Аутентификация |
| **Pydantic** | Валидация callback от AI-агента |
| **Django Streaming (SSE)** | Push-уведомления клиенту |
| **Gunicorn / Uvicorn** | WSGI/ASGI сервер |

---

## AI-Agent

| Технология | Назначение |
|------------|------------|
| **Python 3.11+** | Основной язык |
| **LangChain / LangGraph** | Оркестрация AI-workflow |
| **OpenAI API (GPT-4)** | Основная LLM |
| **Anthropic API (Claude)** | Альтернативная LLM |
| **Tesseract / pytesseract** | OCR — извлечение текста из изображений |
| **PyMuPDF / pdfplumber** | Работа с PDF |
| **python-docx** | Работа с DOCX |
| **SQLite** | Локальное хранение метаданных процедур |
| **Pydantic** | Валидация данных и AIReport |
| **httpx** | HTTP-клиент для callback |

---

## Infrastructure & DevOps

| Технология | Назначение |
|------------|------------|
| **Docker** | Контейнеризация |
| **Docker Compose** | Локальная разработка |
| **AWS** | Продакшн-инфраструктура |
| **Nginx** | Reverse proxy |
| **GitHub Actions** | CI/CD |

---

## Monitoring & Observability

| Технология | Назначение |
|------------|------------|
| **Sentry** | Error tracking |
| **LangSmith** | Трассировка AI-агента |
| **CloudWatch** | Логи (prod) |
| **LLM-as-Judge** | Evaluation агента |

---

## Development Tools

| Технология | Назначение |
|------------|------------|
| **UV / pip** | Python dependencies |
| **npm / pnpm** | JS dependencies |
| **Ruff / Black** | Python linting & formatting |
| **ESLint / Prettier** | JS/TS linting & formatting |
| **pytest** | Python тесты |
| **mypy** | Статическая типизация Python |

