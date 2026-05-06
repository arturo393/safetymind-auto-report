FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY templates/ ./templates/
COPY generate_report.py ./
COPY jira-api/api.py ./api.py

# Create reports directory
RUN mkdir -p /app/reports

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "api.py"]
