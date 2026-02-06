FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Copy application code
COPY . /app

# (Optional) Verify model presence or other setup steps
# The model files are copied via `COPY .` unless excluded in .dockerignore



# Set environment variables defaults
ENV PYTHONUNBUFFERED=1

CMD ["python", "monitor.py"]
