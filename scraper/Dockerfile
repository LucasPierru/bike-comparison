FROM python:3.13
# Install dependencies
RUN apt-get update && apt-get install -y \
  wget \
  unzip \
  curl \
  chromium \
  chromium-driver

# Set environment variable for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/lib/chromium

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
# Set Chrome options for headless mode
ENV DISPLAY=:99
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scripts/trek.py"]