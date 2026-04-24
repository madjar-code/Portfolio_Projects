FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=config.settings.prod

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]