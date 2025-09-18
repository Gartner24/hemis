# Multi-stage Dockerfile for HEMIS Backend

FROM python:3.12-alpine AS builder
WORKDIR /backend

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    pkgconfig \
    curl

# Copy requirements first for caching
COPY requirements.txt ./

# Install Python dependencies globally (no --user, ensures Gunicorn is on PATH)
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.12-alpine AS production
RUN apk add --no-cache curl dumb-init

# Create non-root user
RUN addgroup -S hemis && \
    adduser -S -G hemis hemis-backend-user

WORKDIR /backend

# Copy installed Python packages
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY --chown=hemis-backend-user:hemis . .

# Switch to non-root
USER hemis-backend-user

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]