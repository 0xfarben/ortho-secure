FROM python:3.11-slim

# Prevent .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies, including MySQL client
RUN apt-get update && apt-get install -y default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Add wait-for script and make it executable
RUN chmod +x /app/wait-for.sh

# Set Python path for the app
ENV PYTHONPATH=/app

# Expose application port
EXPOSE 5000

# Default command
CMD ["python", "main.py"]
