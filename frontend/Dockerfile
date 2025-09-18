# Multi-stage Dockerfile for HEMIS Frontend
# Stage 1: Build stage
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /frontend

# Install dumb-init for signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1000 -S nodejs && \
    adduser -S hemis-frontend-user -u 1000

# Copy package files for caching
COPY package*.json ./
COPY yarn.lock* ./

# Install dependencies
RUN npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production stage
FROM node:20-alpine AS production

# Install dumb-init and curl
RUN apk add --no-cache dumb-init curl

# Create non-root user
RUN addgroup -g 1000 -S nodejs && \
    adduser -S hemis-frontend-user -u 1000

# Set working directory
WORKDIR /frontend

# Copy built application
COPY --from=builder --chown=hemis-frontend-user:nodejs /frontend/dist ./dist
COPY --from=builder --chown=hemis-frontend-user:nodejs /frontend/package*.json ./
COPY --from=builder --chown=hemis-frontend-user:nodejs /frontend/vite.config.ts ./

# Install production dependencies
RUN npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force && \
    rm -rf /tmp/* /var/cache/apk/*

# Switch to non-root user
USER hemis-frontend-user

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5173/ || exit 1

# Use dumb-init for signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["npm", "start"]