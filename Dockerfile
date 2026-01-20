# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# build-essential: for compiling python packages (if needed)
# curl: for healthchecks
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
# Copy dependency definitions first
COPY pyproject.toml .
COPY README.md .

# Create a mock source directory to allow installing dependencies
# This tricks pip into installing the libs defined in pyproject.toml
# without needing the actual source code (which changes frequently).
RUN mkdir -p src/quantmind && touch src/quantmind/__init__.py

# Install dependencies (Cached Layer)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Now copy the real source code (Uncached Layer)
COPY src/ src/
COPY scripts/ scripts/
COPY tests/ tests/
COPY data/ data/

# Re-install in editable mode to link the real source code
RUN pip install --no-cache-dir -e .

# Expose ports
# 8501 for Streamlit (if we add it later)
# 8000 for FastAPI (if we add it later)
EXPOSE 8501 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose)
CMD ["python", "scripts/cli.py"]
