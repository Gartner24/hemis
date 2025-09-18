# Multi-stage Dockerfile for HEMIS Backend

# Stage 1: Build stage
FROM python:3.12-alpine AS builder

WORKDIR /backend

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    pkgconfig \
    curl

# Copy requirements first for caching
COPY requirements.txt ./

# Install dependencies into system (not --user!)
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache curl dumb-init

# Create non-root user
RUN addgroup -S hemis && \
    adduser -S -G hemis hemis-backend-user && \
    mkdir -p /var/log/hemis && \
    chown -R hemis-backend-user:hemis /var/log/hemis

WORKDIR /backend

# Copy installed packages from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY --chown=hemis-backend-user:hemis . .

# Environment for logs
ENV LOG_FILE=/var/log/hemis/hemis.log

USER hemis-backend-user

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]