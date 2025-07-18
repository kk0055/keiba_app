FROM python:3.11-slim

# apt-get installが対話的に動作しないように設定 (重要)
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    # General build tools and Python development headers for C extensions
    build-essential \
    python3-dev \
    pkg-config \
    libffi-dev \
    \
    # For mysqlclient (MySQL/MariaDB client development files)
    default-libmysqlclient-dev \
    \
    # For psycopg2-binary (PostgreSQL client development files, often needed even for binary)
    libpq-dev \
    \
    # For chromium and its dependencies
    chromium \
    chromium-driver \
    fonts-ipafont-gothic \
    # Other common imaging libraries (e.g., for Pillow, if it's a sub-dependency of Django/DRF)
    libjpeg-dev \
    zlib1g-dev \
    \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome/Chromedriver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/lib/chromium/chromedriver

WORKDIR /app

# Copy requirements.txt first for effective Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]