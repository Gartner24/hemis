# Multi-stage Dockerfile for HEMIS Backend
# Stage 1: Build stage
FROM python:3.12-alpine AS builder

# Set working directory
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
RUN addgroup -g 1000 -S hemis-backend-user && \
    adduser -S hemis-backend-user -u 1000

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-alpine AS production

# Install system dependencies
RUN apk add --no-cache \
    curl \
    dumb-init

# Create non-root user
RUN addgroup -g 1000 -S hemis-backend-user && \
    adduser -S hemis-backend-user -u 1000

# Set working directory
WORKDIR /backend

# Copy Python packages from builder
COPY --from=builder /root/.local /home/hemis-backend-user/.local

# Copy application code
COPY --chown=hemis-backend-user:hemis-backend-user . .

# Add user's local bin to PATH
ENV PATH=/home/hemis-backend-user/.local/bin:$PATH

# Switch to non-root user
USER hemis-backend-user

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use dumb-init for signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the application with Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]