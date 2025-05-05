FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if needed for Stable Diffusion)
RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose ports (gRPC + Gradio)
EXPOSE 50051 7860

# Run the unified entrypoint
CMD ["python", "main.py"]