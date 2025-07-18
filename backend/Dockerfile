FROM python:3.11-slim

# apt-get installが対話的に動作しないように設定
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        # General build tools and Python development headers for C extensions
        build-essential \
        python3-dev \
        pkg-config \
        libffi-dev \
        \
        # For mysqlclient (MySQL/MariaDB client development files)
        default-libmysqlclient-dev \
        \
        # For psycopg2-binary (PostgreSQL client development files)
        libpq-dev \
        \
        # Other common imaging libraries (e.g., for Pillow)
        libjpeg-dev \
        zlib1g-dev \
        \
        # Chromium and its specific dependencies for headless usage
        # chromium-driver は chromium パッケージに含まれるか、個別にインストールが必要な場合がある
        # python:slim は Debian bullseye/bookworm ベースであるため、chromium が利用可能
        chromium \
        # fonts-ipafont-gothic は日本語フォント。必要なら含める
        fonts-ipafont-gothic \
        # Headless Chromium requires these X11 related libs
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libxrender1 \
        libxi6 \
        libnss3 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libasound2 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcairo2 \
        libdbus-1-3 \
        libegl1 \
        libglib2.0-0 \
        libgudev-1.0-0 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libu2f-udev \
        libvulkan1 \
        libxkbcommon0 \
        libxshmfence6 \
        libxtst6 \
        xdg-utils \
        # Ensure --no-install-recommends is at the end of apt-get install line
        --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome/Chromedriver
# Chromium driverは通常 /usr/bin/chromedriver に配置される
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver 

WORKDIR /app

# Copy requirements.txt first for effective Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
# uvicornはFastAPI/StarletteのWebサーバー
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]