# Build
FROM node:20-alpine AS builder
WORKDIR /frontend
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
