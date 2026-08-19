# syntax=docker/dockerfile:1

# ============================================================
# Stage 1: Dependencies
# ============================================================

FROM node:22-alpine AS deps

WORKDIR /app

RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    libc6-compat

COPY ui/package*.json ./

RUN --mount=type=cache,target=/root/.npm npm ci


# ============================================================
# Stage 2: Builder
# ============================================================

FROM node:22-alpine AS builder

WORKDIR /app

RUN apk add --no-cache libc6-compat

COPY --from=deps /app/node_modules ./node_modules

COPY ui/package*.json ./
COPY ui/tsconfig.json ./
COPY ui/next.config.ts ./
COPY ui/components.json ./
COPY ui/sentry.edge.config.ts ./
COPY ui/sentry.server.config.ts ./
COPY ui/postcss.config.mjs ./

COPY ui/public ./public
COPY ui/src ./src


# ============================================================
# Next.js build-time configuration
# ============================================================

ENV NEXT_PUBLIC_NODE_ENV="oss"

ENV NEXT_TELEMETRY_DISABLED="1"

ENV NEXT_PUBLIC_APP_NAME="GenQuantaa Calling Agent"

# Server-side:
# UI container -> API container
ENV BACKEND_URL="http://api:8000"

# Browser-side:
# Browser on Windows -> API exposed on Windows host
ENV NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"

ENV NODE_OPTIONS="--max-old-space-size=4096"


# ============================================================
# Build
# ============================================================

RUN npm run build && \
    rm -rf /tmp/* /root/.npm /root/.next/cache


# ============================================================
# Stage 3: Production Runner
# ============================================================

FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# IMPORTANT:
# Next.js must listen on Docker port 3010
ENV HOSTNAME=0.0.0.0
ENV PORT=3010


# Create non-root user

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs


# Copy standalone Next.js application

COPY --from=builder --chown=nextjs:nodejs \
    /app/.next/standalone ./

COPY --from=builder --chown=nextjs:nodejs \
    /app/.next/static ./.next/static

COPY --from=builder --chown=nextjs:nodejs \
    /app/public ./public


# Run as non-root

USER nextjs

ENV PORT=3010
ENV HOSTNAME=0.0.0.0

EXPOSE 3010

CMD ["node", "server.js"]