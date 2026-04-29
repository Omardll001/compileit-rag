# ── Backend Dockerfile ──────────────────────────────────────────────────────
# Multi-stage build: keeps the final image lean (~200 MB vs ~900 MB)

# ── Stage 1: build / install deps ───────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml .
COPY app/ app/
COPY ingest/ ingest/

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -e .

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Chroma persists to a volume – mount /app/chroma_db in docker-compose / Cloud Run
VOLUME ["/app/chroma_db"]

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
