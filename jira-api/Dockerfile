FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY jira-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY jira-api/src/ ./src/
COPY jira-api/config/ ./config/
COPY jira-api/templates/ ./templates/
COPY jira-api/generate_report.py ./
COPY jira-api/api.py ./

# Create reports directory
RUN mkdir -p /app/reports

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "api.py"]

