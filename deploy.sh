#!/bin/bash
# SafetyMind Auto-Report Deployment
# Target Server: 192.168.1.149

set -e

SERVER="100.74.53.2"
REMOTE_DIR="~/safetymind-auto-report"
ENV_FILE=".env"

echo "🚀 Deploying SafetyMind Auto-Report to $SERVER"

# 1. Prepare remote directory
ssh -o StrictHostKeyChecking=no "arturo@$SERVER" "mkdir -p $REMOTE_DIR/reports"

# 2. Transfer core configuration and compose
echo "📦 Transferring Orchestration files..."
scp -o StrictHostKeyChecking=no docker-compose.yml "$ENV_FILE" "arturo@$SERVER:$REMOTE_DIR/"

# 3. Sync jira-api (Go API)
echo "📦 Syncing jira-api..."
rsync -avz --exclude '*.exe' --exclude '*.test' jira-api/ "arturo@$SERVER:$REMOTE_DIR/jira-api/"

# 4. Sync jira-portal (Next.js Portal)
echo "📦 Syncing jira-portal (excluding node_modules)..."
rsync -avz --exclude 'node_modules' --exclude '.next' jira-portal/ "arturo@$SERVER:$REMOTE_DIR/jira-portal/"

# 5. Remote Execution: Build and Restart
echo "🐳 Rebuilding Containers on Server..."
ssh -o StrictHostKeyChecking=no "arturo@$SERVER" "
    cd $REMOTE_DIR
    docker compose down || true
    docker compose up --build -d
    echo '✅ Deployment successful!'
    docker ps | grep jira
"
