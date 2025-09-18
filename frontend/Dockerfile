# Multi-stage Dockerfile for HEMIS Frontend

# Stage 1: Build stage
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /frontend

# Install dumb-init for signal handling
RUN apk add --no-cache dumb-init

# Create non-root user (safe, no hardcoded UID/GID)
RUN addgroup -S hemis && \
    adduser -S -G hemis hemis-frontend-user

# Copy package files for caching
COPY package*.json ./
COPY yarn.lock* ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci --no-audit --no-fund && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production stage
FROM node:20-alpine AS production

# Install dumb-init and curl
RUN apk add --no-cache dumb-init curl

# Create non-root user (same as builder stage)
RUN addgroup -S hemis && \
    adduser -S -G hemis hemis-frontend-user

# Set working directory
WORKDIR /frontend

# Copy built application and metadata
COPY --from=builder --chown=hemis-frontend-user:hemis /frontend/dist ./dist
COPY --from=builder --chown=hemis-frontend-user:hemis /frontend/package*.json ./
COPY --from=builder --chown=hemis-frontend-user:hemis /frontend/vite.config.ts ./

# Install only production dependencies for runtime
RUN npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force && \
    rm -rf /tmp/* /var/cache/apk/*

# Switch to non-root user
USER hemis-frontend-user

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5173/ || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]
