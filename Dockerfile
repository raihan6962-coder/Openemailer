FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM python:3.12-slim AS backend-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev curl && rm -rf /var/lib/apt/lists/* && useradd -m -u 1000 appuser

COPY --from=backend-builder /app/wheels /wheels
COPY --from=backend-builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

COPY --chown=appuser:appuser backend/ /app/backend/
COPY --chown=appuser:appuser start.sh /app/start.sh
RUN chmod +x /app/start.sh

COPY --from=frontend-builder --chown=appuser:appuser /app/.next/standalone /app/frontend/
COPY --from=frontend-builder --chown=appuser:appuser /app/.next/static /app/frontend/.next/static
RUN mkdir -p /app/frontend/public

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-3000}/health || exit 1

EXPOSE 3000

CMD ["bash", "/app/start.sh"]
