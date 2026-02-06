FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./

# Development target
FROM base AS development
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM base AS builder
RUN npm ci
COPY . .
RUN npm run build

# Production target
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./
RUN npm ci --omit=dev
ENV PORT=3000
EXPOSE 3000
CMD ["node", "build"]
