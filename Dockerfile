FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Make server executable
RUN chmod +x server.py

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the MCP server
ENTRYPOINT ["python", "server.py"]
