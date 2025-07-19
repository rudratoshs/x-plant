# ──────────────────────────────────────────────────────────────────────────────
# 📄 File: Dockerfile
#
# 🧭 Purpose (Layman Explanation):
#   Instructions for building a container that packages our plant care app with
#   everything it needs to run — like creating a portable box with the app and 
#   all its requirements.
#
# 🧪 Purpose (Technical Summary):
#   Multi-stage Docker build for the FastAPI application with optimized Python 
#   environment, security hardening, and efficient layer caching for both 
#   development and production environments.
#
# 🔗 Dependencies:
#   - requirements/base.txt         → Python dependencies
#   - app/                          → Application source code
#   - config/                       → Configuration files
#   - Docker engine + BuildKit support
#
# 🔄 Connected Modules / Calls From:
#   - docker-compose.yml           → Build context reference
#   - CI/CD pipelines              → Automated image builds
#   - Production deployment scripts
#   - Development environment setup
# ──────────────────────────────────────────────────────────────────────────────

# Use Python 3.11 slim image for smaller size and security
FROM python:3.11-slim as base

# Set build arguments
ARG APP_ENV=development
ARG PYTHONPATH=/app

# Set environment variables
ENV PYTHONPATH=${PYTHONPATH} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Essential system packages
    curl \
    gcc \
    g++ \
    # Image processing libraries (for Pillow)
    libjpeg-dev \
    libpng-dev \
    # PostgreSQL client libraries
    libpq-dev \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first (for better layer caching)
COPY requirements/ requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy application code
COPY app/ app/
COPY config/ config/
COPY migrations/ migrations/
COPY scripts/ scripts/

# Create necessary directories
RUN mkdir -p logs && \
    mkdir -p /app/static && \
    mkdir -p /app/media

# Set ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose application port
EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]