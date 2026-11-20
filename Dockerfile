# =====================================================================
# STAGE 1: Build React Frontend
# =====================================================================
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# =====================================================================
# STAGE 2: Python Backend Runtime
# =====================================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install uv for high-speed dependency resolution
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /bin/uv

# Copy project specification & install production dependencies
COPY pyproject.toml ./
RUN uv pip install --system -r pyproject.toml --extra-index-url https://download.pytorch.org/whl/cpu

# Copy application backend package
COPY deep_research/ ./deep_research/

# Copy built static frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose unified application port
EXPOSE 8000

# Healthcheck against our FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Start the unified FastAPI + Static UI Server
CMD ["uvicorn", "deep_research.api:api", "--host", "0.0.0.0", "--port", "8000"]
