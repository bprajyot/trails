FROM python:3.9-slim

# Create non-root user for security
RUN useradd -m -u 1001 coderunner

# Install required packages
RUN apt-get update && apt-get install -y \
    timeout \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy execution script
COPY execute.py /app/execute.py

# Set permissions
RUN chmod +x /app/execute.py
RUN chown coderunner:coderunner /app

# Switch to non-root user
USER coderunner

# Set resource limits
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "/app/execute.py"]