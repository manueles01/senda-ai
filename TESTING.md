# Senda AI - Testing Guide

This guide will help you verify that everything is running correctly.

## Prerequisites

Make sure you have:
1. Pulled the latest code from the `claude/fix-pydantic-settings-0175i5qfAarSu8iN1k9eJdHA` branch
2. Created your `.env` file from `.env.example`
3. Installed dependencies: `pip install -r requirements.txt`

## Step 1: Check Configuration

First, verify your configuration is loaded correctly:

```bash
# From the repository root
python check_config.py
```

This will:
- ✓ Check if your `.env` file exists
- ✓ Show which environment variables are configured
- ✓ Verify the Settings class loads without errors
- ✓ Mask sensitive values (API keys, passwords)

**Expected Output:**
```
Senda AI - Configuration Check
============================================================

✓ .env file found at: /path/to/senda-ai/.env

ℹ Application Settings:
  App Name: Senda AI API
  Debug Mode: False

ℹ API Configuration:
  ✓ Anthropic API Key: sk-a****
  ✓ Firebase Project ID: your_project_id
  ...
```

## Step 2: Start the Server

Navigate to the API directory and start uvicorn:

```bash
cd apps/api
uvicorn app.main:app --port 8000
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Step 3: Test the API

**In a new terminal**, run the test script:

```bash
# From the repository root (NOT apps/api)
python test_api.py
```

This will test:
- ✓ Root endpoint (`/`)
- ✓ Health check (`/health`)
- ✓ API documentation (`/docs`)

**Expected Output:**
```
Senda AI API - System Test
============================================================

ℹ Testing Root Endpoint: http://localhost:8000/
✓ Status: 200
✓ Response: {'message': 'Welcome to Senda AI API', 'status': 'running'}

ℹ Testing Health Check Endpoint: http://localhost:8000/health
✓ Status: 200
✓ Response: {'status': 'healthy', 'app_name': 'Senda AI API'}

============================================================
✓ All tests passed! (3/3)
```

## Step 4: Manual Browser Testing

Open your browser and visit:

1. **Root**: http://localhost:8000
   - Should show: `{"message": "Welcome to Senda AI API", "status": "running"}`

2. **Health Check**: http://localhost:8000/health
   - Should show: `{"status": "healthy", "app_name": "Senda AI API"}`

3. **API Documentation**: http://localhost:8000/docs
   - Should show: Interactive Swagger UI with all available endpoints

4. **Alternative Docs**: http://localhost:8000/redoc
   - Should show: ReDoc documentation interface

## Troubleshooting

### Configuration errors
If `check_config.py` fails:
- Verify `.env` file exists in the repository root
- Check that all required variables are set
- Ensure no syntax errors in `.env` (no quotes around values)

### Server won't start
If uvicorn fails to start:
- Check port 8000 is not already in use
- Verify you're in the `apps/api` directory
- Check for Python syntax errors in your code

### Tests fail
If `test_api.py` fails:
- Ensure the server is running on port 8000
- Check firewall/antivirus isn't blocking localhost
- Verify no proxy settings interfering with localhost connections

## What Was Fixed Today

The Pydantic validation errors have been resolved:

1. ✓ All fields properly defined in `Settings` class
2. ✓ `anthropic_api_key` field added
3. ✓ `firebase_project_id` field added
4. ✓ `extra='ignore'` configuration prevents future field errors
5. ✓ Complete FastAPI application structure created
6. ✓ Environment variable loading working correctly

Your API is now ready for development!
