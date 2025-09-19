# Build
FROM node:20-alpine AS builder
WORKDIR /frontend

# Accept build arguments for environment variables
ARG VITE_API_BASE_URL=https://hemis.gartnercodes.com/api
ARG VITE_WEBSOCKET_URL=wss://hemis.gartnercodes.com
ARG VITE_FRONTEND_PORT=80
ARG VITE_BACKEND_PORT=5000
ARG VITE_CORS_ORIGINS=https://hemis.gartnercodes.com
ARG VITE_TELEMETRY_UPDATE_INTERVAL=1000
ARG VITE_IOT_API_KEY=your_iot_device_api_key
ARG VITE_LOG_LEVEL=INFO
ARG VITE_NODE_ENV=production
ARG VITE_DEBUG=false

# Set environment variables for the build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WEBSOCKET_URL=$VITE_WEBSOCKET_URL
ENV VITE_FRONTEND_PORT=$VITE_FRONTEND_PORT
ENV VITE_BACKEND_PORT=$VITE_BACKEND_PORT
ENV VITE_CORS_ORIGINS=$VITE_CORS_ORIGINS
ENV VITE_TELEMETRY_UPDATE_INTERVAL=$VITE_TELEMETRY_UPDATE_INTERVAL
ENV VITE_IOT_API_KEY=$VITE_IOT_API_KEY
ENV VITE_LOG_LEVEL=$VITE_LOG_LEVEL
ENV VITE_NODE_ENV=$VITE_NODE_ENV
ENV VITE_DEBUG=$VITE_DEBUG

COPY package*.json ./
COPY yarn.lock* ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Serve static with Nginx
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=builder /frontend/dist ./
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
