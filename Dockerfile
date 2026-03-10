# --- STAGE 1: Builder (The "Workshop") ---
# We use a full-featured image to compile C-extensions like cryptg
FROM python:3.11-slim AS builder

# Install compilers needed for cryptg and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Create a virtual environment to isolate all installed libraries
RUN python -m venv /opt/venv
# Ensure subsequent commands use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# Install requirements into the virtualenv
RUN pip install --no-cache-dir -r requirements.txt


# --- STAGE 2: Final (The "Product") ---
# We go back to a clean, slim image for the actual running app
FROM python:3.11-slim

WORKDIR /app

# 1. Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Kolkata
# Link the virtualenv from the builder to this stage's PATH
ENV PATH="/opt/venv/bin:$PATH"

# 2. Install only runtime essentials (tzdata)
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# 3. MAGIC STEP: Copy ONLY the pre-compiled libraries from the builder
COPY --from=builder /opt/venv /opt/venv

# 4. Copy your application code
COPY . .

# Expose Flask
EXPOSE 5000

CMD ["python", "app.py"]
