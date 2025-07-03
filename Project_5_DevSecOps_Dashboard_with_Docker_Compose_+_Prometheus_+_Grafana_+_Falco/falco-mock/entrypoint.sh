#!/bin/bash

echo "Starting Mock Falco Security Monitor..."
echo "Monitoring containers: ${MONITOR_CONTAINERS:-all}"
echo "Log level: ${FALCO_LOG_LEVEL:-INFO}"

# Wait for Docker socket to be available
while [ ! -S /var/run/docker.sock ]; do
    echo "Waiting for Docker socket..."
    sleep 2
done

echo "Docker socket available, starting monitoring..."

# Start the mock Falco service
exec python /app/mock_falco.py
