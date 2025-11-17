#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Senda API - Google Cloud Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if project ID is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide your Google Cloud Project ID${NC}"
    echo "Usage: ./setup-gcloud.sh YOUR_PROJECT_ID"
    exit 1
fi

PROJECT_ID=$1

echo -e "${GREEN}✓${NC} Using Project ID: $PROJECT_ID\n"

# Set project
echo -e "${BLUE}→${NC} Setting active project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "\n${BLUE}→${NC} Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
echo -e "${GREEN}✓${NC} Cloud Build API enabled"

gcloud services enable run.googleapis.com
echo -e "${GREEN}✓${NC} Cloud Run API enabled"

gcloud services enable secretmanager.googleapis.com
echo -e "${GREEN}✓${NC} Secret Manager API enabled"

gcloud services enable containerregistry.googleapis.com
echo -e "${GREEN}✓${NC} Container Registry API enabled"

# Get project number for IAM
echo -e "\n${BLUE}→${NC} Getting project number for IAM configuration..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
echo -e "${GREEN}✓${NC} Project Number: $PROJECT_NUMBER"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo "Next steps:"
echo "1. Create secrets in Secret Manager (see DEPLOYMENT.md)"
echo "2. Grant Cloud Run access to secrets"
echo "3. Deploy using: gcloud builds submit --config cloudbuild.yaml"

echo -e "\n${BLUE}Quick secrets setup:${NC}"
echo "Run these commands with your actual credentials:"
echo ""
echo "echo -n 'your_username' | gcloud secrets create PHOREST_USERNAME --data-file=-"
echo "echo -n 'your_password' | gcloud secrets create PHOREST_PASSWORD --data-file=-"
echo "echo -n '6Sg8C_kl47YIHlStGcv-_Q' | gcloud secrets create PHOREST_BUSINESS_ID --data-file=-"
echo "echo -n 'mfxegqrFVfJXm_G75LlO8w' | gcloud secrets create PHOREST_BRANCH_ID --data-file=-"
echo "echo -n 'your_telnyx_key' | gcloud secrets create TELNYX_API_KEY --data-file=-"
echo "echo -n 'your_gemini_key' | gcloud secrets create GEMINI_API_KEY --data-file=-"

echo -e "\n${BLUE}Grant IAM permissions:${NC}"
cat <<EOF

for SECRET in PHOREST_USERNAME PHOREST_PASSWORD PHOREST_BUSINESS_ID PHOREST_BRANCH_ID TELNYX_API_KEY GEMINI_API_KEY; do
  gcloud secrets add-iam-policy-binding \$SECRET \\
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \\
    --role="roles/secretmanager.secretAccessor"
done

EOF

echo -e "${GREEN}Done!${NC} Check DEPLOYMENT.md for complete instructions.\n"
