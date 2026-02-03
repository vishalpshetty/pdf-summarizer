# 🌐 Railway Deployment Guide

Complete guide to deploying your PDF Summarizer app to Railway with GitHub integration.

## Overview

You'll deploy two separate Railway services:
1. **Backend Service** (FastAPI) - Handles PDF processing and AI
2. **Frontend Service** (Streamlit) - User interface

Both will auto-deploy on every GitHub push!

## Prerequisites

- ✅ Railway account ([railway.app](https://railway.app))
- ✅ GitHub account
- ✅ Git installed locally
- ✅ Your API keys ready

---

## Part 1: Push to GitHub

### Step 1: Initialize Git Repository

```bash
# Navigate to your project folder
cd /Users/vishalhp/AI\ Folder

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: PDF Summarizer app"
```

### Step 2: Create GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the "+" icon → "New repository"
3. Name it `pdf-summarizer` (or any name you prefer)
4. **Important:** Do NOT initialize with README (we already have one)
5. Click "Create repository"

### Step 3: Push to GitHub

Copy the commands from GitHub (should look like this):

```bash
git remote add origin https://github.com/YOUR-USERNAME/pdf-summarizer.git
git branch -M main
git push -u origin main
```

Your code is now on GitHub! 🎉

---

## Part 2: Deploy Backend to Railway

### Step 1: Create New Project

1. Go to [railway.app](https://railway.app) and log in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your `pdf-summarizer` repository

### Step 2: Configure Backend Service

1. After selecting the repo, Railway will detect it
2. Click on the service settings (gear icon)
3. **Root Directory:** Set to `backend`
   - This tells Railway to look in the `backend` folder
4. **Service Name:** Change to `pdf-summarizer-backend`

### Step 3: Add Environment Variables

1. Go to the "Variables" tab in your backend service
2. Click "Add Variable" and add these:

```
ANTHROPIC_API_KEY = sk-ant-xxxxxxxxxxxxx
LANGSMITH_API_KEY = lsv2_pt_xxxxxxxxxxxxx
LANGSMITH_PROJECT_NAME = pdf-summarizer
```

### Step 4: Deploy!

1. Go to the "Deployments" tab
2. Click "Deploy"
3. Wait for the build to complete (2-3 minutes)
4. Once deployed, click "Generate Domain" to get your backend URL
5. **IMPORTANT:** Copy this URL! You'll need it for the frontend

Your backend URL will look like: `https://pdf-summarizer-backend.railway.app`

### Step 5: Test Backend

Visit `https://your-backend-url.railway.app/health` in your browser. You should see:

```json
{
  "status": "healthy",
  "anthropic_configured": true,
  "langsmith_configured": true
}
```

Also check the interactive docs: `https://your-backend-url.railway.app/docs`

---

## Part 3: Deploy Frontend to Railway

### Step 1: Create Frontend Service

1. Go back to your Railway dashboard
2. Click "New" → "GitHub Repo"
3. Select the SAME `pdf-summarizer` repository
4. Railway will create a second service

### Step 2: Configure Frontend Service

1. Click on the new service settings
2. **Root Directory:** Set to `frontend`
3. **Service Name:** Change to `pdf-summarizer-frontend`

### Step 3: Add Environment Variable

1. Go to "Variables" tab
2. Add ONE variable:

```
BACKEND_URL = https://your-backend-url.railway.app
```

**CRITICAL:** Use the backend URL you copied in Part 2, Step 4!

### Step 4: Deploy Frontend

1. Go to "Deployments" tab
2. Click "Deploy"
3. Wait for build (1-2 minutes)
4. Click "Generate Domain" to get your frontend URL

Your frontend URL will look like: `https://pdf-summarizer-frontend.railway.app`

### Step 5: Test the App!

1. Visit your frontend URL
2. Upload a PDF
3. Generate a summary
4. Success! 🎉

---

## Part 4: Enable Auto-Deploy

Good news: **Auto-deploy is already enabled!** ✅

Railway automatically sets up a GitHub webhook. Every time you push to the `main` branch:

1. Backend will rebuild and redeploy
2. Frontend will rebuild and redeploy
3. No manual intervention needed!

### Test Auto-Deploy

```bash
# Make a small change (e.g., edit README.md)
echo "\n## Updated!" >> README.md

# Commit and push
git add .
git commit -m "Test auto-deploy"
git push

# Watch Railway dashboard - both services will rebuild automatically!
```

---

## Part 5: Monitoring with LangSmith

### View Your Traces

1. Log in to [smith.langchain.com](https://smith.langchain.com)
2. Select your project (`pdf-summarizer`)
3. You'll see a trace for every PDF summarization request!

### What You Can See:

- **Input:** The PDF text sent to Claude
- **Output:** The generated summary
- **Cost:** Token usage and estimated cost
- **Latency:** How long the API call took
- **Metadata:** Model used, temperature, max tokens, etc.

This is incredibly useful for:
- Debugging issues
- Optimizing prompts
- Tracking costs
- Improving performance

---

## Troubleshooting

### Backend Build Fails

**Error:** `No module named 'anthropic'`
- **Fix:** Check that `requirements.txt` is in the `backend` folder
- Verify the Root Directory is set to `backend`

### Frontend Can't Connect to Backend

**Error:** `Could not connect to backend server`
- **Fix:** Double-check the `BACKEND_URL` environment variable
- Make sure it matches your backend's generated domain
- No trailing slash in the URL!

### Railway Build Timeout

**Error:** Build takes too long
- **Fix:** Railway has a 10-minute build limit
- This usually only happens if dependencies are very large
- Try clearing the build cache in Railway settings

### CORS Error in Browser

**Error:** `Access to XMLHttpRequest blocked by CORS policy`
- **Fix:** The backend has `allow_origins=["*"]` which should work
- For production, you may want to restrict this to your frontend URL

---

## Cost Estimation

### Railway Costs

- **Hobby Plan:** $5/month (includes $5 in usage)
- Each service uses ~0.5GB RAM
- Both services together: ~$5-10/month

### Claude API Costs (Anthropic)

- **Claude 3.5 Sonnet:** ~$3 per 1M input tokens
- Average PDF: ~5,000 tokens
- Cost per summarization: ~$0.015 (1.5 cents)
- 100 PDFs: ~$1.50

### LangSmith Costs

- **Free tier:** 5,000 traces/month
- Should be enough for testing and learning
- Paid plans start at $39/month for production use

**Total estimated cost for learning:** ~$10-15/month

---

## Security Best Practices

### For Production Deployment

1. **CORS Configuration:**
   ```python
   # In backend/main.py, replace:
   allow_origins=["*"]
   
   # With your actual frontend URL:
   allow_origins=["https://your-frontend.railway.app"]
   ```

2. **Rate Limiting:**
   - Consider adding rate limiting to prevent abuse
   - Railway has built-in DDoS protection

3. **Environment Variables:**
   - Never commit `.env` files to Git
   - Always use Railway's environment variable system

4. **File Size Limits:**
   - Current limit: 5MB (reasonable for learning)
   - For production, consider cloud storage (S3, etc.)

---

## Next Steps

Once deployed, you can:

1. **Share the app** with friends/colleagues
2. **Monitor usage** in LangSmith dashboard
3. **Add features** (authentication, history, export, etc.)
4. **Optimize costs** by analyzing LangSmith traces
5. **Scale up** if you get more traffic (Railway scales automatically)

---

## Useful Railway Commands

### View Logs

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# View logs
railway logs
```

### Redeploy Manually

In the Railway dashboard:
1. Go to your service
2. Click "Deployments" tab
3. Click "..." on any deployment
4. Select "Redeploy"

---

## Support

If you encounter issues:

1. Check Railway build logs in the dashboard
2. Verify environment variables are set correctly
3. Test the backend health endpoint
4. Check LangSmith for API errors
5. Review this guide for common mistakes

Happy deploying! 🚀
