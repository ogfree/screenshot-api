# Use slim Python base
FROM python:3.11-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates unzip \
    fonts-liberation libnss3 libxss1 libasound2 libatk-bridge2.0-0 \
    libgtk-3-0 libdrm2 libxdamage1 libgbm1 libu2f-udev libxshmfence1 \
    --no-install-recommends

# Install Google Chrome stable
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /app

# Copy dependencies first and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Make sure the script is executable
RUN chmod +x start.sh

# Expose FastAPI port
EXPOSE 10000

# Start FastAPI server
CMD ["./start.sh"]
