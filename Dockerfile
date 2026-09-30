# Stage 1: Build the Node.js Frontend and Proxy Server
FROM node:20-slim AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the Vite frontend and compile the server.ts proxy
RUN npm run build

# Stage 2: Setup Python and Run
FROM python:3.11-slim

WORKDIR /app

# Install Node.js in the Python container
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure the backend module is accessible
ENV PYTHONPATH=/app

# Copy the built assets and backend source from the builder stage
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/backend ./backend
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# Ensure server uses production mode
ENV NODE_ENV=production

# The start command executes the compiled Node server, which spawns the FastAPI backend
CMD ["node", "dist/server.cjs"]
