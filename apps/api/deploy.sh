#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Senda API - Quick Deploy${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Must run from apps/api directory${NC}"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No active Google Cloud project${NC}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✓${NC} Project: $PROJECT_ID"

# Check if secrets exist
echo -e "\n${BLUE}→${NC} Checking if secrets are configured..."
REQUIRED_SECRETS=("PHOREST_USERNAME" "PHOREST_PASSWORD" "TELNYX_API_KEY" "GEMINI_API_KEY")
MISSING_SECRETS=()

for SECRET in "${REQUIRED_SECRETS[@]}"; do
    if ! gcloud secrets describe $SECRET &>/dev/null; then
        MISSING_SECRETS+=($SECRET)
    fi
done

if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Missing secrets: ${MISSING_SECRETS[*]}"
    echo -e "${YELLOW}⚠${NC} Run ./setup-gcloud.sh first or create secrets manually"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build and deploy
echo -e "\n${BLUE}→${NC} Building and deploying to Cloud Run..."
gcloud builds submit --config cloudbuild.yaml

# Get the service URL
echo -e "\n${BLUE}→${NC} Getting service URL..."
SERVICE_URL=$(gcloud run services describe senda-api --region us-central1 --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  Deployment Successful!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    echo -e "Service URL: ${BLUE}$SERVICE_URL${NC}"
    echo -e "Webhook URL: ${BLUE}${SERVICE_URL}/webhook/call${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Update Telnyx webhook to: ${SERVICE_URL}/webhook/call"
    echo "2. Test by calling: +16815080516"
    echo "3. Monitor logs: gcloud run services logs tail senda-api --region us-central1"
else
    echo -e "\n${YELLOW}Deployment completed, but couldn't retrieve service URL${NC}"
    echo "Check Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
fi

echo ""
