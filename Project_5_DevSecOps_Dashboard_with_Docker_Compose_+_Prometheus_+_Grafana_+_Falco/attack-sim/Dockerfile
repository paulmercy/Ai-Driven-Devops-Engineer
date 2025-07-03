FROM python:3.11-slim

WORKDIR /app

# Install system tools for attack simulation
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install requests

# Copy attack simulation script
COPY simulate_attacks.py .

# Make script executable
RUN chmod +x simulate_attacks.py

# Run the simulation
CMD ["python", "simulate_attacks.py"]
