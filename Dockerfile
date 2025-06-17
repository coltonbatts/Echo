# Echo Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn[standard] openai pyyaml

# Copy only necessary files
COPY backend/ ./backend/
COPY prompts/ ./prompts/

# Expose port
EXPOSE 8000

# Command to run the server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
