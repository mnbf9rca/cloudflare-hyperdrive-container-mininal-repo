# Minimal Dockerfile to reproduce Hyperdrive DNS issue
FROM python:3.13-slim

WORKDIR /app

# Install PostgreSQL client library (required for psycopg2)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install psycopg2
RUN pip install --no-cache-dir psycopg2-binary==2.9.10

# Copy test script
COPY test_connection.py .

# Set Python to unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Expose port 8000
EXPOSE 8000

# Run the test script
CMD ["python", "test_connection.py"]