# Use Python 3.11 slim image
FROM python:3.11-slim

# Install some utilities
RUN apt update && apt install -y --no-install-recommends \
    curl \
    mtr \
    iputils-ping \
    telnet \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=server.py

# Install Flask
RUN pip install --no-cache-dir flask==3.0.0 gunicorn==21.2.0

# Copy the application file
COPY server.py .

# Expose port 5000
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "server:app"]
