# 🚀 AI Assistant Production Deployment Guide

## Prerequisites
✅ GitHub repo pushed: https://github.com/duochen13/event-ually
✅ Deployment configs ready: render.yaml, vercel.json
✅ Vercel CLI installed

---

## Part 1: Deploy Backend to Render (5 minutes)

### Step 1: Sign up/Login to Render
1. Go to https://dashboard.render.com/
2. Sign up with GitHub (recommended)

### Step 2: Create Web Service
1. Click **"New +"** → **"Blueprint"** (easiest option)
2. Connect your GitHub repository: **duochen13/event-ually**
3. Render will automatically detect `render.yaml`
4. Click **"Apply"**

### Step 3: Add Environment Variable
In Render Dashboard:
1. Go to your service → **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `your_actual_anthropic_api_key` (get from console.anthropic.com)
4. Click **"Save Changes"**
5. Service will automatically redeploy

### Step 4: Get Backend URL
After deployment completes (3-5 minutes):
- Your backend URL will be: `https://ai-assistant-backend-XXXX.onrender.com`
- **Copy this URL** - you'll need it for frontend deployment!
- Test it: Visit `https://your-backend-url.onrender.com/api/health`

---

## Part 2: Deploy Frontend to Vercel (3 minutes)

### Step 1: Login to Vercel CLI
Open terminal and run:
```bash
vercel login
```
Follow the prompts to authenticate with your email or GitHub.

### Step 2: Set Backend URL
Replace `YOUR_BACKEND_URL` with the actual URL from Part 1:
```bash
cd /Users/duochen/Desktop/spaghetti/playground/frontend
echo "VITE_API_URL=https://YOUR_BACKEND_URL.onrender.com/api" > .env.production
```

Example:
```bash
echo "VITE_API_URL=https://ai-assistant-backend-abc123.onrender.com/api" > .env.production
```

### Step 3: Deploy to Vercel
```bash
cd /Users/duochen/Desktop/spaghetti/playground
vercel --prod
```

Follow the prompts:
- **Setup and deploy?** → Yes
- **Which scope?** → (Select your account)
- **Link to existing project?** → No
- **Project name?** → ai-assistant (or your choice)
- **In which directory is your code located?** → ./
- **Want to override settings?** → No

### Step 4: Get Frontend URL
After deployment completes:
- Your frontend URL: `https://ai-assistant-XXXX.vercel.app`
- **This is your PUBLIC URL!** 🎉
- Share this with anyone!

---

## Part 3: Update Backend CORS (Important!)

After getting your Vercel URL, you must update the backend:

1. Go to **Render Dashboard** → Your service → **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add:
   - Key: `FRONTEND_URL`
   - Value: `https://your-frontend-url.vercel.app` (your actual Vercel URL)
4. Click **"Save Changes"**
5. Service will redeploy automatically

This allows your frontend to communicate with the backend.

---

## 🧪 Testing Your Production Deployment

1. Visit your Vercel URL: `https://ai-assistant-XXXX.vercel.app`
2. Click **"Start New Conversation"**
3. Send a test message: "Hello! Are you working?"
4. Verify Claude responds correctly
5. Test conversation management (create, switch, delete)

---

## 📊 Monitoring & Logs

### Render (Backend)
- **Dashboard**: https://dashboard.render.com/
- **Logs**: Click your service → "Logs" tab
- **Metrics**: Click your service → "Metrics" tab

### Vercel (Frontend)
- **Dashboard**: https://vercel.com/dashboard
- **Deployments**: See all deployments and their status
- **Analytics**: View usage statistics

---

## 🔧 Quick Commands Reference

```bash
# Login to Vercel
vercel login

# Deploy frontend to production
cd /Users/duochen/Desktop/spaghetti/playground
vercel --prod

# Check Vercel deployment status
vercel ls

# View Vercel logs
vercel logs

# Redeploy frontend (after code changes)
git push origin main  # Push changes
vercel --prod         # Redeploy
```

---

## 🚨 Troubleshooting

### Backend Issues

**"Service Unavailable" or 500 errors:**
- Check Render logs for Python errors
- Verify `ANTHROPIC_API_KEY` is set correctly
- Ensure service is running (check Render dashboard)

**Database errors:**
- Check if SQLite database initialized
- View Render logs for "unable to open database" errors

### Frontend Issues

**"Failed to fetch" or CORS errors:**
- Verify `VITE_API_URL` in `.env.production` is correct
- Update `FRONTEND_URL` in Render environment variables
- Ensure backend is running

**Build failures on Vercel:**
- Check build logs in Vercel dashboard
- Verify all npm dependencies installed
- Check for TypeScript/linting errors

**Blank page or 404 errors:**
- Check browser console for errors
- Verify Vercel deployment succeeded
- Check if routes are configured in `vercel.json`

### API Key Issues

**"Authentication error" from Claude:**
- Verify `ANTHROPIC_API_KEY` is correct in Render
- Check API key has credits (console.anthropic.com)
- Ensure no extra spaces in the environment variable

---

## 💰 Cost Estimate

### Free Tier
- **Render Free**:
  - 750 hours/month (enough for 1 service)
  - Sleeps after 15 min of inactivity (wakes in ~30s)
  - Perfect for demos and development

- **Vercel Free**:
  - Unlimited deployments
  - 100GB bandwidth/month
  - Perfect for personal projects

### Paid Options
- **Render**: $7/month for always-on service
- **Vercel**: $20/month for Pro features
- **Anthropic API**: Pay-as-you-go (~$3-15 per million tokens)

---

## 🎯 Next Steps After Deployment

1. **Custom Domain** (Optional):
   - Add custom domain in Vercel dashboard
   - Update DNS settings
   - Enable automatic HTTPS

2. **Add Features**:
   - User authentication
   - Conversation sharing
   - File uploads
   - Voice input

3. **Analytics**:
   - Add Google Analytics
   - Monitor API usage in Anthropic console
   - Track errors with Sentry

4. **Optimization**:
   - Enable caching
   - Add rate limiting
   - Optimize database queries

---

## 📚 Useful Links

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Anthropic Console**: https://console.anthropic.com/
- **Your GitHub Repo**: https://github.com/duochen13/event-ually

---

## ✅ Deployment Checklist

- [ ] Backend deployed to Render
- [ ] `ANTHROPIC_API_KEY` added to Render
- [ ] Backend health check passes
- [ ] Frontend deployed to Vercel
- [ ] `VITE_API_URL` set in frontend
- [ ] `FRONTEND_URL` added to Render
- [ ] Test conversation creation
- [ ] Test AI responses
- [ ] Share public URL!

---

**Questions or issues?** Check the troubleshooting section above or review the Render/Vercel logs for detailed error messages.

**Ready to deploy?** Start with Part 1 above! 🚀
