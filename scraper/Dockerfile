FROM python:3.13
# Install dependencies
RUN apt-get update && apt-get install -y \
  wget \
  unzip \
  curl \
  xvfb \
  gnupg \
  libnss3 \
  libgconf-2-4 \
  libxi6 \
  libgbm-dev \
  libx11-xcb1 \
  && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update \
  && apt-get install -y google-chrome-stable \
  && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
  wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" && \
  unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
  rm /tmp/chromedriver.zip
# Set Chrome options for headless mode
ENV DISPLAY=:99
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scripts/trek.py"]