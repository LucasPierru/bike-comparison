FROM python:3.13

# Install Playwright dependencies & browsers
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN playwright install --with-deps

COPY . .
CMD ["python", "scripts/specialized.py"]