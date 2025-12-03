# AI Marketing Engine - Docker Configuration
# Multi-stage build for optimized production image

# ==========================================
# STAGE 1: Build Environment
# ==========================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies with npm ci for faster, reliable builds
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build arguments for environment configuration
ARG NODE_ENV=production
ARG VITE_APP_VERSION=1.0.0
ARG VITE_APP_ENV=production

# Set environment variables
ENV NODE_ENV=$NODE_ENV
ENV VITE_APP_VERSION=$VITE_APP_VERSION
ENV VITE_APP_ENV=$VITE_APP_ENV

# Build the application
RUN npm run build

# ==========================================
# STAGE 2: Runtime Environment
# ==========================================
FROM nginx:1.25-alpine AS production

# Install additional packages for enhanced functionality
RUN apk add --no-cache \
    curl \
    bash \
    jq

# Copy custom nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/default.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy additional static files
COPY public/icons /usr/share/nginx/html/icons
COPY public/manifest.json /usr/share/nginx/html/manifest.json
COPY public/sw.js /usr/share/nginx/html/sw.js

# Create nginx user and set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Copy health check script
COPY docker/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Copy entrypoint script
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Create directories for nginx
RUN mkdir -p /var/cache/nginx /var/log/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx

# Security: Run as non-root user
USER nginx

# Expose port
EXPOSE 80

# Health check configuration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Labels for metadata
LABEL maintainer="AI Marketing Engine Team <support@aimarketingengine.com>"
LABEL version="1.0.0"
LABEL description="AI Marketing Engine - Voice-controlled marketing intelligence platform"
LABEL org.opencontainers.image.title="AI Marketing Engine"
LABEL org.opencontainers.image.description="Voice-controlled marketing intelligence platform with real-time benchmark data"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="AI Marketing Engine Team"
LABEL org.opencontainers.image.source="https://github.com/aimarketingengine/web-app"
LABEL org.opencontainers.image.licenses="MIT"

# Start the application
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

# ==========================================
# DEVELOPMENT STAGE (for local development)
# ==========================================
FROM node:18-alpine AS development

WORKDIR /app

# Install system dependencies for development
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl \
    bash

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies including devDependencies
RUN npm install

# Copy source code
COPY . .

# Expose development port
EXPOSE 3000

# Development health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start development server
CMD ["npm", "run", "dev"]

# ==========================================
# TESTING STAGE
# ==========================================
FROM node:18-alpine AS testing

WORKDIR /app

# Install dependencies for testing
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl \
    bash \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont

# Set Chrome path for Puppeteer
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Run tests
CMD ["npm", "run", "test:ci"]

# ==========================================
# BUILD TARGETS
# ==========================================
# To build for production:
# docker build --target production -t ai-marketing-engine:latest .

# To build for development:
# docker build --target development -t ai-marketing-engine:dev .

# To run tests:
# docker build --target testing -t ai-marketing-engine:test .

# ==========================================
# DOCKER COMPOSE INTEGRATION
# ==========================================
# This Dockerfile is designed to work with docker-compose.yml
# for complete development and production environments