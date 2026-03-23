# Stage 1 — Build React frontend
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY src/epistemic_platform/frontend/package.json src/epistemic_platform/frontend/package-lock.json ./
RUN npm ci
COPY src/epistemic_platform/frontend/ .
RUN npm run build

# Stage 2 — Python application
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/

# Copy built frontend into source tree before pip install
COPY --from=frontend-build /frontend/dist/ src/epistemic_platform/frontend/dist/

RUN pip install --no-cache-dir .

COPY alembic/ alembic/
COPY alembic.ini .
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
