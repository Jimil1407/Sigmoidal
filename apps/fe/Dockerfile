# syntax=docker/dockerfile:1

FROM node:22-alpine AS base
WORKDIR /repo

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@9.12.3 --activate

# Copy workspace manifests
COPY pnpm-workspace.yaml ./pnpm-workspace.yaml
COPY package.json ./package.json
COPY pnpm-lock.yaml ./pnpm-lock.yaml

# Copy packages and app manifests
COPY packages ./packages
COPY apps/fe/package.json ./apps/fe/package.json

# Install deps
RUN pnpm -w install --frozen-lockfile

# Build app
COPY apps/fe ./apps/fe
RUN cd apps/fe && pnpm build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy built standalone output
COPY --from=base /repo/apps/fe/.next/standalone ./
COPY --from=base /repo/apps/fe/.next/static ./apps/fe/.next/static
COPY --from=base /repo/apps/fe/public ./apps/fe/public

ENV PORT=3000
EXPOSE 3000

CMD ["node", "server.js"]
