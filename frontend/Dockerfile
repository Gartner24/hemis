# Stage 1: Build stage
FROM node:20-alpine AS builder

WORKDIR /frontend

RUN apk add --no-cache dumb-init

# Copy deps
COPY package*.json ./
COPY yarn.lock* ./

RUN npm ci --no-audit --no-fund && npm cache clean --force

COPY . .

RUN npm run build

# Stage 2: Serve static files with nginx
FROM nginx:alpine AS production

# Copy build output to nginx html dir
COPY --from=builder /frontend/dist /usr/share/nginx/html

# Replace default nginx config with minimal one
RUN rm /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
