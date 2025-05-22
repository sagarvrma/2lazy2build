FROM python:3.11-slim

# Install system dependencies that Playwright needs
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    xvfb \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (this works in Docker with root access)
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium

# Copy your application code
COPY . .

# Expose the port that Render expects
EXPOSE 10000

# Start the application
CMD ["python", "app.py"]