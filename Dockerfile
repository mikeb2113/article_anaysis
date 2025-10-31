# Use a minimal base image with Python
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    jq \
    xvfb \
    libxi6 \
    #libgconf-2-4 \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libvulkan1 \
    libxcomposite1 \
    libxdamage1 \
    libxkbcommon0 \
    xdg-utils \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (latest version)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Fetch the exact Chrome version
RUN CHROME_VERSION=$(dpkg-query --showformat='${Version}' --show google-chrome-stable | cut -d'-' -f1) && \
    echo "Detected Chrome version: $CHROME_VERSION" && \
    CHROME_DRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json | \
    jq -r --arg version "$CHROME_VERSION" '.versions[] | select(.version==$version) | .downloads.chromedriver[] | select(.platform=="linux64").url') && \
    if [ -z "$CHROME_DRIVER_URL" ]; then \
        echo "No exact match found. Using latest ChromeDriver."; \
        CHROME_DRIVER_URL=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json | \
        jq -r '.versions[-1].downloads.chromedriver[] | select(.platform=="linux64").url'); \
    fi && \
    echo "Fetching ChromeDriver from: $CHROME_DRIVER_URL" && \
    wget -O /tmp/chromedriver.zip $CHROME_DRIVER_URL && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip

# Set environment variables to use Chrome and ChromeDriver
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_DRIVER=/usr/local/bin/chromedriver

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install Python dependencies (ensure all in one layer)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install requests feedparser beautifulsoup4 newspaper3k lxml_html_clean tenacity scikit-learn lxml selenium webdriver-manager

# Copy the application code
COPY app /app

# Make port 8000 available outside the container
EXPOSE 8000

# Run the application
CMD ["python3", "sentiment_analysis.py"]