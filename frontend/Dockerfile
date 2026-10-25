# ============================================================
# GrowFlow Frontend — Multi-Stage Production Container
# Stage 1: Build React/Vite application
# Stage 2: Serve static distribution via lightweight Nginx
# ============================================================

# ------------------------------------------------------------
# Stage 1: Build Environment
# ------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies using package-lock.json
COPY package.json package-lock.json ./
RUN npm ci

# Copy application source
COPY . .

# Build-time environment variables for Vite bundle embedding
ARG VITE_API_BASE_URL=""
ARG VITE_SUPABASE_URL=""
ARG VITE_SUPABASE_ANON_KEY=""
ARG VITE_APP_ENV="development"
ARG VITE_APP_NAME="GrowFlow"

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY \
    VITE_APP_ENV=$VITE_APP_ENV \
    VITE_APP_NAME=$VITE_APP_NAME

# Execute production build (tsc -b && vite build)
RUN npm run build

# ------------------------------------------------------------
# Stage 2: Production Web Server
# ------------------------------------------------------------
FROM nginx:alpine

# Remove default Nginx site configuration
RUN rm -rf /etc/nginx/conf.d/*

# Copy custom Nginx configuration with SPA routing and API reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# Health check testing the Nginx health probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1/nginx-health || exit 1

CMD ["nginx", "-g", "daemon off;"]
