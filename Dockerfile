FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Copy model file explicitly to ensure it's in the expected location if not already covered by COPY . .
# (Assuming yolo26x.pt is in the root as seen in file list)
COPY yolo26x.pt /app/yolo26x.pt


# Set environment variables defaults
ENV PYTHONUNBUFFERED=1

CMD ["python", "monitor.py"]
