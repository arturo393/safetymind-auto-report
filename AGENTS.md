# safetymind-auto-report

## Architecture

- **jira-api** (Go/Gin) → port 8080
- **jira-portal** (Next.js) → port 8501
- Deployed on `192.168.1.149` via Docker Compose

## Docker

Build context is root (`.`), not subdirectories:
```bash
docker build -t safetymind-jira-portal -f jira-portal/Dockerfile .
docker build -t safetymind-auto-report-api -f jira-api/Dockerfile .
```

Portal uses external pre-built image (`safetymind-jira-portal`). Build separately before deploying:
```bash
docker compose up -d
```

## Sync & Deploy

Local → server:
```bash
rsync -avz --exclude='node_modules' --exclude='.next' --exclude='.git' \
  safetymind-auto-report/ arturo@192.168.1.149:~/safetymind-auto-report/
```

## API Endpoints

- `GET /health` - health check
- `POST /api/generate` - body: `{project_key, report_type, use_ai}`
- `GET /api/reports/list`
- `GET /api/reports/download/:filename`

## Environment Variables

| Variable | Purpose |
|---------|--------|
| `JIRA_URL` | Atlassian URL |
| `JIRA_EMAIL` | Jira email |
| `JIRA_API_TOKEN` | Jira API token |
| `OLLAMA_URL` | Ollama endpoint (optional) |
| `NEXT_PUBLIC_API_URL` | Portal → API URL (default: `http://localhost:8080`) |

## Report Generation

Reports are generated as HTML and converted to PDF using wkhtmltopdf:
- HTML content with real Jira data (issues, metrics)
- AI executive summary (optional, uses Ollama)
- Output: PDF file

Response includes `engine` field: `"html"` (wkhtmltopdf conversion)

## Testing

API health:
```bash
curl http://192.168.1.149:8080/health
```

Generate test report:
```bash
curl -X POST http://192.168.1.149:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"project_key":"GMF","report_type":"progress","use_ai":false}'
```