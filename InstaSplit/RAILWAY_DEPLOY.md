# 🚀 Quick Railway Deployment Guide

## 📋 Pre-Deployment Checklist

✅ Code committed to GitHub  
✅ Railway.toml files added  
✅ Dockerfiles tested locally  
✅ Have Anthropic API key ready  

## 🎯 Deployment Steps

### 1. Push to GitHub

```bash
cd "/Users/vishalhp/AI Folder"
git push origin main
```

### 2. Deploy Backend

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository: `vishalpshetty/pdf-summarizer`
4. Railway will auto-detect services. Click on **backend** service
5. Set **Root Directory**: `InstaSplit/backend`
6. Add **Environment Variables**:
   ```
   ANTHROPIC_API_KEY=your_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key (optional)
   LANGCHAIN_PROJECT=instasplit-prod
   ALLOW_VISION_FALLBACK=false
   PORT=8000
   ```
7. Click **Deploy**
8. **Copy the backend URL** (e.g., `https://xxx.railway.app`)

### 3. Deploy Frontend

1. In the same project, click **"New"** → **"GitHub Repo"**
2. Select same repository
3. Click on **frontend** service
4. Set **Root Directory**: `InstaSplit/frontend`
5. Add **Environment Variables**:
   ```
   BACKEND_URL=https://your-backend-url.railway.app
   PORT=8501
   ```
   (Use the backend URL from step 2.8)
6. Click **Deploy**
7. **Copy the frontend URL** - this is your app!

### 4. Verify Deployment ✅

**Test Backend:**
```bash
curl https://your-backend.railway.app/health
```

**Test Frontend:**
Visit `https://your-frontend.railway.app` and upload a receipt!

## 🔧 Troubleshooting

### Backend Fails to Start
- Check logs for PaddleOCR model downloads (takes 2-3 mins first time)
- Verify ANTHROPIC_API_KEY is set correctly
- Ensure PORT environment variable is set

### Frontend Can't Connect to Backend
- Verify BACKEND_URL is set correctly (must be HTTPS Railway URL)
- Check backend is running and healthy
- Ensure no trailing slash in BACKEND_URL

### Out of Memory Errors
- PaddleOCR requires ~1GB RAM
- Upgrade Railway plan if needed
- Consider switching to Tesseract for lower memory usage

## 💰 Cost Estimate

Railway Free Tier:
- $5/month credits
- Should cover development/testing
- ~500 API calls/month (depending on usage)

For production:
- Backend: ~$10-20/month (includes compute + bandwidth)
- Frontend: ~$5/month
- Anthropic API: Pay per use (~$0.50 per 100 receipts)

## 🎉 Done!

Your InstaSplit app is now live! Share the frontend URL with your friends.

**Frontend URL**: `https://your-app.railway.app`

---

## 📚 Additional Resources

- [Full Deployment Guide](./DEPLOYMENT.md)
- [Railway Documentation](https://docs.railway.app)
- [Troubleshooting Guide](./DEVELOPMENT.md)
