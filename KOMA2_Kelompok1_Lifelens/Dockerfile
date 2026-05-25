# ═══════════════════════════════════════════════════════════════
# LifeLens Backend — Dockerfile
# Kompatibel: Hugging Face Spaces (port 7860) + Docker biasa
# ═══════════════════════════════════════════════════════════════

FROM python:3.11-slim

WORKDIR /app

# System deps untuk numpy, scikit-learn, build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ML models
COPY ml_models/ /app/ml_models/

# Copy application code
COPY app/ /app/app/

# HF Spaces wajib port 7860, bisa di-override via env
ENV PORT=7860

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')" || exit 1

# Run dengan uvicorn — port dari env variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
