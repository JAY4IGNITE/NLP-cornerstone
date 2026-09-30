# Build stage for frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Production stage
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python configuration
COPY pyproject.toml .

# Install python dependencies with extras
RUN pip install --no-cache-dir ".[ml,providers]"

# Copy application files
COPY backend/ backend/
COPY scripts/ scripts/
COPY artifacts/ artifacts/
COPY data/ data/
COPY .env.example .env

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist/ ./frontend/dist/

# Set production environment variables
ENV APP_ENV=production
ENV LLM_PROVIDER=extractive
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Expose the application port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
