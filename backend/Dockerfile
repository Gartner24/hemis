# Multi-stage Dockerfile for HEMIS Backend

# Stage 1: Build stage
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

# Create non-root user
RUN addgroup -S hemis && \
    adduser -S -G hemis hemis-backend-user

# Copy requirements first for caching
COPY requirements.txt ./

# Install Python dependencies into a neutral path
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-alpine AS production

RUN apk add --no-cache curl dumb-init

# Create same non-root user
RUN addgroup -S hemis && \
    adduser -S -G hemis hemis-backend-user

WORKDIR /backend

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=hemis-backend-user:hemis . .

USER hemis-backend-user

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
