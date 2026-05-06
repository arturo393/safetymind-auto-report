# 🛡️ SafetyMind Auto-Report

> Automated Jira report generation with AI-powered insights.

---

## 🏛️ System Architecture

```
safetymind-auto-report/
├── jira-api/              # 🚀 Go/Gin API (port 8080)
│   ├── main.go            # Core API logic
│   ├── config/            # Project configurations (YAML)
│   ├── templates/         # HTML & LaTeX report templates
│   └── Dockerfile         # Multi-stage Go + LaTeX build
├── jira-portal/           # ⚛️ Next.js Portal (port 8501)
│   └── src/               # Atomic components & API routes
├── reports/               # 📂 Generated PDF/HTML reports
└── docker-compose.yml     # Orchestration
```

---

## 🚀 Quick Start

### Docker Compose (Recommended)
```bash
# Configure environment
cp .env.example .env
# Edit .env with your Jira credentials

# Build and run
docker compose up -d
```

### Local Development

#### API (Go):
```bash
cd jira-api
go run main.go
```

#### Portal (Next.js):
```bash
cd jira-portal
npm install
npm run dev
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/projects` | GET | List Jira projects |
| `/api/generate` | POST | Generate report |
| `/api/reports/list` | GET | List generated reports |
| `/api/reports/download/:filename` | GET | Download report |

### Generate Report Example:
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"project_key":"IM","report_type":"progress","use_ai":true,"use_latex":false}'
```

---

## 🔧 Environment Variables

| Variable | Purpose |
|----------|---------|
| `JIRA_URL` | Atlassian URL |
| `JIRA_EMAIL` | Jira email |
| `JIRA_API_TOKEN` | Jira API token |
| `OLLAMA_URL` | Ollama endpoint (optional) |
| `NEXT_PUBLIC_API_URL` | Portal → API URL |

---

© 2026 **SafetyMind Engineering**.
