FROM python:3.11-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install docker requests pyyaml

# Create app directory
WORKDIR /app

# Copy application files
COPY mock_falco.py /app/
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create log directory
RUN mkdir -p /var/log/falco

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DOCKER_API_VERSION=1.41

# Run the mock Falco service
ENTRYPOINT ["/app/entrypoint.sh"]
