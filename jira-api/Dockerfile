FROM python:3.11

WORKDIR /app

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgobject-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY templates/ ./templates/
COPY generate_report.py ./
COPY api.py ./

# Create reports directory
RUN mkdir -p /app/reports

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "api.py"]


