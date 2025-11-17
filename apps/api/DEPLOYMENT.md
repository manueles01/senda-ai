# Senda API - Google Cloud Deployment Guide

This guide will help you deploy the Senda API to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **Google Cloud Project**
   - Create a project at https://console.cloud.google.com
   - Note your PROJECT_ID

2. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Linux
   curl https://sdk.cloud.google.com | bash

   # Windows
   # Download from https://cloud.google.com/sdk/docs/install
   ```

3. **Authenticate with Google Cloud**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Step 1: Enable Required APIs

Run the setup script to enable all necessary Google Cloud APIs:

```bash
chmod +x setup-gcloud.sh
./setup-gcloud.sh YOUR_PROJECT_ID
```

Or manually enable them:

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Step 2: Create Secrets in Secret Manager

You need to create secrets for sensitive data:

```bash
# Phorest credentials
echo -n "your_phorest_username" | gcloud secrets create PHOREST_USERNAME --data-file=-
echo -n "your_phorest_password" | gcloud secrets create PHOREST_PASSWORD --data-file=-
echo -n "6Sg8C_kl47YIHlStGcv-_Q" | gcloud secrets create PHOREST_BUSINESS_ID --data-file=-
echo -n "mfxegqrFVfJXm_G75LlO8w" | gcloud secrets create PHOREST_BRANCH_ID --data-file=-

# Telnyx credentials
echo -n "your_telnyx_api_key" | gcloud secrets create TELNYX_API_KEY --data-file=-

# Gemini API key
echo -n "your_gemini_api_key" | gcloud secrets create GEMINI_API_KEY --data-file=-
```

**Verify secrets:**
```bash
gcloud secrets list
```

## Step 3: Grant Cloud Run Access to Secrets

```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding PHOREST_USERNAME \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding PHOREST_PASSWORD \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding PHOREST_BUSINESS_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding PHOREST_BRANCH_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding TELNYX_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Step 4: Deploy to Cloud Run

### Option A: Using Cloud Build (Recommended for CI/CD)

```bash
# From the apps/api directory
gcloud builds submit --config cloudbuild.yaml
```

### Option B: Direct Deployment (Faster for testing)

```bash
# Build locally
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/senda-api

# Deploy
gcloud run deploy senda-api \
  --image gcr.io/YOUR_PROJECT_ID/senda-api \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 60s \
  --set-secrets=PHOREST_USERNAME=PHOREST_USERNAME:latest,PHOREST_PASSWORD=PHOREST_PASSWORD:latest,PHOREST_BUSINESS_ID=PHOREST_BUSINESS_ID:latest,PHOREST_BRANCH_ID=PHOREST_BRANCH_ID:latest,TELNYX_API_KEY=TELNYX_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-env-vars=PHOREST_BASE_URL=https://api-gateway-us.phorest.com,SALON_TIMEZONE=America/New_York,TELNYX_PHONE_NUMBER=+16815080516
```

## Step 5: Get Your Cloud Run URL

After deployment, you'll see output like:

```
Service [senda-api] revision [senda-api-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://senda-api-xxxxx-uc.a.run.app
```

**Save this URL - you'll need it for Telnyx!**

## Step 6: Update Telnyx Webhook

1. Go to Telnyx Portal: https://portal.telnyx.com
2. Navigate to your Voice AI application
3. Update the webhook URL to:
   ```
   https://senda-api-xxxxx-uc.a.run.app/webhook/call
   ```

## Step 7: Test the Deployment

### Test Health Endpoint

```bash
curl https://YOUR-CLOUD-RUN-URL.run.app/
```

### Test Webhook Health

```bash
curl https://YOUR-CLOUD-RUN-URL.run.app/webhook/health
```

### Test with a Call

Call your Telnyx number: **+16815080516**

## Monitoring & Logs

### View Logs

```bash
# Real-time logs
gcloud run services logs tail senda-api --region us-central1

# Recent logs
gcloud run services logs read senda-api --region us-central1 --limit 100
```

### View in Console

https://console.cloud.google.com/run?project=YOUR_PROJECT_ID

## Updating the Deployment

After making code changes:

```bash
# Commit your changes
git add .
git commit -m "Update API logic"

# Rebuild and deploy
gcloud builds submit --config cloudbuild.yaml
```

## Cost Optimization

**Current Configuration:**
- 0 minimum instances (scales to zero when idle)
- Up to 10 maximum instances (auto-scales based on traffic)
- 512MB memory per instance
- 1 CPU per instance

**Estimated Costs:**
- First 2 million requests/month: FREE
- After that: ~$0.40 per million requests
- CPU usage: ~$0.0000024 per second
- Memory: ~$0.0000025 per GB-second

**For low traffic (< 1000 calls/day):**
- Estimated monthly cost: **$5-10**

**To reduce cold starts (increase min-instances):**
```bash
gcloud run services update senda-api \
  --region us-central1 \
  --min-instances 1
```
*Note: This will increase costs to ~$40/month but eliminate cold start delays*

## Troubleshooting

### Check Container Logs
```bash
gcloud run services logs read senda-api --region us-central1 --limit 50
```

### Check Secret Access
```bash
gcloud secrets describe PHOREST_USERNAME
gcloud secrets versions access latest --secret=PHOREST_USERNAME
```

### Redeploy
```bash
gcloud run deploy senda-api \
  --image gcr.io/YOUR_PROJECT_ID/senda-api:latest \
  --region us-central1
```

### Test Locally First
```bash
# Build Docker image
docker build -t senda-api .

# Run locally
docker run -p 8080:8080 --env-file .env senda-api

# Test
curl http://localhost:8080/
```

## Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use Secret Manager** for all sensitive data
3. **Rotate secrets regularly** in Secret Manager
4. **Enable Cloud Armor** for DDoS protection (optional)
5. **Set up Cloud Monitoring alerts** for errors and high usage

## Next Steps

1. ✅ Deploy API to Cloud Run
2. ✅ Update Telnyx webhook
3. 🔲 Set up custom domain (optional)
4. 🔲 Add Cloud SQL for conversation logging (optional)
5. 🔲 Set up Cloud Monitoring dashboards
6. 🔲 Configure Cloud CDN (if needed)
7. 🔲 Deploy web dashboard to Firebase Hosting

---

**Need Help?**
- Google Cloud Run docs: https://cloud.google.com/run/docs
- Telnyx docs: https://developers.telnyx.com
- Check `claude.md` for API integration details
