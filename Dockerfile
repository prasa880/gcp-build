# Stage 1: Build & Test Environment
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
# Install dependencies into a separate folder
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY . .

# Stage 2: Final Lean Runtime
FROM python:3.12-slim
WORKDIR /app
# Copy only the installed packages and your app code
COPY --from=builder /install /usr/local
COPY --from=builder /app /app

# Security: Run as a non-root user (Standard for GKE)
RUN useradd -m appuser
USER appuser

# Start your app
CMD ["python", "main.py"]
