# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- Fixed `.env` typos: `JIRA_PERSONAL_*` → `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
- Implemented real Jira data fetching in `fetchJiraData()` (was returning dummy data)
- Created missing `jira-api/config/projects.yaml` and `jira-api/templates/` directory
- Fixed Ollama environment variable (`OLLAMA_HOST` → `OLLAMA_URL`)
- Updated README.md to reflect actual directory structure (`jira-api/`, `jira-portal/`)
- Updated `deploy.sh` with correct paths

### Added
- Real-time Jira issues fetching with metrics calculation (total, done, in progress, open issues)
- HTML templates for kickoff, progress, and final reports in `jira-api/templates/`
- Project configuration with client and project manager info in `jira-api/config/projects.yaml`

### Removed
- Orphaned `requirements.txt` (no Python code exists in project)

## [Previous]

### Added
- Go API (Gin framework) with 7 endpoints
- Next.js portal with atomic component design
- Docker compose orchestration
- Ollama AI integration for executive summaries
- LaTeX PDF generation support
