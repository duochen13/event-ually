# Deployment Guide

This guide will walk you through deploying the Task Manager application to Render (backend) and Vercel (frontend).

## Prerequisites

- GitHub account with your repository pushed
- Render account (sign up at https://render.com)
- Vercel account (sign up at https://vercel.com)

## Step 1: Deploy Backend to Render

### 1.1 Connect GitHub Repository

1. Go to https://dashboard.render.com
2. Click "New +" and select "Web Service"
3. Connect your GitHub account if not already connected
4. Select your repository (`event-ually`)

### 1.2 Configure Service

Render will automatically detect the `render.yaml` configuration file. Verify these settings:

- **Name**: `task-manager-backend`
- **Environment**: `Python`
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && gunicorn app:app`
- **Plan**: Free (or your preference)

### 1.3 Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete (3-5 minutes)
3. Copy your backend URL (format: `https://task-manager-backend-xxxx.onrender.com`)

### 1.4 Test Backend

Once deployed, test the health endpoint:
```bash
curl https://your-backend-url.onrender.com/api/health
```

You should receive: `{"message": "API is healthy!", "status": "ok"}`

## Step 2: Deploy Frontend to Vercel

### 2.1 Configure Environment Variable

Before deploying, you need to set the backend URL:

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. **IMPORTANT**: Before deploying, add environment variable:
   - Key: `VITE_API_URL`
   - Value: `https://your-backend-url.onrender.com/api` (use your actual Render URL)

### 2.2 Configure Build Settings

Vercel will automatically detect the `vercel.json` configuration. Verify:

- **Framework Preset**: Vite
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/dist`

### 2.3 Deploy

1. Click "Deploy"
2. Wait for deployment to complete (2-3 minutes)
3. Your frontend will be available at: `https://your-project.vercel.app`

## Step 3: Verify Deployment

1. Visit your Vercel URL
2. Try creating, updating, and deleting tasks
3. Refresh the page - data should persist

## Configuration Files Created

- `render.yaml` - Backend deployment config for Render
- `vercel.json` - Frontend deployment config for Vercel

## Troubleshooting

### Frontend can't connect to backend
- Verify `VITE_API_URL` environment variable in Vercel settings
- Check backend is running on Render
- Verify CORS settings allow your Vercel domain

### Database resets on Render
- Free tier services restart periodically
- Consider upgrading to persistent disk or using PostgreSQL

## Automatic Deployments

Both platforms support automatic deployments:
- **Render**: Auto-deploys on push to main branch
- **Vercel**: Auto-deploys on every git push

## Next Steps

1. Test all functionality
2. Configure custom domains (optional)
3. Set up monitoring and alerts
4. Implement production database (PostgreSQL recommended)

For detailed instructions, see: https://render.com/docs and https://vercel.com/docs
