# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /frontend

COPY package*.json ./
COPY yarn.lock* ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy build output to Nginx html folder
COPY --from=builder /frontend/dist /usr/share/nginx/html

# Replace default server config (with SPA fallback)
COPY nginx.conf /opt/projects/proxy/conf.d/hemis.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
