# Railway Deployment Guide

Complete guide for deploying InstaSplit to Railway.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository with your code
- Anthropic API key

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository has:
- ✅ Backend Dockerfile
- ✅ Frontend Dockerfile
- ✅ .gitignore
- ✅ No .env files committed (use .env.example)

### 2. Deploy Backend

1. **Create New Project**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your InstaSplit repository

2. **Configure Backend Service**
   - Railway will detect the backend Dockerfile
   - Set the root directory to `/backend`
   - Click "Deploy"

3. **Set Environment Variables**
   
   Go to Variables tab and add:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=instasplit-production
   ALLOW_VISION_FALLBACK=false
   ```

4. **Get Backend URL**
   - Railway will assign a public URL
   - Example: `https://instasplit-backend.up.railway.app`
   - Copy this URL for frontend configuration

### 3. Deploy Frontend

1. **Add New Service**
   - In the same project, click "New"
   - Select "GitHub Repo"
   - Choose the same repository

2. **Configure Frontend Service**
   - Set root directory to `/frontend`
   - Railway will detect the Dockerfile

3. **Set Environment Variables**
   ```
   BACKEND_URL=https://your-backend-url.up.railway.app
   ```
   (Use the backend URL from step 2.4)

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

5. **Get Frontend URL**
   - Railway assigns a public URL
   - Example: `https://instasplit.up.railway.app`
   - This is your app URL!

### 4. Verify Deployment

1. **Test Backend**
   ```bash
   curl https://your-backend-url.up.railway.app/health
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "ocr": "PaddleOCR",
     "llm": "configured"
   }
   ```

2. **Test Frontend**
   - Visit your frontend URL
   - Upload a sample receipt
   - Verify end-to-end flow

## Custom Domain (Optional)

### Add Custom Domain to Frontend

1. Go to frontend service settings
2. Click "Settings" → "Domains"
3. Add custom domain: `split.yourdomain.com`
4. Add CNAME record in your DNS:
   ```
   split.yourdomain.com → your-railway-url.up.railway.app
   ```

### Add Custom Domain to Backend

1. Go to backend service settings
2. Add domain: `api.split.yourdomain.com`
3. Update frontend `BACKEND_URL` to use new domain

## Monitoring & Logs

### View Logs

1. Click on service in Railway dashboard
2. Go to "Deployments"
3. Click on active deployment
4. View real-time logs

### Common Log Patterns

- OCR processing: `"OCR Method: PaddleOCR"`
- LLM calls: `"llm_used: true"`
- Errors: Look for traceback or ERROR level logs

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Request counts
- Deployment history

## Scaling

### Resource Allocation

Default Railway resources are usually sufficient for personal use (1-2 times/week).

To increase resources:
1. Go to service settings
2. Adjust memory/CPU limits
3. Note: Higher resources = higher cost

### Auto-scaling

Railway auto-scales based on load. No configuration needed.

## Cost Optimization

### Estimate Monthly Costs

**Railway Costs:**
- Hobby Plan: $5/month (includes $5 credit)
- Pro Plan: $20/month (includes $20 credit)
- Additional usage billed per resource

**Typical Resource Usage (personal use ~2x/week):**
- Backend: ~$2-5/month
- Frontend: ~$1-3/month
- Total: ~$3-8/month (well within Hobby plan)

**Anthropic API Costs:**
- OCR-first pipeline minimizes LLM calls
- Average: $0.001-0.01 per receipt
- ~$0.02-0.20/month for 2x/week usage

**Total Estimated Cost: $3-10/month**

### Reduce Costs

1. **Disable Vision Fallback**
   ```
   ALLOW_VISION_FALLBACK=false
   ```
   Vision models are expensive; use only if needed.

2. **Optimize Image Sizes**
   Already implemented! Images auto-resize to 1600px max.

3. **Use Aggressive OCR**
   The deterministic parser handles most cases without LLM.

4. **Sleep Inactive Services**
   Railway can sleep services after inactivity (Hobby plan).

## Troubleshooting

### "Service Failed to Start"

**Check:**
1. Build logs for errors
2. Environment variables are set correctly
3. Dockerfile paths are correct

**Fix:**
- Review Railway build logs
- Test Docker build locally first
- Ensure all dependencies in requirements.txt

### "Backend Connection Refused"

**Check:**
1. Backend service is running
2. `BACKEND_URL` is correct in frontend
3. No typos in URL

**Fix:**
- Verify backend health endpoint
- Check frontend environment variables
- Ensure both services in same project

### "OCR Not Working"

**Check:**
1. Tesseract installed in backend Docker
2. Memory allocation sufficient
3. Build logs for library errors

**Fix:**
- Review Dockerfile system dependencies
- Increase memory allocation
- Check PaddleOCR model downloads

### "High Costs"

**Check:**
1. Vision fallback enabled? (disable if unused)
2. LangChain tracing enabled? (optional overhead)
3. Excessive requests?

**Fix:**
- Set `ALLOW_VISION_FALLBACK=false`
- Disable tracing in production
- Review Railway metrics

## Updating Deployment

### Deploy New Changes

Railway auto-deploys on git push:

```bash
git add .
git commit -m "Update: description"
git push origin main
```

Railway will:
1. Detect changes
2. Rebuild affected services
3. Deploy automatically
4. Zero-downtime deployment

### Rollback

1. Go to "Deployments"
2. Find previous successful deployment
3. Click "Redeploy"

## Security Best Practices

### Environment Variables

- ✅ Never commit `.env` files
- ✅ Use Railway's encrypted variables
- ✅ Rotate API keys periodically
- ✅ Use separate keys for dev/prod

### API Security

- ✅ CORS configured in FastAPI
- ✅ Request size limits enforced (8MB)
- ✅ Input validation with Pydantic
- ✅ No authentication needed (personal use)

**For Production/Shared Use:**
- Add authentication (JWT, OAuth)
- Rate limiting
- Usage monitoring
- User quotas

## Backup & Recovery

### Backup Strategy

**What to Backup:**
- Code: Git repository (already backed up)
- Environment variables: Document in secure location
- No database, no persistent data needed

**Recovery:**
- Redeploy from Git
- Re-enter environment variables
- Takes ~5 minutes

### Disaster Recovery

If Railway has issues:
1. Export environment variables
2. Deploy to alternative (Render, Fly.io, etc.)
3. Update DNS if using custom domain
4. No data loss (stateless app)

## Support

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

**InstaSplit Issues:**
- Check logs first
- Review troubleshooting section
- Test locally with Docker Compose

---

**Happy Deploying! 🚀**
