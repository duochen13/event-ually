# Deployment Guide

This guide will help you deploy the Task Manager application to production using Render (backend) and Vercel (frontend).

## Prerequisites

- GitHub account
- Render account (sign up at https://render.com)
- Vercel account (sign up at https://vercel.com)
- Your code pushed to GitHub

## Step 1: Deploy Backend to Render

### 1.1 Create New Web Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository: `duochen13/event-ually`

### 1.2 Configure Service

Fill in the following settings:

- **Name**: `task-manager-backend` (or your preferred name)
- **Region**: Choose closest to your location
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 1.3 Add Environment Variables

Click "Advanced" and add these environment variables:

- `PYTHON_VERSION` = `3.9.0`
- `SECRET_KEY` = (click "Generate" to create a random secret)
- `FRONTEND_URL` = (leave empty for now, will update after deploying frontend)

### 1.4 Deploy

1. Click "Create Web Service"
2. Wait for the deployment to complete (5-10 minutes)
3. Copy your backend URL (e.g., `https://task-manager-backend.onrender.com`)

**Important**: Free tier services may spin down after inactivity. First request may take 30-60 seconds.

## Step 2: Deploy Frontend to Vercel

### 2.1 Install Vercel CLI (Optional)

You can deploy via GitHub integration or CLI:

```bash
npm install -g vercel
```

### 2.2 Deploy via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository: `duochen13/event-ually`
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.3 Add Environment Variables

In "Environment Variables" section, add:

- **Name**: `VITE_API_URL`
- **Value**: `https://your-backend.onrender.com/api` (use your Render URL from Step 1.4)
- **Environment**: Production

### 2.4 Deploy

1. Click "Deploy"
2. Wait for deployment (2-3 minutes)
3. Copy your frontend URL (e.g., `https://task-manager-xyz.vercel.app`)

## Step 3: Update Backend CORS

1. Go back to Render dashboard
2. Open your backend service
3. Go to "Environment"
4. Add/Update the `FRONTEND_URL` environment variable:
   - **Key**: `FRONTEND_URL`
   - **Value**: Your Vercel URL (e.g., `https://task-manager-xyz.vercel.app`)
5. Click "Save Changes"
6. Service will automatically redeploy

## Step 4: Test Your Deployment

1. Visit your Vercel URL (frontend)
2. Try creating, updating, and deleting tasks
3. Verify data persists after refresh

### Troubleshooting

**CORS Errors:**
- Ensure `FRONTEND_URL` in Render matches your Vercel URL exactly (no trailing slash)
- Check Render logs for CORS-related errors

**API Connection Failed:**
- Verify `VITE_API_URL` in Vercel is correct
- Check Render service is running (free tier spins down after inactivity)
- Test backend health: `https://your-backend.onrender.com/api/health`

**Build Failures:**
- Check build logs in Render/Vercel dashboard
- Ensure all dependencies are in requirements.txt / package.json

## Deployment URLs

After successful deployment, save your URLs:

- **Backend**: `https://your-backend.onrender.com`
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-backend.onrender.com/api`

## Updating Your Deployment

### Update Backend:
```bash
git add backend/
git commit -m "Update backend"
git push origin main
```
Render will automatically redeploy.

### Update Frontend:
```bash
git add frontend/
git commit -m "Update frontend"
git push origin main
```
Vercel will automatically redeploy.

## Alternative: Deploy via CLI

### Vercel CLI:
```bash
cd frontend
vercel --prod
```

### Railway (Alternative to Render):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

## Cost

- **Render Free Tier**:
  - 750 hours/month
  - Service spins down after 15 min inactivity
  - 512 MB RAM

- **Vercel Free Tier**:
  - Unlimited deployments
  - 100 GB bandwidth/month
  - Automatic HTTPS

Both free tiers are sufficient for development and small projects!
