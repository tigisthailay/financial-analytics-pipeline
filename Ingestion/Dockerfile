# Dockerfile for Finnhub Producer
FROM python:3.9-slim

WORKDIR /app

COPY custom_logger.py .
COPY requirements.txt .
COPY data_ingestion.py .

# Copy all files in the directory into the container
# COPY . .

RUN pip install --no-cache-dir -r requirements.txt
# Set entrypoint
CMD ["python", "data_ingestion.py"]
